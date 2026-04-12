# AutoResearch — How to Use in Your Projects

AutoResearch runs an autonomous performance optimization loop on any Django app.
Inspired by Karpathy's autoresearch: the agent proposes one change, measures the result,
and keeps or discards — while you sleep.

---

## What It Does

Each iteration:
1. Proposes one targeted change (queries, caching, templates, middleware)
2. Runs your full pytest suite — if tests fail, discards immediately
3. Measures performance: 60% backend (query count + p95 response time) + 40% Lighthouse score
4. Commits if score improves, discards if not
5. Logs every iteration to `artifacts/autoresearch/<app>/log.json`
6. Repeats

You wake up to a git log of improvements, each one tested and measured.

---

## Prerequisites

Install once on your machine:

```bash
# Lighthouse (required for frontend score)
npm install -g lighthouse

# Playwright + Chromium (required for headless Lighthouse)
pip install playwright
playwright install chromium
```

---

## Setup Per Project

### Step 1 — Add autoresearch to your project's CLAUDE.md

In your Django project root, open or create `CLAUDE.md` and add:

```
@~/superjeff/agents/autoresearch/autoresearch-agent.md
```

This makes the agent available in that project's Claude Code session.

### Step 2 — Create a program.md for the app you want to optimize

```bash
mkdir -p artifacts/autoresearch/<your_app>
cp ~/superjeff/templates/autoresearch.md artifacts/autoresearch/<your_app>/program.md
```

Then edit `artifacts/autoresearch/<your_app>/program.md`:

```markdown
app_name: expenses
base_url: http://localhost:8000

urls:
- /expenses/
- /expenses/reports/
- /expenses/submit/
```

Fill in:
- `app_name` — your Django app label (must match `INSTALLED_APPS`)
- `base_url` — your running dev server URL
- `urls` — the pages that matter most for end-user performance

### Step 3 — Start your dev server

Lighthouse needs a running server to audit. In a separate terminal:

```bash
python manage.py runserver
```

### Step 4 — Run the loop

```bash
/loop /superjeff:autoresearch <your_app>
```

Or for a single iteration (to test the setup):

```bash
/superjeff:autoresearch <your_app>
```

---

## In the Morning

Check what the agent improved:

```bash
# See all commits from last night
git log --oneline | grep autoresearch

# See the full iteration log with scores
cat artifacts/autoresearch/<your_app>/log.json

# See what code changed
git diff HEAD~5 HEAD -- <your_app>/
```

Example log output:

```json
[
  {
    "iteration": 1,
    "timestamp": "2026-04-12T23:14:02+00:00",
    "hypothesis": "Add select_related('owner') to ExpenseReport queryset to eliminate N+1",
    "diff_summary": "expenses/views.py",
    "backend_score": 81.2,
    "frontend_score": 74.0,
    "combined_score": 78.3,
    "tests_passed": true,
    "decision": "KEEP",
    "git_commit": "a3f91bc"
  },
  {
    "iteration": 2,
    "timestamp": "2026-04-12T23:21:18+00:00",
    "hypothesis": "Add cache_page(60) to reports view",
    "diff_summary": "expenses/views.py",
    "backend_score": 79.1,
    "frontend_score": 74.0,
    "combined_score": 77.1,
    "tests_passed": true,
    "decision": "DISCARD",
    "git_commit": null
  }
]
```

---

## What the Agent May Change

| Target | Examples |
|---|---|
| `views.py` | `select_related`, `prefetch_related`, `only()`, `cache_page` |
| `services.py` | Query optimization, `cache.set()` / `cache.get()` |
| `templates/` | Reduce DOM nodes, lazy-load images, defer scripts |
| `middleware` | Cache-Control headers |
| `urls.py` | Ordering only — no structural changes |

## What the Agent Will Never Touch

- `models.py` — no field changes, no schema changes
- `migrations/` — no database changes
- Files outside the target app
- Authentication or permissions

---

## Safety Gates

A change is only KEPT if **both** conditions are true:

1. All pytest tests pass
2. Combined fitness score >= previous iteration score

If either fails, the change is discarded via `git checkout` and the loop continues.

---

## Fitness Score Reference

```
score = 0.6 × backend_score + 0.4 × frontend_score

backend_score  = f(query_count, p95_response_time_ms)  — 0 to 100, higher is better
frontend_score = Lighthouse performance score           — 0 to 100, higher is better
```

Backend scoring rules:
- 0 queries → 100 points for query dimension
- Each additional query reduces the score
- Faster p95 response time → higher time dimension score

---

## Multiple Apps in One Project

Run separate loops per app. Each has its own `program.md` and `log.json`.

```bash
# Terminal 1
/loop /superjeff:autoresearch expenses

# Terminal 2 (separate Claude Code session)
/loop /superjeff:autoresearch reports
```

---

## Multiple Projects

AutoResearch is project-local. For each Django project:

1. The `artifacts/autoresearch/` directory lives in that project's repo
2. The `program.md` is specific to that project's URLs and app structure
3. The `log.json` accumulates over time — commit it to track progress

The `autoresearch/measure_fitness.py` utility and agent live in SuperJeff (`~/superjeff/`)
and are shared across all your projects — no copying needed.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `No program.md found` | program.md not created yet | `cp ~/superjeff/templates/autoresearch.md artifacts/autoresearch/<app>/program.md` |
| `lighthouse: command not found` | Lighthouse not installed | `npm install -g lighthouse` |
| `frontend score always 0` | Dev server not running | `python manage.py runserver` in separate terminal |
| `app_name must be alphanumeric` | Typo or slash in app name | Use only letters, digits, underscores |
| Loop keeps discarding | Baseline too high or changes too broad | Check `log.json` — baseline score may need recalibration |
| Tests fail immediately | Existing test suite broken before loop starts | Fix tests first, then run autoresearch |

---

## After a Session

Run the validate command to confirm all gains are stable:

```bash
/superjeff:validate <your_app>
```

This runs the full 4-domain audit — architecture, security, UX compliance, test coverage —
on top of whatever autoresearch improved.
