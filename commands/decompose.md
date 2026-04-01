---
name: decompose
command: /superjeff:decompose
description: Transform a business case into a structured list of Django apps
input: Free-text business case (passed inline or from a file)
output: artifacts/decomposition.json (validated against schemas/app_schema.json)
workflow: workflows/bc_to_apps.yaml
---

## Purpose

Runs the Product Decomposition Agent on a business case and produces a validated JSON app decomposition.

## Usage

```
/superjeff:decompose
```

Then provide your business case as free text, or reference a file:

```
/superjeff:decompose < business_case.txt
```

## What Happens

1. The Orchestrator loads `workflows/bc_to_apps.yaml`
2. The Product Decomposition Agent receives your business case
3. The agent produces a JSON decomposition following Django conventions
4. The output is validated against `schemas/app_schema.json`
5. A circular dependency check is performed
6. The artifact is saved to `artifacts/decomposition.json`
7. A summary is printed: N apps, their names, and their dependencies

## Output Example

```json
{
  "project_name": "expensio",
  "apps": [
    { "name": "accounts", "models": ["User", "Company"], "dependencies": [] },
    { "name": "expenses", "models": ["ExpenseReport"], "dependencies": ["accounts"] }
  ]
}
```

## Next Step

Run `/superjeff:specify <app_name>` for each app in the output.

## Failure Modes

| Error | Cause | Resolution |
|---|---|---|
| `schema_validation_failed` | Agent output doesn't match app_schema.json | Re-run with more specific business case |
| `circular_dependency_detected` | App A depends on B and B depends on A | Review agent output and split the dependency |
| `monolith_detected` | Single app has 6+ unrelated models | Agent will auto-split; review the split |
