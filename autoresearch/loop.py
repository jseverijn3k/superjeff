"""
autoresearch.loop
Iteration orchestrator for the autoresearch loop.

Reads program.md, runs one experiment iteration, measures fitness,
and commits or discards based on safety gates.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from autoresearch.measure_fitness import (
    combined_score,
    measure_backend,
    measure_frontend,
    run_tests,
)


def load_program(app_name: str) -> dict[str, Any]:
    """Load and parse program.md for the given app."""
    program_path = Path(f"artifacts/autoresearch/{app_name}/program.md")
    if not program_path.exists():
        raise FileNotFoundError(
            f"No program.md found at {program_path}. "
            f"Copy templates/autoresearch.md and fill it in first."
        )
    text = program_path.read_text()
    config: dict[str, Any] = {"raw": text, "app_name": app_name}

    for line in text.splitlines():
        if line.startswith("app_name:"):
            config["app_name"] = line.split(":", 1)[1].strip()
        elif line.startswith("base_url:"):
            config["base_url"] = line.split(":", 1)[1].strip()
        elif line.startswith("urls:"):
            pass

    urls: list[str] = []
    in_urls = False
    for line in text.splitlines():
        if line.strip() == "urls:":
            in_urls = True
            continue
        if in_urls:
            stripped = line.strip()
            if stripped.startswith("- "):
                urls.append(stripped[2:])
            elif stripped and not stripped.startswith("#"):
                in_urls = False

    config["urls"] = urls or ["/"]
    config.setdefault("base_url", "http://localhost:8000")
    return config


def load_log(app_name: str) -> list[dict[str, Any]]:
    """Load existing iteration log or return empty list."""
    log_path = Path(f"artifacts/autoresearch/{app_name}/log.json")
    if not log_path.exists():
        return []
    return json.loads(log_path.read_text())


def save_log(app_name: str, entries: list[dict[str, Any]]) -> None:
    """Write iteration log to disk."""
    log_path = Path(f"artifacts/autoresearch/{app_name}/log.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(entries, indent=2))


def git_checkout_all() -> None:
    """Discard uncommitted changes — DISCARD path."""
    subprocess.run(["git", "checkout", "--", "."], check=True, capture_output=True)


def git_commit(app_name: str, iteration: int, score: float) -> str:
    """Commit current changes and return the SHA."""
    msg = f"autoresearch({app_name}): iteration {iteration} — score {score:.2f}"
    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], check=True, capture_output=True)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return sha


def run_iteration(
    app_name: str,
    hypothesis: str,
    diff_summary: str,
    previous_score: float,
) -> dict[str, Any]:
    """
    Execute one autoresearch iteration.

    The agent has already applied its proposed change before calling this.
    This function measures, decides, and commits or discards.

    Args:
        app_name:       Django app label
        hypothesis:     What the agent changed and why
        diff_summary:   Files changed (short description)
        previous_score: Combined score from previous iteration (0-100)

    Returns:
        Iteration log entry dict
    """
    log = load_log(app_name)
    iteration_number = len(log) + 1

    program = load_program(app_name)
    urls = program["urls"]
    base_url = program["base_url"]

    test_result = run_tests(app_name)
    if not test_result["passed"]:
        git_checkout_all()
        entry = _make_entry(
            iteration=iteration_number,
            hypothesis=hypothesis,
            diff_summary=diff_summary,
            backend_score=0.0,
            frontend_score=0.0,
            combined=0.0,
            tests_passed=False,
            decision="DISCARD",
            git_commit_sha=None,
        )
        log.append(entry)
        save_log(app_name, log)
        return entry

    backend = measure_backend(app_name, urls)
    frontend = measure_frontend(base_url, [u for u in urls])
    score = combined_score(backend, frontend)

    if score < previous_score:
        git_checkout_all()
        entry = _make_entry(
            iteration=iteration_number,
            hypothesis=hypothesis,
            diff_summary=diff_summary,
            backend_score=backend["score"],
            frontend_score=frontend["score"],
            combined=score,
            tests_passed=True,
            decision="DISCARD",
            git_commit_sha=None,
        )
        log.append(entry)
        save_log(app_name, log)
        return entry

    sha = git_commit(app_name, iteration_number, score)
    entry = _make_entry(
        iteration=iteration_number,
        hypothesis=hypothesis,
        diff_summary=diff_summary,
        backend_score=backend["score"],
        frontend_score=frontend["score"],
        combined=score,
        tests_passed=True,
        decision="KEEP",
        git_commit_sha=sha,
    )
    log.append(entry)
    save_log(app_name, log)
    return entry


def _make_entry(
    iteration: int,
    hypothesis: str,
    diff_summary: str,
    backend_score: float,
    frontend_score: float,
    combined: float,
    tests_passed: bool,
    decision: str,
    git_commit_sha: str | None,
) -> dict[str, Any]:
    return {
        "iteration": iteration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypothesis": hypothesis,
        "diff_summary": diff_summary,
        "backend_score": round(backend_score, 2),
        "frontend_score": round(frontend_score, 2),
        "combined_score": round(combined, 2),
        "tests_passed": tests_passed,
        "decision": decision,
        "git_commit": git_commit_sha,
    }
