---
name: conform
command: /superjeff:conform
description: Bring an existing Django app into SuperJeff conformance — audit, characterization tests, refactor, then hand off to the normal build pipeline
input: App name + path (e.g. expenses apps/expenses)
output: Conformed app with service layer, FBVs, proper tests, and a clean gap report
workflow: workflows/conform_pipeline.yaml
---

## Purpose

For existing Django apps that work but don't follow SuperJeff architecture conventions. Runs a structured conform pipeline that is safe for production repos: it establishes a test safety net before touching any code.

## Usage

```
/superjeff:conform <app_name> <app_path>
```

Example:
```
/superjeff:conform expenses apps/expenses
```

## What Happens (9 stages)

```
1. Audit          Read all existing code → reverse-engineered spec + gap report
                  git commit: audit(expenses)

2. Review Gaps    Surface critical gaps to you — must acknowledge before continuing

3. Factories      Create factory_boy factories for all existing models
                  git commit: test(expenses): factories for existing models

4. Characterization Tests
                  Write tests documenting CURRENT behaviour (including bugs)
                  All must pass before any refactoring begins
                  git commit: test(expenses): characterization tests

5. Refactor Plan  Generate 2-5 min tasks ordered: security → exceptions → models
                  → services → serializers → views (FBV) → urls → cleanup
                  git commit: plan(expenses): refactoring task plan

6. Refactor       Execute plan task-by-task
                  Characterization tests run after EVERY task
                  git commit: refactor(expenses): <task> per task

7. Architecture Check
                  Grep for CBVs, ViewSets, direct ORM, fields=__all__
                  All must return no output

8. Replace Tests  Delete characterization tests, write proper tests
                  (success + 401 + 403 + 400 + 404 per endpoint)
                  git commit: test(expenses): replace characterization tests

9. Quality + Security Audit + Validate
                  git commit: validate(expenses): conform complete
```

## After Conform

The app is now ready for normal feature development:

```
/superjeff:brainstorm   ← design new feature
/superjeff:specify expenses  ← generates spec for new feature
/superjeff:build expenses    ← builds via normal TDD pipeline
```

## What Makes This Safe for Existing Code

The key is **characterization tests first**. You cannot safely refactor without them. They lock in current behaviour so you know immediately if a refactoring step breaks something — before you commit it.

The refactor plan runs the characterization suite after every single task. If any test fails, the task is undone and re-approached.

## When to Run Per App vs All at Once

Run per app, not all at once. Conform one app, validate it, then move to the next. This keeps commits small and failures isolated.

Suggested order: start with the most independent app (fewest dependencies), work outward.

## Failure Modes

| Error | Cause | Resolution |
| --- | --- | --- |
| `characterization_test_failed_before_refactor` | Test doesn't match actual behaviour | Fix the test — don't touch the code |
| `characterization_test_failed_after_refactor` | Refactor changed behaviour | Undo the task, re-approach |
| `critical_gap_unresolved` | Architecture gap not fixed | Check refactor plan task coverage |
| `cbv_still_present` | FBV migration missed a view | Search with `grep -rn "class.*View"` |
