---
name: validate
command: /superjeff:validate
description: Run the full 4-domain audit across all built apps — architecture, security, UX compliance, and test coverage. Acts as an independent peer review gate.
input: Optional app name; if omitted, validates all apps in artifacts/code/
output: artifacts/reports/validation_summary.json
---

## Purpose

An independent peer review gate. Runs four specialist audits in sequence and produces a consolidated report. This is the "lead developer review" before a merge — it checks the work against every standard defined in the system, without assuming the implementer got it right.

The four audits map to four independent perspectives:

| Audit | Agent | Perspective |
| --- | --- | --- |
| Architecture | Quality Agent (Gate 1–5) | "Does the code follow the rules?" |
| Security | Security Agent (OWASP Top 10) | "Can this be attacked?" |
| UX Compliance | UX Compliance Agent | "Does the UI match the design?" |
| Test Coverage | Quality Agent (Gate 2) | "Is the test suite trustworthy?" |

Each audit is independent and can be run standalone (see below).

---

## Usage

**Full audit — all domains, all apps:**
```
/superjeff:validate
```

**Full audit — single app:**
```
/superjeff:validate <app_name>
```

**Single domain only:**
```
/superjeff:validate <app_name> --domain architecture
/superjeff:validate <app_name> --domain security
/superjeff:validate <app_name> --domain ux
/superjeff:validate <app_name> --domain tests
```

---

## What Happens

```
For each app:

1. Architecture Audit      [Quality Agent — Gates 1, 3, 4, 5]
   Checks: service layer, FBV-only, dumb models, serializers,
           exceptions, caching, Celery, migrations, API accessibility
   Output: artifacts/reports/<app>_quality.json
   Blocks on: critical or high findings

2. Security Audit          [Security Agent — OWASP Top 10]
   Checks: access control, injection, auth, secrets, config,
           logging, SSRF, software integrity
   Output: artifacts/reports/<app>_security.json
   Blocks on: any critical finding, 2+ high findings

3. UX Compliance Audit     [UX Compliance Agent]
   Checks: design tokens applied, all pages implemented,
           component states (loading/empty/error/populated),
           HTMX indicators, aria-live regions, form labels,
           HTMX patterns match spec, accessibility baseline
   Requires: artifacts/ux/<app>_ux_spec.json
   Output: artifacts/reports/<app>_ux_compliance.json
   Blocks on: critical or 2+ high findings
   Skips: if no UX spec exists (backend-only app)

4. Test Coverage Audit     [Quality Agent — Gate 2]
   Checks: test files exist, pytest used, factory_boy used,
           5 test cases per endpoint (success/401/403/400/404),
           isolation, APIClient, no objects.create in tests
   Output: included in artifacts/reports/<app>_quality.json
   Blocks on: missing test files, critical coverage gaps

5. Aggregate report
   Output: artifacts/reports/validation_summary.json
   Print: findings table sorted by severity × domain
```

---

## When to Run

| Situation | When to validate |
| --- | --- |
| After `/superjeff:build <app>` | Always — built into build_pipeline.yaml final stage |
| Before merging a feature branch | Always — run standalone `/superjeff:validate <app>` |
| After a refactor | Always — confirm nothing regressed |
| After `/superjeff:conform <app>` | Automatically triggered at the end |
| After `/superjeff:conform-ui <app>` | Automatically triggered (UX domain only) |
| Periodic audit of production code | Run without `<app>` to audit all apps |

---

## Output Format

```json
{
  "timestamp": "ISO8601",
  "apps_validated": ["string"],
  "overall_status": "passed|failed",
  "domains": {
    "architecture": "passed|failed|skipped",
    "security": "passed|failed|skipped",
    "ux_compliance": "passed|failed|skipped",
    "test_coverage": "passed|failed|skipped"
  },
  "findings_by_app": {
    "<app_name>": {
      "architecture": { "critical": 0, "high": 0, "medium": 0, "low": 0 },
      "security": { "critical": 0, "high": 0, "medium": 0, "low": 0 },
      "ux_compliance": { "critical": 0, "high": 0, "medium": 0, "low": 0, "spec_coverage_percent": 100 },
      "test_coverage": { "critical": 0, "high": 0, "medium": 0, "low": 0 }
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

`overall_status: passed` requires **all** of:

- Zero `critical` findings in any domain
- Zero `high` security findings
- Zero `critical` or `high` architecture findings
- All test files present and tests passing
- UX spec coverage ≥ 95% (if UX spec exists)

## Failure Modes

| Error | Cause | Resolution |
| --- | --- | --- |
| `critical_architecture_finding` | CBV, direct ORM in view, no service layer | Fix per remediation in quality report |
| `critical_security_finding` | OWASP violation | Fix per remediation in security report |
| `critical_ux_finding` | Missing hx-indicator, form without label, missing page | Fix template per UX spec finding |
| `missing_test_files` | No test_models.py / test_api.py etc. | Write tests before re-running |
| `ux_spec_missing` | UX audit skipped | Run `/superjeff:design <app>` first if UI exists |
| `no_code_artifacts` | Nothing to audit | Run `/superjeff:build <app>` first |
