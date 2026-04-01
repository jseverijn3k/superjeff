---
name: "TDD Workflow for Django"
description: "Test-driven development workflow for Django + DRF: write failing tests first, implement to pass, refactor"
version: "1.0"
origin: "superjeff"
---

## When to Activate

- Build pipeline enters the `write_tests` stage
- User runs `/superjeff:build <app_name>`

## RED Phase — Writing Failing Tests

Generate test files before any implementation:

```python
# tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .factories import UserFactory, ExpenseFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user

class TestExpenseListCreate:

    def test_list_expenses_success(self, authenticated_client):
        client, user = authenticated_client
        ExpenseFactory.create_batch(3, owner=user)
        response = client.get(reverse('expenses:expense-list'))
        assert response.status_code == 200
        assert response.data['count'] == 3

    def test_list_expenses_unauthenticated(self, api_client):
        response = api_client.get(reverse('expenses:expense-list'))
        assert response.status_code == 401

    def test_create_expense_success(self, authenticated_client):
        client, user = authenticated_client
        data = {'title': 'Lunch', 'amount': '25.00', 'category': 'meals'}
        response = client.post(reverse('expenses:expense-list'), data)
        assert response.status_code == 201
        assert response.data['title'] == 'Lunch'

    def test_create_expense_invalid_amount(self, authenticated_client):
        client, _ = authenticated_client
        data = {'title': 'Lunch', 'amount': '-10.00'}
        response = client.post(reverse('expenses:expense-list'), data)
        assert response.status_code == 400
        assert 'amount' in response.data

    def test_list_expenses_only_own(self, authenticated_client, api_client):
        client, user = authenticated_client
        other_user = UserFactory()
        ExpenseFactory(owner=other_user)  # Should NOT appear in user's list
        response = client.get(reverse('expenses:expense-list'))
        assert response.data['count'] == 0
```

## Factory Pattern

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = 'accounts.User'

    email = factory.LazyAttribute(lambda _: fake.email())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class ExpenseFactory(DjangoModelFactory):
    class Meta:
        model = 'expenses.ExpenseReport'

    owner = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    amount = factory.LazyAttribute(lambda _: fake.pydecimal(min_value=1, max_value=1000, right_digits=2))
```

## Confirm RED (before implementation)

```bash
pytest apps/<app_name>/tests/ -v
# All new tests must FAIL here
# If any pass: the test is wrong — fix it
```

## GREEN Phase — Implement to Pass

Implement models → serializers → views → urls in that order.

```bash
pytest apps/<app_name>/tests/ -v
# All tests must PASS here
```

## REFACTOR Phase

- Remove duplication
- Extract common fixtures
- Ensure no test has side effects on others
- All tests still pass after refactoring

## Anti-Patterns

Avoid:
- Writing tests after implementation
- Using `unittest.TestCase` — use plain pytest functions
- `model.objects.create()` in tests — use factories
- Assertions on response text — assert on `response.data` and `status_code`
- Shared mutable state between tests

## Related Skills

- [Django App Specification](../django/SKILL.md)
- [Validation Pipeline](../validation/SKILL.md)
