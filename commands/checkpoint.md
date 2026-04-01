---
name: checkpoint
command: /superjeff:checkpoint
description: Save current pipeline state, summarize progress, and identify the next step
input: None
output: artifacts/pipeline_state.json (updated) + printed summary
---

## Purpose

Saves pipeline state mid-session and prints a human-readable summary of what has been done and what comes next. Use this before context gets long, before a break, or after completing any pipeline stage.

## What Happens

1. Reads all artifacts in `artifacts/` to determine current pipeline position
2. Updates `artifacts/pipeline_state.json` with current stage, completed artifacts, and pending tasks
3. Prints a session summary

## Output Example

```
=== SuperJeff Checkpoint ===

Project: expensio
Current stage: implement (expenses)

Completed:
  ✓ artifacts/specs/2026-01-15-expense-tracker.md
  ✓ artifacts/decomposition.json (7 apps)
  ✓ artifacts/requirements/expenses.json
  ✓ artifacts/plans/expenses_plan.md
  ✓ artifacts/tests/expenses/ (7 test files, all RED confirmed)

In progress:
  → Task 8/14: implement ExpenseService.list_expenses()

Pending:
  - Remaining implement tasks (6 of 14)
  - code_review stage
  - verify_green stage
  - quality_audit stage
  - security_review stage
  - validate stage

Apps not yet specified: accounts, budgets, approvals, payments, notifications, reporting

Next action: continue /superjeff:build expenses from task 8
===
```

## When to Use

- Before context window gets full (use `/superjeff:checkpoint` proactively every 30-40 exchanges)
- After completing a pipeline stage
- Before switching to a different app
- At end of a work session
