# SuperJeff

An AI-native software development system that transforms a high-level business case into a fully implementable, tested, and security-audited Django application — using structured multi-agent workflows.

---

## What It Does

```text
Business Case (free text)
        ↓
  /superjeff:decompose
        ↓
  Django App Map (JSON)
        ↓
  /superjeff:specify <app>
        ↓
  Implementation-Ready Spec (JSON)
        ↓
  /superjeff:build <app>
        ↓
  TDD: Tests → Code → Refactor → Security Review
        ↓
  /superjeff:validate
        ↓
  Production-Ready Django App
```

---

## Commands

| Command | What It Does |
| --- | --- |
| `/superjeff:decompose` | Business case → structured Django app list |
| `/superjeff:specify <app>` | App definition → full implementation spec |
| `/superjeff:build <app>` | Spec → TDD build pipeline |
| `/superjeff:validate` | Full quality + security audit |

---

## Repository Structure

```text
superjeff/
├── agents/
│   ├── orchestrator/       # Routes tasks, maintains pipeline state
│   ├── product/            # Product Decomposition Agent
│   ├── requirements/       # Requirements Agent (per app)
│   ├── frontend/           # User flow + component spec agent
│   ├── quality/            # Quality + accessibility audit agent
│   └── security/           # OWASP Top 10 security audit agent
│
├── skills/
│   ├── decomposition/      # Business case → domain mapping
│   ├── django/             # Model/serializer/view generation patterns
│   ├── testing/            # TDD workflow (RED→GREEN→REFACTOR)
│   └── validation/         # Quality and security gate checklists
│
├── workflows/
│   ├── bc_to_apps.yaml         # Decompose workflow
│   ├── app_to_requirements.yaml # Specify workflow
│   └── build_pipeline.yaml     # Build + validate workflow
│
├── schemas/
│   ├── app_schema.json          # Validates decomposition output
│   ├── requirements_schema.json # Validates requirements output
│   └── api_contract.json        # API contract schema
│
├── instincts/
│   ├── django.yaml    # Django model/view/serializer rules
│   ├── security.yaml  # Security enforcement rules
│   └── testing.yaml   # TDD enforcement rules
│
├── hooks/
│   └── hooks.json     # Pre/PostToolUse + SessionStart hooks
│
├── commands/
│   ├── decompose.md
│   ├── specify.md
│   ├── build.md
│   └── validate.md
│
├── examples/
│   └── expense-tracker/   # Full end-to-end example
│
├── artifacts/             # Generated outputs (gitignored)
│
└── SOUL.md                # Design principles
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

### Quality Agent

- **Input**: Generated Django code
- **Output**: Structured quality report (test coverage, conventions, accessibility)
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

See [SOUL.md](SOUL.md) for the five principles:

1. **Agent-First** — Route to a specialist. Never implement generically.
2. **Test-Driven** — RED before GREEN. Always.
3. **Security-First** — Validation is a design constraint, not a QA gate.
4. **Structured Output** — JSON or YAML. Never prose.
5. **Plan Before Execute** — No implementation without a completed spec.

---

## Inspiration

- [obra/superpowers](https://github.com/obra/superpowers) — plan→execute flow, TDD mindset, subtask breakdown
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — instincts, hooks, security checks, workflow commands
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) — role descriptions, output formats
