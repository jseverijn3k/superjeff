---
name: learn
command: /superjeff:learn
description: Extract a reusable pattern, rule, or instinct from the current session and save it to the appropriate instinct file
input: Description of what to learn (free text)
output: Updated instinct file in instincts/ or new skill in skills/
---

## Purpose

Captures something discovered in the current session — a new Django pattern, a recurring mistake, a better approach — and saves it as a permanent rule so it applies to all future projects.

This is how SuperJeff improves over time.

## Usage

```
/superjeff:learn
```

Then describe what to capture. Examples:

- "We found that Celery tasks should always use `task_soft_time_limit` to prevent runaway tasks"
- "The pattern for idempotent cache invalidation is to delete the key and let it rebuild on next read, not to update in place"
- "When using `select_for_update()`, always wrap in `transaction.atomic()` or PostgreSQL raises an error"

## What Happens

1. Agent classifies the insight: is it a model rule? A security rule? A testing rule? A new skill?
2. Writes the rule to the appropriate file:
   - Django patterns → `instincts/django.yaml`
   - Security patterns → `instincts/security.yaml`
   - Testing patterns → `instincts/testing.yaml`
   - New workflow → `skills/<name>/SKILL.md`
3. Prints confirmation with the rule ID and location

## Rule Format Added

```yaml
- id: <snake_case_id>
  trigger: "<when this applies>"
  rule: "<the rule, imperative>"
  pattern: "<example if helpful>"
  severity: critical|high|medium|low
  learned_from: "<brief context>"
```

## When to Use

- When you find a pattern that isn't in the instincts yet
- When a bug was caused by a missing rule
- When a code review finding should become permanent
- When the security agent finds something not yet in `security.yaml`
