# SuperJeff

An AI-native software development system that transforms a high-level business case into a fully implementable, tested, and security-audited Django application — using structured multi-agent workflows.

---

## What It Does

**For new projects:**

```text
Business Case (free text)
        ↓
  /superjeff:brainstorm        ← design gate, Socratic questions, design artifact
        ↓
  /superjeff:decompose         ← Django app map (JSON, schema-validated)
        ↓
  /superjeff:specify <app>     ← models, services, views, tests spec (JSON)
        ↓
  /superjeff:design <app>      ← UX spec: design tokens, pages, HTMX patterns, accessibility
        ↓
  /superjeff:build <app>
        ├─ Plan               ← 2-5 min tasks: backend + frontend, exact code, verify commands
        ├─ RED                ← failing tests (pytest + factory_boy)
        ├─ GREEN              ← implement task-by-task (models → services → views → templates)
        ├─ Code Review        ← spec compliance + architecture check
        ├─ Verification Gate  ← fresh pytest + grep, evidence required
        ├─ Quality Audit      ← 5-gate Quality Agent report
        └─ Security Audit     ← OWASP Top 10 Security Agent report
        ↓
  /superjeff:validate          ← final gate across all apps
        ↓
  Production-Ready Django App (backend + HTMX frontend)
```

**For existing repos (working code, no tests):**

```text
Existing Django App (no tests, no service layer)
        ↓
  /superjeff:conform <app>
        ├─ Audit              ← read existing code → spec + gap report
        ├─ Factories          ← factory_boy for all existing models
        ├─ Characterization   ← tests locking current behaviour (safety net)
        ├─ Refactor Plan      ← 2-5 min tasks, characterization suite after each
        ├─ Refactor           ← security → models → services → FBVs → urls
        ├─ Architecture Check ← grep confirms no CBVs, no direct ORM
        ├─ Replace Tests      ← proper tests replace characterization tests
        └─ Quality + Security Audit
        ↓
  App now conforms → use /superjeff:build for new features
```

**For existing repos (working UI, no design system):**

```text
Existing Django Templates (no design tokens, no HTMX, no accessibility baseline)
        ↓
  /superjeff:conform-ui <app> <templates_path>
        ├─ UI Audit           ← read all templates, CSS, JS → existing UX spec + gap report
        ├─ Design Tokens      ← derive token system from existing palette → tokens.css
        ├─ Base Template      ← fix/create base.html (skip link, landmarks, HTMX)
        ├─ Accessibility      ← fix critical gaps (labels, alt, keyboard nav)
        ├─ Empty + Loading    ← empty states for all lists, hx-indicator everywhere
        ├─ HTMX Migration     ← replace JS/full-page reloads with HTMX patterns
        ├─ Component Extract  ← extract reusable HTML to named partials
        └─ Token Application  ← replace hardcoded values with var(--token) references
        ↓
  UI now conforms → use /superjeff:design for new feature UI
```

---

## Commands

| Command | What It Does |
| --- | --- |
| `/superjeff:brainstorm` | Design gate — Socratic validation before planning |
| `/superjeff:decompose` | Business case → structured Django app list |
| `/superjeff:specify <app>` | App definition → full implementation spec |
| `/superjeff:design <app>` | UX spec — design tokens, pages, HTMX patterns, accessibility |
| `/superjeff:build <app>` | Full TDD pipeline: plan → RED → GREEN → review → audit |
| `/superjeff:validate` | Full quality + security audit |
| `/superjeff:conform <app>` | Bring existing app into conformance (audit → refactor → proper tests) |
| `/superjeff:conform-ui <app> <path>` | Bring existing templates into conformance (audit → tokens → HTMX → accessibility) |
| `/superjeff:checkpoint` | Save pipeline state + print progress summary |
| `/superjeff:learn` | Capture a session insight as a permanent instinct rule |

---

## Repository Structure

