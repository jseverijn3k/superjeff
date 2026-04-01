---
name: "Code Review"
description: "Systematic code review after each build stage, not just at the end. Reviews for spec compliance first, then code quality."
version: "1.0"
origin: "superpowers-inspired"
---

## When to Activate

- After the `implement` stage — before `refactor`
- After the `refactor` stage — before `secure`
- When the Quality Agent produces findings — to resolve them
- When a human reviewer provides feedback

## Two-Stage Review Process

Code review happens in two stages, in this order. Do not combine them.

### Stage 1 — Spec Compliance Review

Does the code do what the requirements artifact says it should?

Check against `artifacts/requirements/<app>.json`:

- [ ] Every model defined in the spec exists with the correct fields
- [ ] Every service method in the spec exists with the correct signature
- [ ] Every API endpoint in the spec exists with the correct method, path, and auth requirement
- [ ] Every business rule in the spec is enforced in the correct layer (model / serializer / service / view)
- [ ] Every test case in the spec has a corresponding test function

If any spec item is missing: stop Stage 2. Fix the gap first.

### Stage 2 — Code Quality Review

Is the code well-written within the spec?

- [ ] Service layer: every view uses a service — no direct ORM
- [ ] FBV only: no CBVs, ViewSets, or DRF routers
- [ ] Models are dumb: no business methods, no cross-model queries
- [ ] Serializers have no ownership checks and no business logic
- [ ] `@extend_schema` on all API views
- [ ] No `print()` — only `logging.getLogger(__name__)`
- [ ] No bare `except:` clauses
- [ ] No `fields = "__all__"` in serializers
- [ ] `select_related` / `prefetch_related` in service methods for every list endpoint
- [ ] Domain exceptions used, not raw `Exception`
- [ ] Migrations present and idempotent (if raw SQL)

## Providing Feedback

When giving feedback on code, be specific:

**Good:** "Line 42 in `expenses/views.py`: `ExpenseReport.objects.filter(owner=request.user)` should move to `ExpenseService.list_expenses(request.user)`. The view is doing ORM work."

**Bad:** "The service layer needs improvement."

Every piece of feedback must include:
- File + line number
- What is wrong
- What it should be instead
- Why (rule reference)

## Receiving Feedback

When feedback is received:

1. Read every comment before making any changes
2. For each comment: understand the rule being violated — don't just apply the fix mechanically
3. If you disagree, explain the reasoning before pushing back — "I think this is correct because..." not just "I'll leave it"
4. After making all changes: re-run the full test suite
5. Re-run the Quality Agent gate to confirm all findings are resolved

**Do not:**
- Fix the symptom without understanding the cause
- Make unrelated changes during a review cycle
- Agree with feedback you don't understand — ask for clarification

## Review Severity Triage

When reviewing Quality Agent findings:

| Severity | Action |
| --- | --- |
| `critical` | Block. Fix before next stage. Re-run Quality Agent. |
| `high` | Block. Fix before next stage. Re-run Quality Agent. |
| `medium` | Fix in the same session. Note in commit message. |
| `low` | Fix or log as accepted technical debt. Note in commit. |

## Related Skills

- [Verification Before Completion](../verification/SKILL.md) — run after review changes
- [Systematic Debugging](../debugging/SKILL.md) — when a fix introduces new failures
- [Planning & Subtask Breakdown](../planning/SKILL.md) — review findings become new tasks
