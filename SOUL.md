# SOUL — The Design Principles of SuperJeff

SuperJeff is an AI-native software development system. These principles govern every agent, skill, workflow, and hook in this repository.

---

## The Five Principles

### 1. Agent-First
Route every task to the appropriate specialist immediately. The orchestrator exists to delegate, not to execute. A general-purpose response is a failed response.

### 2. Test-Driven
No implementation without a failing test. Always: RED → GREEN → REFACTOR. Test coverage is a prerequisite for code review, not an afterthought.

### 3. Security-First
Sanitize all inputs. Protect all credentials. Default to the most restrictive permission. Security is not a QA gate — it is a design constraint.

### 4. Structured Output
Every agent produces JSON or YAML. Never prose. If a human can read it but a machine cannot parse it, the output is invalid.

### 5. Plan Before Execute
Decompose before building. Specify before coding. Review before merging. No implementation phase begins without a completed planning artifact.

### 6. Commit Every Stage

Every completed pipeline stage produces a git commit. No exceptions. A stage without a commit did not happen. Commit messages follow the format below and must reference the stage and app name.

---

## Git Workflow

SuperJeff uses git as the audit trail for the pipeline. Every stage transition is a commit.

### Commit Message Format

```
<type>(<app>): <description>

[optional body]
```

**Types:**

| Type | When to use |
| --- | --- |
| `decompose` | After Product Decomposition Agent produces app list |
| `specify` | After Requirements Agent produces app spec |
| `test` | After failing tests are written (RED phase) |
| `implement` | After implementation passes tests (GREEN phase) |
| `refactor` | After Quality Agent review and fixes |
| `secure` | After Security Agent review and fixes |
| `validate` | After full validation passes |

### Examples

```
decompose(expensio): 7 Django apps from expense tracker business case

specify(expenses): full model/view/serializer spec with 7 test cases

test(expenses): failing tests for expense report CRUD and submit flow

implement(expenses): ExpenseReport models, serializers, views — all tests pass

refactor(expenses): fix missing Meta.ordering and add db_index on owner FK

secure(expenses): add rate limiting to submit endpoint, scope queryset to company

validate(expenses): all quality and security gates pass
```

### Rules

- MUST commit after every stage — never batch multiple stages into one commit
- MUST use the correct `type` prefix so the pipeline audit trail is readable
- MUST include the app name in the scope (e.g. `specify(accounts)`)
- MUST NOT commit broken tests or failing code — GREEN before commit on `implement`
- MUST NOT use `--no-verify` to bypass hooks

---

## Pipeline Stages

```text
Business Case
     ↓
Product Decomposition      [Product Decomposition Agent]
     ↓  git commit: decompose(<project>)
App Requirements           [Requirements Agent × N apps]
     ↓  git commit: specify(<app>) per app
Implementation Plan        [Planning Agent]
     ↓
TDD — Write Failing Tests  [Execution Layer]
     ↓  git commit: test(<app>)
TDD — Implement to Pass    [Execution Layer]
     ↓  git commit: implement(<app>)
Code Review                [Quality Agent]
     ↓  git commit: refactor(<app>)
Security Check             [Security Agent]
     ↓  git commit: secure(<app>)
Accessibility Check        [Quality Agent]
     ↓
Validated Artifact
     ↓  git commit: validate(<app>)
```

---

## What SuperJeff Is Not

- Not a code generator that skips tests
- Not a system that produces vague prose specifications
- Not a monolithic agent trying to do everything
- Not a system that ships without security review
