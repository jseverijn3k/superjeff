---
name: build
command: /superjeff:build
description: Execute the full TDD build pipeline for a specified Django app
input: App name (must have a requirements artifact)
output: artifacts/code/<app_name>/ — production-ready Django app code
workflow: workflows/build_pipeline.yaml
---

## Purpose

Runs the full TDD build pipeline: plan → write failing tests → implement → refactor → security review → validate.

## Usage

```
/superjeff:build <app_name>
```

Example:
```
/superjeff:build expenses
```

## Pipeline Stages

```
Plan          → Task breakdown ordered by dependency
  ↓
Write Tests   → Failing tests from requirements (RED)
  ↓
Implement     → Django code that makes tests pass (GREEN)
  ↓
Refactor      → Quality Agent review (REFACTOR)
  ↓
Security      → Security Agent OWASP audit
  ↓
Validate      → All gates must pass
```

## Prerequisites

- `artifacts/requirements/<app_name>.json` must exist
- Run `/superjeff:specify <app_name>` first

## Output Location

```
artifacts/
  plans/
    <app_name>_plan.json
  tests/
    <app_name>/
      test_models.py
      test_views.py
      test_serializers.py
  code/
    <app_name>/
      models.py
      serializers.py
      views.py
      urls.py
      permissions.py
      signals.py
      migrations/
      admin.py
  reports/
    <app_name>_quality.json
    <app_name>_security.json
```

## Quality Gates

The pipeline will HALT if:
- Any test fails after implementation
- Quality Agent finds a `critical` or `high` severity finding
- Security Agent finds a `critical` severity finding or 2+ `high` findings
- Migrations are missing for model changes

## Next Step

Run `/superjeff:validate` to run all checks across the full project.

## Failure Modes

| Error | Cause | Resolution |
|---|---|---|
| `tests_not_failing_before_impl` | Test already passes = wrong test | Fix the test to actually test something |
| `tests_failing_after_impl` | Implementation is wrong | Review the failing test output |
| `quality_gate_blocked` | High/critical quality finding | Fix finding then re-run |
| `security_gate_blocked` | Critical security finding | Fix finding then re-run |
| `missing_migrations` | Model defined without migration | Run makemigrations |
