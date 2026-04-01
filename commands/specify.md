---
name: specify
command: /superjeff:specify
description: Generate complete implementation-ready requirements for a single Django app
input: App name (must exist in artifacts/decomposition.json)
output: artifacts/requirements/<app_name>.json + artifacts/contracts/<app_name>_contract.json
workflow: workflows/app_to_requirements.yaml
---

## Purpose

Runs the Requirements Agent on a single app definition and produces a fully-specified, implementation-ready requirements document plus an API contract.

## Usage

```
/superjeff:specify <app_name>
```

Example:
```
/superjeff:specify expenses
```

## What Happens

1. The Orchestrator loads `artifacts/decomposition.json`
2. It extracts the app definition for `<app_name>`
3. The Requirements Agent receives the app definition
4. The agent produces a full specification:
   - Models with typed fields
   - Serializers with validation rules
   - Views with permission classes
   - Business rules with enforcement layer
   - Test cases (happy path + edge cases + failure paths)
5. Output validated against `schemas/requirements_schema.json`
6. API contract generated and saved to `artifacts/contracts/`

## Prerequisites

- `artifacts/decomposition.json` must exist (run `/superjeff:decompose` first)
- `<app_name>` must be one of the apps in the decomposition

## Output Location

```
artifacts/
  requirements/
    <app_name>.json
  contracts/
    <app_name>_contract.json
```

## Next Step

Run `/superjeff:build <app_name>` to implement the specified app.

## Failure Modes

| Error | Cause | Resolution |
|---|---|---|
| `app_not_found` | App name not in decomposition | Check spelling; run /superjeff:decompose first |
| `schema_validation_failed` | Requirements don't match schema | Re-run or provide more detail about the app |
| `insufficient_test_cases` | < 5 test cases per endpoint | Agent will retry with explicit test generation |
