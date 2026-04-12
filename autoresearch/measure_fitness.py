"""
autoresearch.measure_fitness
Fitness measurement utilities for the autoresearch loop.

Measures backend performance (query count + response time) and
frontend performance (Lighthouse score), combines them into a
single fitness score for keep/discard decisions.
"""
from __future__ import annotations

import json
import subprocess
import statistics
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def combined_score(
    backend: dict[str, Any],
    frontend: dict[str, Any],
    weights: tuple[float, float] = (0.6, 0.4),
) -> float:
    """
    Combine backend and frontend scores into a single fitness value.

    Args:
        backend:  dict with 'score' key (0-100), from measure_backend()
        frontend: dict with 'score' key (0-100), from measure_frontend()
        weights:  (backend_weight, frontend_weight) — must sum to 1.0

    Returns:
        float in [0, 100]

    Raises:
        ValueError: if weights do not sum to 1.0
    """
    if abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1.0, got {sum(weights)}")
    return weights[0] * backend["score"] + weights[1] * frontend["score"]


def run_tests(app_name: str) -> dict[str, Any]:
    """
    Run the pytest suite and return pass/fail result.

    Args:
        app_name: Django app label (used to scope pytest path if needed)

    Returns:
        dict with keys: passed (bool), failed_count (int), output (str)
    """
    result = subprocess.run(
        ["python3", "-m", "pytest", "--tb=short", "-q"],
        capture_output=True,
        text=True,
    )
    passed = result.returncode == 0
    output = result.stdout + result.stderr

    failed_count = 0
    for line in output.splitlines():
        if "failed" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "failed" and i > 0:
                    try:
                        failed_count = int(parts[i - 1])
                    except ValueError:
                        failed_count = 1
                    break

    return {
        "passed": passed,
        "failed_count": failed_count,
        "output": output,
    }


def measure_backend(
    app_name: str,
    urls: list[str],
) -> dict[str, Any]:
    """
    Measure backend performance: query count and response time.

    Args:
        app_name: Django app label
        urls:     list of URL paths to test (must be non-empty)

    Returns:
        dict with keys: query_count (int), p95_response_time_ms (float), score (float 0-100)

    Raises:
        ValueError: if urls is empty
    """
    if not urls:
        raise ValueError("urls must be a non-empty list")

    measurement = _run_backend_measurement(app_name, urls)
    query_count = measurement["query_count"]
    p95 = measurement["p95_response_time_ms"]

    score = _backend_score(query_count, p95)

    return {
        "query_count": query_count,
        "p95_response_time_ms": p95,
        "score": score,
    }


def measure_frontend(
    base_url: str,
    paths: list[str],
) -> dict[str, Any]:
    """
    Measure frontend performance via Lighthouse.

    Args:
        base_url: running server base URL, e.g. 'http://localhost:8000'
        paths:    URL paths to audit (must be non-empty)

    Returns:
        dict with keys: lighthouse_performance (float), score (float 0-100)
        On server/Lighthouse failure: returns score=0 without raising.

    Raises:
        ValueError: if paths is empty
    """
    if not paths:
        raise ValueError("paths must be a non-empty list")

    scores: list[float] = []
    for path in paths:
        try:
            lh_score = _run_lighthouse(base_url + path)
            scores.append(lh_score)
        except (ConnectionError, FileNotFoundError, OSError):
            scores.append(0.0)

    avg = statistics.mean(scores) if scores else 0.0

    return {
        "lighthouse_performance": avg,
        "score": avg,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_backend_measurement(app_name: str, urls: list[str]) -> dict[str, Any]:
    """
    Internal: measure query count and response times using Django test client.
    Imported and patched in tests.
    In production: sets up Django, uses test client + connection.queries.
    """
    import os
    import django
    import time

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{app_name}.settings")
    django.setup()

    from django.test import Client
    from django.db import connection, reset_queries

    settings = django.conf.settings
    settings.DEBUG = True

    client = Client()
    response_times: list[float] = []
    total_queries = 0

    for url in urls:
        for _ in range(10):
            reset_queries()
            start = time.perf_counter()
            client.get(url)
            elapsed_ms = (time.perf_counter() - start) * 1000
            response_times.append(elapsed_ms)
            total_queries += len(connection.queries)

    p95 = _percentile(response_times, 95)
    avg_queries = total_queries // (len(urls) * 10)

    return {
        "query_count": avg_queries,
        "p95_response_time_ms": p95,
    }


def _run_lighthouse(url: str) -> float:
    """
    Internal: invoke Lighthouse CLI and parse performance score.
    Raises ConnectionError or FileNotFoundError on failure (caller handles).
    """
    result = subprocess.run(
        [
            "lighthouse",
            url,
            "--output=json",
            "--output-path=stdout",
            "--only-categories=performance",
            "--chrome-flags=--headless",
            "--quiet",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise ConnectionError(f"Lighthouse failed: {result.stderr[:200]}")

    data = json.loads(result.stdout)
    score = data["categories"]["performance"]["score"]
    return float(score) * 100


def _backend_score(query_count: int, p95_ms: float) -> float:
    """
    Convert query count and p95 response time to a 0-100 score.
    Lower queries and faster responses = higher score.

    Scoring:
      - query_count=0 → 100 points for query dimension
      - query_count scaling: 100 / (1 + query_count * 0.5), capped at 100
      - p95 scaling: 100 / (1 + p95_ms / 100), capped at 100
      - final = average of both dimensions
    """
    if query_count == 0:
        query_score = 100.0
    else:
        query_score = min(100.0, 100.0 / (1 + query_count * 0.5))

    time_score = min(100.0, 100.0 / (1 + p95_ms / 100))

    return (query_score + time_score) / 2


def _percentile(data: list[float], pct: int) -> float:
    """Return the Nth percentile of a list of floats."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * pct / 100)
    index = min(index, len(sorted_data) - 1)
    return sorted_data[index]