```text
superjeff/
├── agents/
│   ├── orchestrator/       # Routes tasks, maintains pipeline state
│   ├── product/            # Product Decomposition Agent
│   ├── requirements/       # Requirements Agent (per app)
│   ├── audit/              # Audit Agent — reads existing code, reverse-engineers spec + gaps
│   ├── ui-audit/           # UI Audit Agent — reads templates, CSS, JS → UX spec + gap report
│   ├── frontend/           # Frontend Agent — UX spec with design tokens, HTMX patterns, a11y
│   ├── quality/            # 5-gate quality audit (incl. architecture compliance)
│   └── security/           # OWASP Top 10 security audit agent
│
├── skills/
│   ├── brainstorming/           # Socratic design gate before planning
│   ├── planning/                # 2-5 min subtask breakdown with verify commands
│   ├── testing/                 # TDD workflow (RED→GREEN→REFACTOR)
│   ├── characterization-testing/ # Safety net tests for existing code before refactoring
│   ├── code-review/             # 2-stage review: spec compliance + architecture
│   ├── verification/            # Evidence-before-claims gate (fresh pytest + grep)
│   ├── debugging/               # 4-phase root-cause methodology
│   ├── ux-design/               # UX spec: design tokens, pages, HTMX patterns, accessibility
│   ├── decomposition/           # Business case → domain mapping
│   ├── django/                  # Model/serializer/view generation patterns
│   └── validation/              # Quality and security gate checklists
│
├── workflows/
│   ├── bc_to_apps.yaml          # Decompose workflow
│   ├── app_to_requirements.yaml # Specify workflow
│   ├── build_pipeline.yaml      # Build pipeline v3 — backend + HTMX frontend (10 stages)
│   ├── conform_pipeline.yaml    # Conform pipeline — existing backend code (9 stages)
│   └── conform_ui_pipeline.yaml # Conform UI pipeline — existing templates (9 stages)
│
├── schemas/
│   ├── app_schema.json          # Validates decomposition output
│   ├── requirements_schema.json # Validates requirements output
│   └── api_contract.json        # API contract schema
│
├── instincts/
│   ├── django.yaml              # Django model/view/serializer rules
│   ├── security.yaml            # Security rules + prompt injection + agentic safety
│   ├── testing.yaml             # TDD enforcement rules
│   └── claude-rules-template.md # Generic CLAUDE.md for new projects
│
├── hooks/
│   └── hooks.json               # 16 hooks across 5 lifecycle events
│
├── commands/
│   ├── brainstorm.md    # /superjeff:brainstorm
│   ├── decompose.md     # /superjeff:decompose
│   ├── specify.md       # /superjeff:specify
│   ├── design.md        # /superjeff:design
│   ├── build.md         # /superjeff:build
│   ├── validate.md      # /superjeff:validate
│   ├── conform.md       # /superjeff:conform
│   ├── conform-ui.md    # /superjeff:conform-ui
│   ├── checkpoint.md    # /superjeff:checkpoint
│   └── learn.md         # /superjeff:learn
│
├── examples/
│   └── expense-tracker/   # Full end-to-end example
│
├── artifacts/             # Generated outputs (gitignored)
│
└── SOUL.md                # 6 design principles + git workflow
```

---

## Agents

### Product Decomposition Agent

- **Input**: Business case (free text)
- **Output**: JSON list of Django apps with models, endpoints, and dependencies
- **File**: [agents/product/decomposition-agent.md](agents/product/decomposition-agent.md)

### Requirements Agent

- **Input**: Single app definition from decomposition output
- **Output**: Full spec — models, serializers, views, permissions, business rules, test cases
- **File**: [agents/requirements/requirements-agent.md](agents/requirements/requirements-agent.md)

### Frontend Agent

- **Input**: Requirements Agent output (API contract) + brainstorm design artifact
- **Output**: UX spec — design tokens, page inventory, component library, HTMX patterns, accessibility baseline
- **Stack**: Django templates + HTMX + vanilla JS (HTMX-first)
- **File**: [agents/frontend/frontend-agent.md](agents/frontend/frontend-agent.md)

### Audit Agent

- **Input**: Existing Django app (code path)
- **Output**: Reverse-engineered requirements spec + architecture gap report + characterization test plan
- **File**: [agents/audit/audit-agent.md](agents/audit/audit-agent.md)

### UI Audit Agent

