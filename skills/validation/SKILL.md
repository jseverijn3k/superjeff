---
name: "Validation Pipeline"
description: "Quality and security validation gates for generated Django code"
version: "1.0"
origin: "superjeff"
---

## When to Activate

- User runs `/superjeff:validate`
- Build pipeline enters `refactor`, `security_review`, or `validate` stages

## Quality Gate Checklist

Run these checks in order. Stop at first `critical` failure.

### Gate 1: Test Suite
```bash
pytest --tb=short -q
# Expected: all tests pass, 0 failures
```

### Gate 2: Django Conventions
```bash
# Check all models have __str__
grep -rn "def __str__" apps/*/models.py

# Check no serializer uses __all__
grep -rn "fields = '__all__'" apps/*/serializers.py
# Expected: no matches

# Check all views have permission_classes
grep -rn "permission_classes" apps/*/views.py
```

### Gate 3: Migrations
```bash
python manage.py migrate --check
# Expected: no pending migrations
```

### Gate 4: Security Quick Scan
```bash
# Check for hardcoded secrets
grep -rn "SECRET_KEY\s*=" apps/ --include="*.py"
grep -rn "password\s*=\s*['\"]" apps/ --include="*.py"

# Check for raw SQL
grep -rn "\.raw(" apps/ --include="*.py"
grep -rn "cursor\.execute" apps/ --include="*.py"
```

## Severity Classification

| Severity | Example | Pipeline Action |
|---|---|---|
| critical | Unauthenticated write endpoint | HALT |
| high | Missing `__str__`, raw SQL | HALT |
| medium | Missing ordering in Meta | WARN |
| low | Print statement in non-test code | WARN |

## Anti-Patterns

Avoid:
- Skipping validation before submitting code for review
- Treating `medium` findings as unimportant (they compound)
- Running validate only at the end — run after each app build

## Related Skills

- [TDD Workflow](../testing/SKILL.md)
- [Django App Specification](../django/SKILL.md)
