---
name: validate
command: /superjeff:validate
description: Run the full validation suite across all built apps — quality, security, and test coverage
input: Optional app name; if omitted, validates all apps in artifacts/code/
output: artifacts/reports/validation_summary.json
workflow: workflows/build_pipeline.yaml (validate stage)
---

## Purpose

Runs the Quality Agent and Security Agent across all generated code. Produces a consolidated validation report suitable for a pre-merge gate.

## Usage

Validate all apps:
```
/superjeff:validate
```

Validate a single app:
```
/superjeff:validate <app_name>
```

## What Happens

1. For each app in `artifacts/code/`:
   - Run Quality Agent → `artifacts/reports/<app_name>_quality.json`
   - Run Security Agent → `artifacts/reports/<app_name>_security.json`
2. Aggregate all findings into `artifacts/reports/validation_summary.json`
3. Print a findings table sorted by severity

## Output Format

```json
{
  "timestamp": "ISO8601",
  "apps_validated": ["string"],
  "overall_status": "passed|failed",
  "gates": {
    "all_tests_pass": true,
    "no_critical_findings": true,
    "migrations_present": true,
    "no_security_blockers": true
  },
  "findings_by_app": {
    "<app_name>": {
      "quality": { "critical": 0, "high": 0, "medium": 0, "low": 0 },
      "security": { "critical": 0, "high": 0, "medium": 0, "low": 0 }
    }
  },
  "total_findings": {
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }
}
```

## Pass Criteria

- `overall_status: passed` requires:
  - Zero `critical` findings across all apps
  - Zero `high` security findings across all apps
  - All tests pass
  - All migrations present

## Failure Modes

| Error | Cause | Resolution |
|---|---|---|
| `no_code_artifacts` | No apps in artifacts/code/ | Run /superjeff:build first |
| `critical_security_finding` | OWASP violation found | Fix finding per remediation instructions |
| `critical_quality_finding` | Test coverage or convention gap | Fix finding per remediation instructions |
| `test_suite_failed` | Tests not passing | Investigate failing test output |
