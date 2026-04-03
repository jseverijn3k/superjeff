---
name: conform-ui
command: /superjeff:conform-ui
description: Bring existing Django templates into SuperJeff UI conformance — audit, design tokens, accessibility fixes, HTMX migration, component extraction
input: App name + templates path (e.g. expenses templates/expenses/)
output: Conformed UI with design tokens, HTMX patterns, empty/loading states, and accessibility baseline
workflow: workflows/conform_ui_pipeline.yaml
---

## Purpose

For existing Django apps that have working templates but don't follow SuperJeff UI conventions. Runs a structured UI conform pipeline that is safe for production repos: it audits first, then makes incremental changes in severity order, verifying at each step.

The backend equivalent is `/superjeff:conform`. Run both on existing apps — backend first, then UI.

## Usage

```
/superjeff:conform-ui <app_name> <templates_path> [static_path]
```

Examples:
```
/superjeff:conform-ui expenses templates/expenses/
/superjeff:conform-ui expenses apps/expenses/templates/expenses/ apps/expenses/static/expenses/
```

## What Happens (9 stages)

```
1. UI Audit         Read all templates, CSS, JS → existing UX spec + gap report + refactor plan
                    git commit: audit(expenses): UI audit — templates, CSS, HTMX usage, gap report

2. Review Gaps      Surface critical + high gaps — must acknowledge before continuing

3. Design Tokens    Define token system from existing palette, generate tokens.css
                    git commit: design(expenses): define design token system

4. Base Template    Fix/create base.html — skip link, landmarks, HTMX, tokens CSS linked
                    git commit: design(expenses): base template

5. Accessibility    Fix critical accessibility gaps (missing labels, alt, keyboard nav)
                    git commit: design(expenses): fix critical accessibility gaps

6. Empty + Loading  Add empty states to all lists, hx-indicator to all HTMX requests
                    git commit: design(expenses): add empty states and loading indicators

7. HTMX Migration   Replace JS/full-page reloads with HTMX patterns (per task commits)
                    git commit: design(expenses): migrate <feature> from JS to HTMX

8. Component Extract Extract reusable HTML into named partials in templates/<app>/partials/
                    git commit: design(expenses): extract reusable partials

9. Token Application Replace hardcoded colors/spacing with var(--token) references
                    git commit: design(expenses): apply design tokens

10. Verify + Validate Final gate: all gaps resolved, tokens applied, accessibility baseline met
                    git commit: validate(expenses): UI conform complete
```

## What Makes This Safe for Existing Templates

**Audit first, always.** You cannot safely refactor templates without knowing what exists. The UI Audit Agent reads everything before touching anything.

Changes are made in severity order:
1. Critical accessibility (no visual change)
2. Design tokens (additive — define system, apply incrementally)
3. Empty/loading states (additive — new HTML only)
4. HTMX migration (replace JS, verify each replacement before committing)
5. Component extraction (structural refactor — visual result identical)
6. Token application (find-and-replace — visual result identical)

Every step verifies with grep before committing.

## When to Run Per App vs All at Once

Run per app. Conform one app's UI, validate it, then move to the next. Start with the most visible app (usually the main dashboard or list views).

## Design Token Philosophy

The token system derives from your existing palette — it doesn't impose a new look. If your app uses `#2563EB` as its primary blue, that becomes `--color-primary: #2563EB`. Nothing changes visually; the architecture becomes consistent.

Tokens are defined once in `static/<app>/css/tokens.css` and referenced everywhere else.

## HTMX Migration Strategy

The pipeline replaces JS patterns with HTMX equivalents in order of impact:

| Current pattern | HTMX replacement |
| --- | --- |
| `fetch()` / `$.ajax()` for list data | `hx-get` + `hx-target` |
| Form submit via `$.ajax()` | `hx-post` + `hx-target` |
| Search filtering on keyup | `hx-trigger="keyup changed delay:300ms"` |
| Delete with JS confirm | `hx-confirm` attribute |
| Tab switching with JS | `hx-get` + `hx-push-url` |
| Show/hide with JS | `hx-get` returning partial |

JS is only kept if HTMX genuinely cannot replace it (drag-and-drop, browser APIs).

## After Conform-UI

The app's UI is now conform:

```
/superjeff:design expenses    ← design new feature UI (uses existing token system)
/superjeff:build expenses     ← builds backend + frontend together
```

## Failure Modes

| Error | Cause | Resolution |
| --- | --- | --- |
| `missing_base_template` | No shared base template exists | Create templates/base.html from scratch |
| `htmx_not_installed` | HTMX script not in base template | Add CDN link to base.html |
| `broken_template_after_partial_extraction` | Include path wrong | Check template directory structure |
| `contrast_ratio_failure` | Existing color fails WCAG AA | Darken text or lighten background until ≥ 4.5:1 |
| `js_replacement_breaks_feature` | HTMX replacement not equivalent | Revert JS, document as js_requirement in UX spec |
