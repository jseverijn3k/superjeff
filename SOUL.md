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
| `design` | After brainstorm design artifact OR UX spec is saved |
| `decompose` | After Product Decomposition Agent produces app list |
| `specify` | After Requirements Agent produces app spec |
| `audit` | After Audit Agent produces spec + gap report (conform pipeline) |
| `plan` | After task breakdown plan is generated |
| `test` | After failing/characterization tests are written |
| `implement` | After implementation passes tests (GREEN phase) |
| `refactor` | After code review, Quality Agent fixes, or refactor task |
| `secure` | After Security Agent review and fixes |
| `validate` | After full validation passes |

### Examples

```
design(expensio): expense tracker — multi-tenant approval workflow design

decompose(expensio): 7 Django apps from expense tracker business case

specify(expenses): full model/view/serializer spec with 7 test cases

plan(expenses): 14 tasks — exceptions → models → factories → tests → services → views

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

## Pipeline A — New Features (build_pipeline)

```text
Business Case
     ↓
/superjeff:brainstorm       [Brainstorming Skill]
     ↓  → artifacts/specs/YYYY-MM-DD-<feature>.md
Product Decomposition       [Product Decomposition Agent]
     ↓  git commit: decompose(<project>)
App Requirements            [Requirements Agent × N apps]
     ↓  git commit: specify(<app>) per app
UX Design                   [/superjeff:design — UX Skill + Frontend Agent]
     ↓  git commit: design(<app>)   → artifacts/ux/<app>_ux_spec.json
     ↓  design tokens, pages, components, HTMX patterns, accessibility
Implementation Plan         [Planning Skill — 2-5 min tasks: backend + frontend]
     ↓  git commit: plan(<app>)
TDD — Write Failing Tests   [Testing Skill — pytest + factory_boy]
     ↓  git commit: test(<app>)   ← all tests confirmed FAILING
TDD — Implement to Pass     [Follow plan task-by-task, verify after each]
     ↓  git commit: implement(<app>)  ← all tests confirmed PASSING
Code Review                 [Code Review Skill — spec compliance + architecture]
     ↓  git commit: refactor(<app>)
Verification Gate           [Verification Skill — fresh pytest + grep checks]
     ↓  evidence shown, not assumed
Quality Audit               [Quality Agent — 5-gate structured report]
     ↓  git commit: refactor(<app>) if fixes needed
Security Audit              [Security Agent — OWASP Top 10]
     ↓  git commit: secure(<app>)
Validated Artifact
     ↓  git commit: validate(<app>)
```

## Pipeline B — Existing Repos (conform_pipeline)

```text
Existing Django App (working code, no tests)
     ↓
/superjeff:conform <app>    [Audit Agent]
     ↓  git commit: audit(<app>)   ← spec + gap report
Factories                   [Testing Skill]
     ↓  git commit: test(<app>): factories
Characterization Tests      [Characterization Testing Skill — safety net]
     ↓  git commit: test(<app>): characterization tests
     ↓  ALL MUST PASS before touching any code
Refactor Plan               [Planning Skill — 2-5 min tasks, charact. suite after each]
     ↓  git commit: plan(<app>): refactor plan
Refactor                    [Execute plan — security → models → services → FBVs → urls]
     ↓  git commit: refactor(<app>): <task> per task
Architecture Verification   [Verification Skill — grep confirms no CBVs/direct ORM]
Replace Tests               [Testing Skill — proper tests replace characterization]
     ↓  git commit: test(<app>): replace characterization tests
Quality + Security Audit
     ↓  git commit: validate(<app>): conform complete
     ↓
App conforms → continue with Pipeline A for new features
```

## Pipeline C — Existing UI (conform_ui_pipeline)

```text
Existing Django Templates (working UI, no design system)
     ↓
/superjeff:conform-ui <app> [UI Audit Agent]
     ↓  git commit: audit(<app>): UI audit — templates, CSS, HTMX, gap report
Review UI Gaps              Surface critical + high gaps — user acknowledges
Design Tokens               Define token system from existing palette → tokens.css
     ↓  git commit: design(<app>): design token system
Base Template               Fix/create base.html — skip link, landmarks, HTMX
     ↓  git commit: design(<app>): base template
Accessibility Critical      Fix missing labels, alt, keyboard nav (critical gaps)
     ↓  git commit: design(<app>): fix critical accessibility gaps
Empty + Loading States      Add empty states to all lists, hx-indicator everywhere
     ↓  git commit: design(<app>): empty states and loading indicators
HTMX Migration              Replace JS/full-page reloads with HTMX patterns
     ↓  git commit: design(<app>): migrate <feature> from JS to HTMX (per task)
Component Extraction        Extract reusable HTML to named partials
     ↓  git commit: design(<app>): extract reusable partials
Token Application           Replace hardcoded values with var(--token) references
     ↓  git commit: design(<app>): apply design tokens
Verify + Validate
     ↓  git commit: validate(<app>): UI conform complete
     ↓
UI conforms → continue with /superjeff:design for new feature UI
```

---

## What SuperJeff Is Not

- Not a code generator that skips tests
- Not a system that produces vague prose specifications
- Not a monolithic agent trying to do everything
- Not a system that ships without security review