- **Input**: Existing Django app templates + CSS + JS paths
- **Output**: Reverse-engineered UX spec + design gap report + UI refactor plan
- **File**: [agents/ui-audit/ui-audit-agent.md](agents/ui-audit/ui-audit-agent.md)

### Quality Agent

- **Input**: Generated Django code
- **Output**: Structured quality report (test coverage, architecture compliance, conventions)
- **File**: [agents/quality/quality-agent.md](agents/quality/quality-agent.md)

### Security Agent

- **Input**: Generated Django code
- **Output**: OWASP Top 10 security audit report
- **File**: [agents/security/security-agent.md](agents/security/security-agent.md)

### Orchestrator

- **Role**: Routes tasks, validates artifacts, maintains pipeline state
- **File**: [agents/orchestrator/orchestrator.md](agents/orchestrator/orchestrator.md)

---

## Django Rules & Principles

These rules are enforced by the Requirements Agent and the build pipeline. They are defined in [instincts/claude-rules-template.md](instincts/claude-rules-template.md) and applied automatically to every generated Django project.

### Architecture — Layered, Service-First

```text
Views / API      ← HTTP handling only, no business logic
    ↓
Services         ← All business logic lives here
    ↓
Models (ORM)     ← Data definition only, "dumb" models
```

| Rule | Detail |
| --- | --- |
| **Service layer is mandatory** | Every view calls a service method. Direct model queries in views are forbidden. |
| **Services are stateless** | Constructor accepts `user`. Never accepts `request`, `HttpResponse`, or serializer instances. |
| **One service per aggregate root** | Max ~300 lines. Split into sub-services at sync logic, permissions, or side-effects. |
| **N+1 is the service's problem** | `select_related` / `prefetch_related` in service methods, never in views. |

### Views — Function-Based Only

| Rule | Detail |
| --- | --- |
| **FBVs always** | `def my_view(request):` — never `class MyView(APIView)`, never `class MyViewSet(ModelViewSet)` |
| **HTML views** | `@login_required`, in `apps/<app>/views.py`, catch service exceptions → `messages.error()` |
| **API views** | `@api_view` + `@permission_classes`, in `api/v1/views/<app>.py`, `@extend_schema` required |
| **No DRF routers** | Explicit URL paths only in `api/v1/urls.py` |

### Models — Dumb Data Layer

| Rule | Detail |
| --- | --- |
| Always `__str__` | Returns a human-readable identifier |
| Always timestamps | `created_at = auto_now_add`, `updated_at = auto_now` |
| Always UUID PK | `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` on public-facing resources |
| Always `Meta.ordering` | On any model used in a list view |
| No `null=True` on text fields | Use `blank=True, default=""` instead |
| No business logic in models | No business methods, no cross-model queries, no permission logic |

### Serializers

| Rule | Detail |
| --- | --- |
| Never `fields = "__all__"` | Always explicit field list |
| `read_only_fields` | Always includes `id`, `created_at`, `updated_at` |
| No business logic | Only input validation and data mapping |
| No ownership checks | Ownership belongs in services |

### Services

| Rule | Detail |
| --- | --- |
| Location | `apps/<app>/services/<service>.py` |
| Method naming | `create_`, `update_`, `delete_`, `get_`, `can_`, `list_` |
| Transactions | `@transaction.atomic` on multi-write operations |
| Exceptions | Raise from `apps/<app>/exceptions.py` — never raw `Exception` |
| Side effects | Triggered explicitly from services — never from `model.save()` or signals |
| Signals | Django signals only for cache invalidation and auditing, never for business logic |

### Caching & Celery

| Rule | Detail |
| --- | --- |
| Cache backend | Redis via `django.core.cache` |
| Cache key pattern | `<resource>_<user_id>_<params>` |
| Log HIT/MISS | `logger.info()` on every cache access |
| Celery tasks | Only triggered from services — views never call `.delay()` directly |

### What Is Forbidden

- Class-Based Views of any kind
- ViewSets of any kind
- DRF routers
- `fields = "__all__"` in serializers
- Business logic in views, models, or serializers
- Direct model queries in views
- `request.user.is_staff` checks in views
- `eval()`, `exec()`, hardcoded secrets
- Django signals for business logic
- `print()` — use `logging`

