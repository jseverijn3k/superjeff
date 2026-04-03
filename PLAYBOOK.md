# SuperJeff Playbook

When to use which pipeline, command, and agent — and in what order.

---

## Decision Tree

```
Do you have existing code?
│
├─ NO  → New project
│         Go to: New Project Flow
│
└─ YES → Does the code have tests?
          │
          ├─ NO  → Run /superjeff:conform <app> first
          │         Go to: Existing Backend Flow
          │
          └─ YES → Does it follow SuperJeff architecture?
                    │
                    ├─ NO  → Run /superjeff:conform <app> first
                    │         Go to: Existing Backend Flow
                    │
                    └─ YES → Ready for new features
                              Go to: New Feature Flow
```

---

## New Project Flow

**Start here when:** you have a business case and no existing code.

```
Step 1   /superjeff:brainstorm
         → Socratic design gate. Answer the questions one by one.
         → Produces: artifacts/specs/YYYY-MM-DD-<feature>.md
         → Commit: design(<project>): brainstorm artifact

Step 2   /superjeff:decompose
         → Breaks business case into Django apps with models and endpoints.
         → Produces: artifacts/decomposition/<project>.json
         → Commit: decompose(<project>): N apps

Step 3   /superjeff:specify <app>        ← repeat per app
         → Full spec: models, serializers, views, permissions, test cases.
         → Produces: artifacts/requirements/<app>.json
         → Commit: specify(<app>): full spec

Step 4   /superjeff:design <app>         ← repeat per app (skip for API-only apps)
         → UX spec: design tokens, pages, HTMX patterns, accessibility.
         → Produces: artifacts/ux/<app>_ux_spec.json
         → Commit: design(<app>): UX spec

Step 5   /superjeff:build <app>          ← repeat per app
         → Full TDD pipeline: plan → RED → GREEN → review → audit
         → Includes frontend tasks if UX spec exists
         → Commits: plan, test, implement, refactor, secure, validate

Step 6   /superjeff:validate             ← once, across all apps
         → 4-domain peer review: architecture, security, UX, tests
         → Blocks on critical/high findings
```

---

## Existing Backend Flow

**Start here when:** you have working Django code but no tests, or the architecture doesn't follow SuperJeff conventions (CBVs, direct ORM in views, no service layer).

```
Step 1   /superjeff:conform <app>        ← repeat per app, most independent first
         → Audit → characterization tests → refactor → proper tests → validate
         → Safe for production: characterization tests lock behaviour first
         → Commits: audit, test (factories), test (characterization),
                    plan, refactor (per task), test (replace), validate

Step 2   /superjeff:validate <app>
         → Confirm the app passes all 4 audit domains
         → If UI also needs work: continue to Existing UI Flow

Step 3   → Continue with New Feature Flow
```

**Order matters:** start with the app that has the fewest dependencies on other apps.

---

## Existing UI Flow

**Start here when:** you have working Django templates but no design system, no HTMX, or accessibility gaps.

```
Step 1   /superjeff:conform-ui <app> <templates_path>
         → UI audit → design tokens → base template → accessibility →
           empty/loading states → HTMX migration → component extraction →
           token application → validate
         → Commits: audit, design (tokens), design (base), design (a11y),
                    design (states), design (htmx per task), design (partials),
                    design (tokens applied), validate

Step 2   /superjeff:validate <app> --domain ux
         → Confirm UX compliance passes

Step 3   → Continue with New Feature Flow
```

---

## New Feature Flow

**Start here when:** the backend conforms and you want to add a feature to an existing app.

```
Step 1   /superjeff:brainstorm           ← for significant features only
         → Skip for bug fixes, minor additions, pure config changes

Step 2   /superjeff:specify <app>
         → Generates spec for the new feature (extends existing spec)

Step 3   /superjeff:design <app>         ← skip for backend-only changes
         → Updates UX spec with new pages/components

Step 4   /superjeff:build <app>
         → Builds the feature on top of the existing conformed app

Step 5   /superjeff:validate <app>
         → Peer review gate before merge
```

---

## When to Run Each Command

| Command | Run when | Skip when |
| --- | --- | --- |
| `/superjeff:brainstorm` | New significant feature | Bug fix, minor field addition, pure config |
| `/superjeff:decompose` | New project from scratch | Adding feature to existing app |
| `/superjeff:specify <app>` | Any new feature or app | Pure UI change with no model/API changes |
| `/superjeff:design <app>` | New pages or components needed | API-only app, backend-only change |
| `/superjeff:build <app>` | After spec (and optionally design) are ready | Never skip — this is the implementation pipeline |
| `/superjeff:conform <app>` | Existing code without tests or with wrong architecture | App already conforms (check with `/superjeff:validate`) |
| `/superjeff:conform-ui <app>` | Existing templates without design system or HTMX | App has no templates (API-only), or UI already conforms |
| `/superjeff:validate` | Before every merge, after every build/conform | Never skip |
| `/superjeff:checkpoint` | Long sessions, before switching apps | Not needed for short sessions |
| `/superjeff:learn` | You discover a pattern or anti-pattern worth keeping | Routine work |

---

## When to Run Each Agent

Agents run automatically inside pipelines. You do not invoke them directly — the commands and workflows route to them. This table shows which agent does what, for reference.

