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

## Instincts

Behavioral rules loaded by every agent:

- **[instincts/django.yaml](instincts/django.yaml)** — Models always have `__str__`, UUIDs, timestamps. Serializers never use `__all__`. Views always have explicit `permission_classes`.
- **[instincts/security.yaml](instincts/security.yaml)** — No hardcoded secrets. No raw SQL. No `eval()`. JWT tokens must expire.
- **[instincts/testing.yaml](instincts/testing.yaml)** — Tests are written before implementation. Every endpoint has 5+ test cases. Use pytest + factory_boy.

---

## Hooks

Loaded from [hooks/hooks.json](hooks/hooks.json):

| Hook | Event | Action |
| --- | --- | --- |
| `superjeff:init` | SessionStart | Create artifacts directories |
| `security:no-verify-guard` | PreToolUse (Bash) | Block `git --no-verify` |
| `security:no-force-push-main` | PreToolUse (Bash) | Block force push to main |
| `security:no-eval-exec` | PreToolUse (Write) | Warn on `eval()`/`exec()` |
| `security:no-hardcoded-secrets` | PreToolUse (Write) | Block hardcoded secrets |
| `superjeff:validate-json-output` | PostToolUse (Write) | Validate JSON in artifacts/ |
| `superjeff:pipeline-state-persist` | Stop | Backup pipeline state |

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