---

## Instincts

Behavioral rules loaded by every agent:

- **[instincts/django.yaml](instincts/django.yaml)** — Models always have `__str__`, UUIDs, timestamps. Serializers never use `__all__`. Views always have explicit `permission_classes`.
- **[instincts/security.yaml](instincts/security.yaml)** — No hardcoded secrets. No raw SQL. No `eval()`. JWT tokens must expire.
- **[instincts/testing.yaml](instincts/testing.yaml)** — Tests are written before implementation. Every endpoint has 5+ test cases. Use pytest + factory_boy.
- **[instincts/claude-rules-template.md](instincts/claude-rules-template.md)** — Full CLAUDE.md template applied to every new project: layered architecture, FBV enforcement, service layer, caching, Celery, idempotent migrations, git workflow.

---

## Hooks

Loaded from [hooks/hooks.json](hooks/hooks.json):

### SessionStart

| Hook | Action |
| --- | --- |
| `superjeff:init` | Create artifacts directories, print session context |
| `superjeff:context-load` | Detect Python/Django environment |

### PreToolUse — Security (blocking)

| Hook | Matcher | Action |
| --- | --- | --- |
| `security:no-verify-guard` | Bash | Block `git --no-verify` |
| `security:no-force-push-main` | Bash | Block force push to main/master |
| `security:no-hardcoded-secrets` | Write\|Edit | Block hardcoded credentials |
| `security:no-eval-exec` | Write\|Edit | Block `eval()`/`exec()` |
| `security:no-raw-sql` | Write\|Edit | Warn on raw SQL (ORM required) |

### PreToolUse — Architecture (blocking)

| Hook | Matcher | Action |
| --- | --- | --- |
| `architecture:no-cbv-viewset` | Write\|Edit | Block CBVs, ViewSets — FBV only |
| `architecture:no-fields-all` | Write\|Edit | Block `fields = "__all__"` in serializers |

### PreToolUse — Quality (advisory)

| Hook | Matcher | Action |
| --- | --- | --- |
| `commit:quality-check` | Bash | Warn on `print()` before git commit |
| `security:config-protection` | Write\|Edit | Warn before modifying production settings |

### PostToolUse

| Hook | Matcher | Action |
| --- | --- | --- |
| `superjeff:validate-json-artifacts` | Write | Validate JSON in `artifacts/` |
| `quality:migration-check` | Bash | Remind to run `makemigrations` after model edits |
| `post:bash:command-log` | Bash | Append all commands to `artifacts/bash-audit.log` |

### Stop

| Hook | Action |
| --- | --- |
| `stop:pipeline-state-persist` | Back up `pipeline_state.json` |
| `stop:test-reminder` | Remind to run `pytest` if Python files changed |
| `stop:session-summary` | Print artifact counts for the session |

### PreCompact

| Hook | Action |
| --- | --- |
| `pre:compact:state-save` | Save pipeline state before context compaction |

---

## Example Walkthrough

See [examples/expense-tracker/](examples/expense-tracker/) for a complete end-to-end run:

1. [01_business_case.txt](examples/expense-tracker/01_business_case.txt) — Input business case
2. [02_decomposition_output.json](examples/expense-tracker/02_decomposition_output.json) — 7 Django apps decomposed
3. [03_requirements_expenses_app.json](examples/expense-tracker/03_requirements_expenses_app.json) — Full spec for the `expenses` app

---

## Design Philosophy

See [SOUL.md](SOUL.md) for the six principles:

1. **Agent-First** — Route to a specialist. Never implement generically.
2. **Test-Driven** — RED before GREEN. Always.
3. **Security-First** — Validation is a design constraint, not a QA gate.
4. **Structured Output** — JSON or YAML. Never prose.
5. **Plan Before Execute** — No implementation without a completed spec.
6. **Commit Every Stage** — Every pipeline stage produces a git commit. A stage without a commit did not happen.

---

## Inspiration

- [obra/superpowers](https://github.com/obra/superpowers) — plan→execute flow, TDD mindset, subtask breakdown
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — instincts, hooks, security checks, workflow commands
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) — role descriptions, output formats
