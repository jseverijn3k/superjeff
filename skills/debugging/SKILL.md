---
name: "Systematic Debugging"
description: "4-phase root-cause methodology. Never fix symptoms. Always understand before acting. Circuit breaker after 3 failed attempts."
version: "1.0"
origin: "superpowers-inspired"
---

## When to Activate

- A test fails unexpectedly
- An implementation doesn't behave as specified
- An error recurs after a previous fix
- You are about to try something for the third time

## The 4 Phases

### Phase 1 — Observe

Stop. Read the full error output. Do not skip lines.

Collect:
- Exact error message (not a paraphrase)
- Exact file and line number
- Stack trace (the full one, not just the last frame)
- What was the last change made before this error appeared?

Do not form a hypothesis yet. You are gathering facts.

### Phase 2 — Hypothesize

Form one hypothesis: "I believe the error is caused by X because Y."

Be specific:
- "I believe the error is caused by a missing `select_related` on line 42 of `activity_service.py` because the stack trace shows an N+1 query on `ActivityProgress`"
- NOT: "I think there's a database issue"

If you cannot form a specific hypothesis, go back to Phase 1 and read more carefully.

### Phase 3 — Verify the Hypothesis

Before writing any fix, verify the hypothesis is correct:

- Add a temporary `print` or `logger.debug` to confirm the assumption
- Write a minimal reproduction (a test that fails for this exact reason)
- Check if the failure disappears when you remove only the hypothesized cause

If the failure does not disappear when you remove the hypothesized cause, your hypothesis is wrong. Go back to Phase 2.

### Phase 4 — Fix the Root Cause

Fix only what your verified hypothesis identified. Do not clean up unrelated code while fixing a bug.

After the fix:
- Run the failing test — it must pass
- Run the full test suite — nothing new must fail
- Commit with a message that explains the root cause: `fix(expenses): select_related missing caused N+1 on activity list`

## The Circuit Breaker

**If you have attempted 3 different fixes and the error persists: stop.**

This means your mental model of the system is wrong. Do not try a 4th fix.

Instead:
1. Write down exactly what you have tried and what happened
2. Re-read the relevant model definitions, service methods, and test setup from scratch
3. Ask: "What assumption am I making that could be wrong?"
4. Start Phase 1 again with fresh eyes

A wrong mental model fixed with more guesses produces fragile code. An hour of re-reading is faster than a day of accidental fixes.

## Anti-Patterns

Avoid:
- **Symptom fixing** — changing the test to pass instead of fixing the code
- **Shotgun debugging** — making 3 changes at once and seeing if one works
- **Hopeful uncommitted changes** — running tests with temporary hacks and calling it fixed
- **Skipping the stack trace** — "I know what's wrong" before reading the error
- **Fixing unrelated code** — cleaning up while debugging (creates new bugs, obscures the fix)

## Django-Specific Debugging Checklist

When a test fails in Django:

- [ ] Is the test database populated? (`@pytest.mark.django_db` on the test or class)
- [ ] Did the factory create the object in the right state?
- [ ] Is the queryset scoped to the test user? (ownership check)
- [ ] Did `makemigrations` run after a model change?
- [ ] Is `select_related` / `prefetch_related` missing (N+1)?
- [ ] Is a signal firing unexpectedly and changing state?
- [ ] Is the URL reversed correctly? (`reverse("app:view-name")`)
- [ ] Is the authenticated user the owner of the resource in the test?

## Related Skills

- [TDD Workflow](../testing/SKILL.md) — tests are your debugging instruments
- [Verification](../verification/SKILL.md) — confirm fixes are real before claiming done