| Agent | Invoked by | What it audits |
| --- | --- | --- |
| Product Decomposition | `/superjeff:decompose` | Business case → Django app list |
| Requirements | `/superjeff:specify` | App definition → full backend spec |
| Frontend | `/superjeff:design` | Requirements + design artifact → UX spec |
| Audit | `/superjeff:conform` | Existing backend code → spec + gap report |
| UI Audit | `/superjeff:conform-ui` | Existing templates + CSS + JS → UX gap report |
| Quality | `/superjeff:build`, `/superjeff:validate` | Architecture compliance, test coverage, conventions |
| Security | `/superjeff:build`, `/superjeff:validate` | OWASP Top 10 |
| UX Compliance | `/superjeff:validate` (if UX spec exists) | Implementation vs. UX spec |
| Orchestrator | All pipelines | Routes tasks, validates artifacts, maintains state |

---

## The Four Audit Domains

Every `/superjeff:validate` run covers four independent perspectives:

### 1. Architecture

**Agent:** Quality Agent (Gates 1, 3, 4, 5)
**What it checks:**

- Service layer mandatory — no direct ORM in views
- FBV only — no CBVs, no ViewSets, no DRF routers
- Dumb models — no business logic, no cross-model queries
- Serializers — no `__all__`, correct `read_only_fields`
- Exceptions — domain exceptions in `exceptions.py`, not raw `Exception`
- Caching — Redis, correct key pattern, HIT/MISS logged
- Celery — tasks only triggered from services
- Migrations — idempotent, `SeparateDatabaseAndState` for raw SQL

**Blocks on:** any critical or high finding.

### 2. Security

**Agent:** Security Agent
**What it checks:**

- Access control — explicit `permission_classes`, object-level, no `AllowAny` on writes
- Injection — ORM only, no raw SQL, no `eval()`/`exec()`
- Authentication — JWT expiry, token rotation, single-use reset tokens
- Secrets — no hardcoded credentials, `SECRET_KEY` from environment
- Configuration — `DEBUG=False`, explicit `ALLOWED_HOSTS`, CSRF/CORS configured
- Logging — auth events logged, no sensitive data in logs

**Blocks on:** any critical finding, or 2+ high findings.

### 3. UX Compliance

**Agent:** UX Compliance Agent
**What it checks (against `artifacts/ux/<app>_ux_spec.json`):**

- Design tokens — `tokens.css` exists, no hardcoded hex colors in templates
- Pages — all pages implemented, correct layout, 4 states per page
- Components — all states implemented (loading/empty/error/populated)
- HTMX — every request has `hx-indicator`, every target has `aria-live`
- Forms — all fields present, all have `<label>`, error display matches spec
- HTMX patterns — live-search has `delay:`, infinite-scroll uses `revealed`, etc.
- Accessibility — skip link, main landmark, no `outline: none`

**Blocks on:** any critical finding, or 2+ high findings.
**Skips:** if no UX spec exists (API-only app).

### 4. Test Coverage

**Agent:** Quality Agent (Gate 2)
**What it checks:**

- Test files exist: `test_models.py`, `test_services.py`, `test_views.py`, `test_api.py`
- pytest used — no `unittest.TestCase` subclasses
- factory_boy used — no `Model.objects.create()` in test bodies
- Every endpoint has 5 test cases: success / 401 / 403 / 400 / 404
- Every service method has a unit test
- Tests are isolated — no shared mutable state

**Blocks on:** missing test files, fewer than 5 test cases per endpoint.

---

## Pipeline Reference

| Pipeline | Command | Stages | Use for |
| --- | --- | --- | --- |
| `build_pipeline` | `/superjeff:build <app>` | plan → RED → GREEN → review → verify → quality → security → validate | New features from spec |
| `conform_pipeline` | `/superjeff:conform <app>` | audit → factories → characterization → plan → refactor → arch check → replace tests → quality → validate | Existing backend without tests |
| `conform_ui_pipeline` | `/superjeff:conform-ui <app> <path>` | audit → tokens → base template → a11y → empty/loading → HTMX → partials → token apply → validate | Existing templates without design system |
| (standalone) | `/superjeff:validate <app>` | architecture → security → UX → tests | Pre-merge peer review gate |

---

## Commit Type Reference

Every pipeline stage produces a git commit. The commit type signals which stage it came from.

| Type | Stage |
| --- | --- |
| `design` | Brainstorm artifact saved, or UX spec produced |
| `decompose` | Product Decomposition Agent output |
| `specify` | Requirements Agent output |
| `plan` | Implementation task plan produced |
| `test` | Tests written (RED phase, factories, characterization, replacement) |
| `implement` | Implementation passes tests (GREEN phase) |
| `refactor` | Code review fixes, Quality Agent fixes |
| `secure` | Security Agent fixes |
| `audit` | Audit Agent or UI Audit Agent output |
| `validate` | Final validation gate passed |

---

## Artifact Reference

All generated files land in `artifacts/`. Gitignored by default — the code that implements them is what gets committed.

```
artifacts/
├── specs/                        ← brainstorm design artifacts
│   └── YYYY-MM-DD-<feature>.md
├── decomposition/                ← product decomposition output
│   └── <project>.json
├── requirements/                 ← per-app specs
│   └── <app>.json
├── ux/                           ← UX specs and design tokens
│   ├── <app>_ux_spec.json
│   ├── <app>_design_tokens.json
│   └── <app>_existing_ux.json   ← from conform-ui audit
├── plans/                        ← implementation task plans
│   ├── <app>_plan.md
│   ├── <app>_refactor_plan.md
│   ├── <app>_characterization_plan.md
│   └── <app>_ui_refactor_plan.md
├── reports/                      ← all audit outputs
│   ├── <app>_quality.json
│   ├── <app>_security.json
│   ├── <app>_ux_compliance.json
│   ├── <app>_ui_gaps.json
│   ├── <app>_gaps.json
│   ├── <app>_code_review.json
│   └── validation_summary.json
└── bash-audit.log                ← all commands executed (hook)
```
