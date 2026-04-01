---
name: "Verification Before Completion"
description: "Evidence-before-claims gate. Never mark a task done based on belief. Always run fresh verification and show the output."
version: "1.0"
origin: "superpowers-inspired"
---

## When to Activate

- Before marking any task as complete
- Before the `implement` stage transitions to `refactor`
- Before the `refactor` stage transitions to `secure`
- Before claiming "all tests pass"
- Before any git commit on an `implement` or `refactor` stage

## The Core Rule

**Claiming something works is not the same as verifying it works.**

A test that passed 10 minutes ago may not pass now. The codebase changed. Run it again.

Never write "all tests pass" in a commit message, comment, or response without having run `pytest` in the same session and seeing the output.

## Verification Checklist

Before completing any implementation stage:

### 1. Run the full test suite fresh

```bash
pytest apps/<app>/ -v --tb=short
```

- [ ] All tests pass — zero failures, zero errors
- [ ] No tests were skipped that should run
- [ ] The number of passing tests matches the number of test cases in the requirements artifact

### 2. Verify no regressions

```bash
pytest --tb=short -q
```

- [ ] Tests in other apps still pass — your changes did not break anything else

### 3. Verify migrations are clean

```bash
python manage.py migrate --check
```

- [ ] No pending migrations
- [ ] No "your models in app X have changes that are not yet reflected in a migration" warnings

### 4. Verify the architecture gate

```bash
# No CBVs or ViewSets
grep -rn "class.*APIView\|ModelViewSet\|ReadOnlyModelViewSet" apps/ api/
# Expected: no output

# No direct ORM in views
grep -rn "\.objects\." apps/*/views.py api/
# Expected: no output

# No __all__ in serializers
grep -rn "fields = '__all__'\|fields = \"__all__\"" apps/ api/
# Expected: no output
```

- [ ] All grep commands return no output

### 5. Verify the commit is clean

- [ ] `git status` shows only intentional changes
- [ ] `git diff` contains only what the task specifies — nothing extra, nothing missing

## Evidence Format

When reporting task completion, always include the actual output:

```
✓ Task 7 complete

pytest apps/expenses/ -v
========================= 14 passed in 0.83s =========================

python manage.py migrate --check
No migrations to apply.

grep CBV check: no output ✓
```

Never write "done" without evidence. Never write "tests pass" without showing the output.

## The Intermediate State Problem

After each task (not just at the end of the plan):

- The code compiles / has no syntax errors
- Existing tests still pass (new tests may still be RED)
- No half-implemented functions (`pass` stubs without a test to cover them)

If a task leaves the codebase in a broken intermediate state, it was too large. Split it.

## Anti-Patterns

Avoid:
- "Tests should pass now" — run them and show the output
- Committing before running the test suite
- Running only the new tests, not the full suite
- Counting test output lines from a previous run
- "I'll verify at the end" — verify at every task checkpoint

## Related Skills

- [Planning & Subtask Breakdown](../planning/SKILL.md) — tasks must be small enough to verify individually
- [Systematic Debugging](../debugging/SKILL.md) — what to do when verification fails
- [TDD Workflow](../testing/SKILL.md) — RED/GREEN are both verification steps
