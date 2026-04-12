---
name: autoresearch
command: /superjeff:autoresearch
description: Run autonomous performance research loop on a Django app
input: App name (must have artifacts/autoresearch/<app>/program.md)
output: artifacts/autoresearch/<app>/log.json — iteration log with scores and decisions
agent: agents/autoresearch/autoresearch-agent.md
---

## Purpose

Runs an autonomous experiment loop on a Django app, inspired by Karpathy's autoresearch.
The agent proposes one change per iteration, measures fitness (60% backend / 40% Lighthouse),
and keeps or discards based on two safety gates: tests green AND score improved.

## Usage

```
/superjeff:autoresearch <app_name>
```

Example:
```
/superjeff:autoresearch expenses
```

## Prerequisites

1. Copy the template and fill it in:
   ```
   cp templates/autoresearch.md artifacts/autoresearch/<app>/program.md
   ```
2. Edit `artifacts/autoresearch/<app>/program.md`:
   - Set `app_name`
   - Set `base_url` (your running dev server)
   - List the `urls` to measure
3. Start your Django dev server (needed for Lighthouse measurement)
4. Install Lighthouse: `npm install -g lighthouse`

## What the Agent May Change

- views.py
- services.py
- templates/
- Any middleware in the target app

## What the Agent Will Never Touch

- models.py
- migrations/
- settings.py
- Files outside the target app

## Safety Gates

Both must pass for a change to be KEPT:
1. All pytest tests remain green
2. Combined fitness score >= previous iteration score

If either fails: git checkout (full discard), log entry written, next iteration begins.

## Fitness Score

```
score = 0.6 * backend_score + 0.4 * frontend_score

backend_score  = f(query_count, p95_response_time_ms)  [0-100, higher=better]
frontend_score = Lighthouse performance score           [0-100, higher=better]
```

## Output

```
artifacts/autoresearch/<app>/log.json   — full iteration log
git log                                 — one commit per KEEP, message: autoresearch(<app>): iteration N — score X.XX
```

## Running Autonomously (recommended)

```
/loop /superjeff:autoresearch <app_name>
```

Start it before you go to sleep. In the morning, review:
```
git log --oneline | grep autoresearch
cat artifacts/autoresearch/<app>/log.json
```

## Dependencies

Python:
- pytest (already in SuperJeff)
- No additional Python deps required

npm (one-time install):
```
npm install -g lighthouse
```

Playwright (for Lighthouse in CI):
```
pip install playwright && playwright install chromium
```

## Next Step

After an autoresearch session, run `/superjeff:validate <app>` to verify all gains
are stable and no regressions were introduced.
