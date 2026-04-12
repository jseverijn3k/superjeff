# Design: AutoResearch voor SuperJeff

## Problem Statement

SuperJeff heeft geen mechanisme om autonoom te experimenteren met performance-verbeteringen in bestaande Django-apps — een developer moet elke optimalisatie handmatig identificeren, implementeren en meten.

## Approach

Een nieuw command `/superjeff:autoresearch <app>` dat een autonome experimentloop uitvoert op een bestaande Django-app. De loop leest een `autoresearch.md` per app (equivalent van Karpathy's `program.md`), maakt één wijziging tegelijk in views/services/templates/caching/middleware, meet een gecombineerde fitness score, en commit of discardt via git.

**Fitness score = 60% backend + 40% frontend**
- Backend: query count + response time via pytest + django-assert-num-queries
- Frontend: Lighthouse score via headless Chrome (Playwright)

**Veiligheidsgates (AND-conditie):**
1. Alle bestaande pytest tests blijven groen
2. Gecombineerde fitness score groter dan of gelijk aan vorige iteratie

**Loop-modus:** volledig autonoom via `/loop` skill — start, ga slapen, 's ochtends zie je git log met iteraties.

## Key Decisions

- **Één command, niet vijf** — de `autoresearch.md` per app definieert het doel, niet het command
- **Git als keep/discard mechanisme** — verbeterd = commit, verslechterd = git checkout
- **Datamodel is off-limits** — geen migraties in de loop, te onomkeerbaar
- **Tests als harde gate** — SuperJeff's test-driven principe is niet onderhandelbaar, ook niet voor performance

## Data Model Changes

Geen. Datamodel wijzigingen zijn expliciet out of scope.

## Service Layer Changes

Nieuwe `autoresearch/measure_fitness.py` utility:
- `measure_backend(app)` — query count + p95 response time — score 0-100
- `measure_frontend(url)` — Playwright + Lighthouse — score 0-100
- `combined_score(backend, frontend, weights=(0.6, 0.4))` — één getal

## New Files

```
commands/autoresearch.md
agents/autoresearch/autoresearch-agent.md
templates/autoresearch.md
artifacts/autoresearch/<app>/program.md
artifacts/autoresearch/<app>/log.json
autoresearch/measure_fitness.py
```

## API Changes

Geen nieuwe endpoints.

## Out of Scope

- Datamodel wijzigingen / migraties
- Wijzigingen buiten de target app
- Multi-app loops in één run
- Dependency upgrades
- Semi-autonoom of per-iteratie review mode

## Risks

- Lighthouse vereist een draaiende dev-server — opstarten/neerhalen per iteratie voegt complexiteit toe
- Playwright + Chrome dependency buiten de normale SuperJeff stack
- Een autonome agent die middleware aanpast kan de app onbereikbaar maken — fitness-meting faalt dan, discard volgt automatisch, maar de loop kan vastlopen
- autoresearch.md kwaliteit bepaalt de kwaliteit van experimenten — garbage in, garbage out
