---
name: "Planning & Subtask Breakdown"
description: "Decompose a requirements artifact into a granular, dependency-ordered task list. Each task is 2-5 minutes of focused work with exact file paths, complete code, and inline verification commands."
version: "1.0"
origin: "superpowers-inspired"
---

## When to Activate

- Build pipeline enters the `plan` stage
- User runs `/superjeff:build <app>`
- Orchestrator calls `generate_task_list` action

## Why This Matters

Vague tasks ("add validation to the serializer") cause implementation drift. A task is only good if you could hand it to someone who has never seen the codebase and they could complete it in under 5 minutes without asking a question.

Every task in the plan must be:
- **Atomic** — one logical change, one file, one concern
- **Verifiable** — has a command that proves it worked
- **Ordered** — depends only on tasks listed before it
- **Complete** — contains the actual code, not a description of the code

## Task Format

Every task follows this exact structure:

```markdown
### Task N: <action verb> <what> in <file>

**File:** `apps/<app>/path/to/file.py` (line N if modifying existing)
**Depends on:** Task M (if any)

#### What to write

```python
# Complete, runnable code — no placeholders, no "add here"
def validate_amount(self, value):
    if value <= 0:
        raise serializers.ValidationError("Amount must be greater than zero.")
    return value
```

#### Verify

```bash
pytest apps/<app>/tests/test_serializers.py::TestExpenseSerializer::test_amount_negative -v
```

Expected output: `PASSED` (or `FAILED` if this is a RED task)

#### Commit

```
test(expenses): failing test for negative expense amount
```
```

## Task Ordering Rules (STRICT)

The plan must follow this dependency order — no exceptions:

```
1. Exceptions       apps/<app>/exceptions.py
2. Models           apps/<app>/models.py
3. Migrations       python manage.py makemigrations <app>
4. Factories        apps/<app>/tests/factories.py
5. Tests (RED)      apps/<app>/tests/test_models.py
                    apps/<app>/tests/test_services.py
                    apps/<app>/tests/test_views.py
                    apps/<app>/tests/test_api.py
6. Services         apps/<app>/services/<service>.py
7. Permissions      apps/<app>/permissions.py
8. Serializers      apps/<app>/serializers.py
9. Views (HTML)     apps/<app>/views.py
10. Views (API)     api/v1/views/<app>.py
11. URLs            apps/<app>/urls.py + api/v1/urls.py
12. Signals         apps/<app>/signals.py (if needed)
13. Verify GREEN    pytest — all tests must pass
```

## Granularity Rules

**Target: each task takes 2-5 minutes.**

Split a task if it:
- Touches more than one file
- Has more than one `def` or `class`
- Would require more than one commit message to describe
- Has more than one verification command

Merge tasks if:
- They are always done together (e.g., `exceptions.py` often has 2-3 exception classes — one task)
- Splitting them would leave code in an unrunnable state

## RED Phase Tasks

For every test file, generate tasks in this order:

1. **Write the factory** (if not yet existing)
2. **Write the failing test** — run it, confirm it FAILS
3. *(later)* **Write the implementation** — run the test, confirm it PASSES

Never write implementation tasks before the corresponding test task. If you find yourself writing an implementation task with no test task before it, stop and write the test first.

## Plan Self-Review Checklist

Before finalizing the plan:

- [ ] Every task has an exact file path (no "somewhere in services.py")
- [ ] Every task has complete, runnable code (no `# ... rest of implementation`)
- [ ] Every task has a verify command with expected output
- [ ] Every task has a commit message
- [ ] No two consecutive tasks modify the same file (if they do, merge them)
- [ ] Tests come before implementations — no exceptions
- [ ] Migrations task follows every model task
- [ ] No task references a file or class that doesn't exist yet at that point in the plan
- [ ] The final task is `pytest` — all tests pass

## Example: Plan for `expenses` App (abbreviated)

```markdown
# Plan: expenses app

Source: artifacts/requirements/expenses.json
Design: artifacts/specs/2026-01-15-expense-tracker.md

---

### Task 1: Create domain exceptions

**File:** `apps/expenses/exceptions.py`

```python
class ExpenseError(Exception):
    pass

class ExpenseSubmitError(ExpenseError):
    pass

class EmptyReportError(ExpenseSubmitError):
    pass
```

**Verify:** `python -c "from apps.expenses.exceptions import EmptyReportError; print('OK')"`
**Commit:** `model(expenses): domain exceptions`

---

### Task 2: Create ExpenseReport model

**File:** `apps/expenses/models.py`

```python
import uuid
from django.db import models

class ExpenseReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="expense_reports")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[
        ("draft", "Draft"), ("submitted", "Submitted"),
        ("approved", "Approved"), ("rejected", "Rejected"),
    ], default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["owner", "status"])]

    def __str__(self):
        return f"{self.title} ({self.owner.email})"
```

**Verify:** `python manage.py check apps.expenses`
**Commit:** `model(expenses): ExpenseReport model`

---

### Task 3: Create migration

**Command:** `python manage.py makemigrations expenses`
**Verify:** Migration file exists in `apps/expenses/migrations/`
**Commit:** `model(expenses): initial migration`

---

### Task 4: Create ExpenseReport factory

**File:** `apps/expenses/tests/factories.py`

```python
import factory
from factory.django import DjangoModelFactory
from apps.expenses.models import ExpenseReport
from apps.accounts.tests.factories import UserFactory

class ExpenseReportFactory(DjangoModelFactory):
    class Meta:
        model = ExpenseReport
    owner = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Expense Report {n}")
    status = "draft"
```

**Verify:** `python -c "from apps.expenses.tests.factories import ExpenseReportFactory; print('OK')"`
**Commit:** `test(expenses): ExpenseReport factory`

---

### Task 5: Write failing test — list endpoint scope

**File:** `apps/expenses/tests/test_api.py`

```python
@pytest.mark.django_db
def test_list_expenses_only_own(authenticated_client):
    client, user = authenticated_client
    other = UserFactory()
    ExpenseReportFactory(owner=other)
    response = client.get(reverse("api:v1:expenses-list"))
    assert response.status_code == 200
    assert response.data["count"] == 0
```

**Verify:** `pytest apps/expenses/tests/test_api.py::test_list_expenses_only_own -v`
Expected: `FAILED` (view doesn't exist yet)
**Commit:** `test(expenses): failing test — list scoped to owner`

---

[...tasks continue through services → views → urls → GREEN verification...]

---

### Final Task: Verify all tests pass

**Command:** `pytest apps/expenses/ -v`
Expected: all PASSED, 0 failures
**Commit:** `implement(expenses): all tests green`
```

## Output

Save the plan to: `artifacts/plans/<app>_plan.md`

The plan is the single source of truth for the `implement` stage. If implementation diverges from the plan, update the plan first and note why.

## Related Skills

- [Brainstorming & Design Gate](../brainstorming/SKILL.md) — input to this skill
- [TDD Workflow](../testing/SKILL.md) — RED/GREEN details
- [Verification](../verification/SKILL.md) — final gate after plan execution
