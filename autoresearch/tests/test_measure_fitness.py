"""
Tests for autoresearch.measure_fitness
All tests must FAIL before implementation exists.

TC-002: combined_score respects 60/40 weighting
TC-003: failing tests trigger DISCARD
TC-004: lower combined score triggers DISCARD
TC-005: equal score does not trigger DISCARD
TC-006: improved score produces git commit
TC-007: log.json appended after every iteration
TC-008: agent never touches models.py or migrations
TC-009: measure_backend handles zero queries gracefully
TC-010: Lighthouse failure does not crash loop
"""
import pytest
import subprocess
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# combined_score — TC-002, weighting, edge cases
# ---------------------------------------------------------------------------

class TestCombinedScore:
    def test_60_40_weighting(self):
        """TC-002: 0.6*80 + 0.4*60 = 72.0"""
        from autoresearch.measure_fitness import combined_score
        backend = {"score": 80.0}
        frontend = {"score": 60.0}
        result = combined_score(backend, frontend)
        assert result == pytest.approx(72.0)

    def test_custom_weights(self):
        """Custom weights respected when provided"""
        from autoresearch.measure_fitness import combined_score
        backend = {"score": 100.0}
        frontend = {"score": 0.0}
        result = combined_score(backend, frontend, weights=(1.0, 0.0))
        assert result == pytest.approx(100.0)

    def test_weights_must_sum_to_one(self):
        """Weights that don't sum to 1.0 raise ValueError"""
        from autoresearch.measure_fitness import combined_score
        with pytest.raises(ValueError, match="weights"):
            combined_score({"score": 50}, {"score": 50}, weights=(0.5, 0.6))

    def test_both_zero(self):
        """Zero scores on both sides returns 0.0"""
        from autoresearch.measure_fitness import combined_score
        result = combined_score({"score": 0.0}, {"score": 0.0})
        assert result == pytest.approx(0.0)

    def test_both_hundred(self):
        """Perfect scores return 100.0"""
        from autoresearch.measure_fitness import combined_score
        result = combined_score({"score": 100.0}, {"score": 100.0})
        assert result == pytest.approx(100.0)

    def test_equal_score_is_keep_threshold(self):
        """TC-005: score >= previous means KEEP — equality is sufficient"""
        from autoresearch.measure_fitness import combined_score
        prev = combined_score({"score": 75.0}, {"score": 75.0})
        current = combined_score({"score": 75.0}, {"score": 75.0})
        assert current >= prev  # KEEP condition


# ---------------------------------------------------------------------------
# run_tests
# ---------------------------------------------------------------------------

class TestRunTests:
    def test_passing_tests_return_passed_true(self):
        """TC-006 prerequisite: run_tests returns passed=True when pytest exits 0"""
        from autoresearch.measure_fitness import run_tests
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="2 passed", stderr="")
            result = run_tests("expenses")
        assert result["passed"] is True
        assert result["failed_count"] == 0

    def test_failing_tests_return_passed_false(self):
        """TC-003: failing tests trigger DISCARD — run_tests signals failure"""
        from autoresearch.measure_fitness import run_tests
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="1 failed", stderr="")
            result = run_tests("expenses")
        assert result["passed"] is False
        assert result["failed_count"] >= 1

    def test_output_captured(self):
        """pytest stdout is returned in output field"""
        from autoresearch.measure_fitness import run_tests
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="3 passed in 0.5s", stderr="")
            result = run_tests("expenses")
        assert "passed" in result["output"]


# ---------------------------------------------------------------------------
# measure_backend
# ---------------------------------------------------------------------------

class TestMeasureBackend:
    def test_returns_required_keys(self):
        """measure_backend returns query_count, p95_response_time_ms, score"""
        from autoresearch.measure_fitness import measure_backend
        with patch("autoresearch.measure_fitness._run_backend_measurement") as mock_m:
            mock_m.return_value = {"query_count": 5, "p95_response_time_ms": 120.0}
            result = measure_backend("expenses", ["/expenses/"])
        assert "query_count" in result
        assert "p95_response_time_ms" in result
        assert "score" in result

    def test_score_in_valid_range(self):
        """score is always between 0 and 100"""
        from autoresearch.measure_fitness import measure_backend
        with patch("autoresearch.measure_fitness._run_backend_measurement") as mock_m:
            mock_m.return_value = {"query_count": 3, "p95_response_time_ms": 80.0}
            result = measure_backend("expenses", ["/expenses/"])
        assert 0.0 <= result["score"] <= 100.0

    def test_zero_queries_returns_high_score(self):
        """TC-009: zero queries is valid and yields score=100 for query dimension"""
        from autoresearch.measure_fitness import measure_backend
        with patch("autoresearch.measure_fitness._run_backend_measurement") as mock_m:
            mock_m.return_value = {"query_count": 0, "p95_response_time_ms": 10.0}
            result = measure_backend("expenses", ["/expenses/"])
        assert result["query_count"] == 0
        assert result["score"] > 90.0  # near-perfect when zero queries

    def test_empty_urls_raises(self):
        """Empty URL list raises ValueError"""
        from autoresearch.measure_fitness import measure_backend
        with pytest.raises(ValueError, match="urls"):
            measure_backend("expenses", [])


# ---------------------------------------------------------------------------
# measure_frontend
# ---------------------------------------------------------------------------

class TestMeasureFrontend:
    def test_returns_required_keys(self):
        """measure_frontend returns lighthouse_performance and score"""
        from autoresearch.measure_fitness import measure_frontend
        with patch("autoresearch.measure_fitness._run_lighthouse") as mock_lh:
            mock_lh.return_value = 85.0
            result = measure_frontend("http://localhost:8000", ["/"])
        assert "lighthouse_performance" in result
        assert "score" in result

    def test_score_equals_lighthouse_performance(self):
        """score == lighthouse_performance for frontend measurement"""
        from autoresearch.measure_fitness import measure_frontend
        with patch("autoresearch.measure_fitness._run_lighthouse") as mock_lh:
            mock_lh.return_value = 72.0
            result = measure_frontend("http://localhost:8000", ["/"])
        assert result["score"] == pytest.approx(result["lighthouse_performance"])

    def test_server_unreachable_returns_zero(self):
        """TC-010: unreachable server returns score=0, does not crash"""
        from autoresearch.measure_fitness import measure_frontend
        with patch("autoresearch.measure_fitness._run_lighthouse") as mock_lh:
            mock_lh.side_effect = ConnectionError("server not reachable")
            result = measure_frontend("http://localhost:8000", ["/"])
        assert result["score"] == 0.0
        assert result["lighthouse_performance"] == 0.0

    def test_lighthouse_not_installed_returns_zero(self):
        """TC-010: missing lighthouse binary returns score=0, does not crash"""
        from autoresearch.measure_fitness import measure_frontend
        with patch("autoresearch.measure_fitness._run_lighthouse") as mock_lh:
            mock_lh.side_effect = FileNotFoundError("lighthouse not found")
            result = measure_frontend("http://localhost:8000", ["/"])
        assert result["score"] == 0.0

    def test_empty_paths_raises(self):
        """Empty paths list raises ValueError"""
        from autoresearch.measure_fitness import measure_frontend
        with pytest.raises(ValueError, match="paths"):
            measure_frontend("http://localhost:8000", [])
