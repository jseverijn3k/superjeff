---
name: "Characterization Testing"
description: "Write tests that capture what existing code currently does — not what it should do. These tests are the safety net for refactoring legacy Django code without breaking behaviour."
version: "1.0"
origin: "superjeff"
---

## When to Activate

- Before any refactoring of existing code
- `conform_pipeline.yaml` enters the `characterization_tests` stage
- The Audit Agent has produced `artifacts/plans/<app>_characterization_plan.md`

## What Characterization Tests Are

A characterization test documents the **current behaviour** of code — including bugs. If the code returns a 500 for a missing field, the characterization test asserts `status_code == 500`. You are not testing what is correct; you are creating a tripwire that fires if refactoring accidentally changes behaviour.

Once refactoring is complete and the architecture is clean, you replace characterization tests with proper tests that assert what the code *should* do.

**The rule: characterization tests must all pass before you touch a single line of production code.**

## Process

### Step 1 — Read the characterization test plan

Load `artifacts/plans/<app>_characterization_plan.md`. This is the Audit Agent's output listing every view and its observed behaviour.

### Step 2 — Write one test per observed behaviour

For each entry in the plan:

```python
# apps/<app>/tests/test_characterization.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.<app>.tests.factories import <Model>Factory
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db

class TestCharacterization<ViewName>:
    """
    Characterization tests for <ViewName>.
    These document CURRENT behaviour — do not fix bugs here.
    Replace with proper tests after refactoring is complete.
    """

    def test_<view>_<scenario>_returns_<status>(self):
        # Arrange: minimal setup to reach the code path
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Act: call the endpoint exactly as a real client would
        response = client.get(reverse("<app>:<url-name>"))

        # Assert: whatever the code currently returns — even if wrong
        assert response.status_code == 200  # document what IS, not what should be
```

### Step 3 — Run all tests, confirm they pass

```bash
pytest apps/<app>/tests/test_characterization.py -v
```

**All tests must pass before refactoring begins.** If a characterization test fails, your understanding of the current behaviour is wrong — fix the test, not the code.

### Step 4 — Keep tests green throughout refactoring

Run the full characterization suite after every refactoring task:

```bash
pytest apps/<app>/tests/test_characterization.py -v --tb=short
```

If any characterization test fails after a refactor step, stop and undo that step. You changed behaviour unintentionally.

### Step 5 — Replace with proper tests after refactoring

Once the app is fully refactored:

1. Delete `test_characterization.py`
2. Write proper tests in `test_models.py`, `test_services.py`, `test_views.py`, `test_api.py`
3. These assert what the code *should* do, not just what it happens to do

## What to Cover

For every existing view, write tests for:

| Scenario | What to assert |
| --- | --- |
| Happy path with auth | `status_code`, response shape |
| Without auth (if auth exists) | whether it 401s or not |
| Missing required data | current error behaviour (even if it's a 500) |
| Object that belongs to another user | whether isolation works or not |

Mark tests that document a **known bug** with:
```python
# KNOWN BUG: this returns 200 instead of 404 for missing resource
# Do not fix here — fix after refactoring with a proper test
```

## Writing Tips for Untestable Code

Legacy code is often hard to test because it has no seams. Common problems and workarounds:

**Problem: View creates objects directly with no factory**
```python
# Workaround: create objects manually for now, note it in the test
user = User.objects.create_user(email="test@test.com", password="pass")
# TODO: replace with UserFactory after refactoring
```

**Problem: View calls external service with no mock**
```python
# Workaround: patch the external call
from unittest.mock import patch

def test_view_that_calls_stripe(self):
    with patch("apps.payments.views.stripe.charge.create") as mock_charge:
        mock_charge.return_value = {"id": "ch_test"}
        response = client.post(...)
    assert response.status_code == 200
```

**Problem: No URL name defined**
```python
# Workaround: use hardcoded path for now, note the gap
response = client.get("/api/expenses/")  # TODO: add url name after refactoring
```

## Anti-Patterns

Avoid:
- Writing characterization tests that fix bugs — document the bug, don't fix it
- Skipping characterization tests because "the code is simple" — simplicity is not a reason to skip a safety net
- Deleting characterization tests before the refactor is complete
- Running only new tests after a refactor step — always run the full characterization suite

## Related Skills

- [Systematic Debugging](../debugging/SKILL.md) — when a characterization test reveals unexpected behaviour
- [Planning & Subtask Breakdown](../planning/SKILL.md) — refactoring tasks come after characterization tests pass
- [TDD Workflow](../testing/SKILL.md) — the proper tests that replace characterization tests
