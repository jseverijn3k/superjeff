# AutoResearch Program — <app_name>

## Instructions
Fill in the sections below and save this file to:
  artifacts/autoresearch/<app_name>/program.md

Then run: /superjeff:autoresearch <app_name>

---

## Configuration

app_name: <app_name>
base_url: http://localhost:8000

urls:
- /<app_name>/
- /<app_name>/detail/

## Goal

Improve end-user performance of the <app_name> app.
Fitness = 60% backend (query count + response time) + 40% frontend (Lighthouse).

## What you may change

- views.py — add select_related, prefetch_related, only(), caching
- services.py — optimize queries, add caching layer
- templates — reduce DOM complexity, lazy-load images, defer scripts
- middleware — add response caching headers
- urls.py — no structural changes, only ordering

## What you must NOT change

- models.py
- migrations/
- settings.py secrets
- Any file outside this app directory

## Constraints

- Every iteration must leave all pytest tests green
- Combined fitness score must be >= previous iteration to KEEP
- One targeted change per iteration — no sweeping refactors
- Prefer the smallest change that measurably improves the score

## Agent Notes

Start by measuring the baseline score before proposing any changes.
Log the baseline as iteration 0 in log.json.
Then propose the single most impactful hypothesis first.
