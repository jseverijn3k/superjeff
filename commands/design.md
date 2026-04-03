---
name: design
command: /superjeff:design
description: Produce a UX spec for a Django + HTMX app — design tokens, page inventory, component library, HTMX patterns, and accessibility baseline
input: App name (e.g. expenses)
output: artifacts/ux/<app>_ux_spec.json
workflow: workflows/build_pipeline.yaml (design stage)
---

## Purpose

Transforms the brainstorm design artifact and Requirements Agent output into a structured UX spec: design tokens, page layouts, component states, HTMX interaction patterns, and accessibility requirements. This is the bridge between "what the app does" (spec) and "how it looks and behaves" (implementation).

Run this after `/superjeff:specify <app>` and before `/superjeff:build <app>`.

## Usage

```
/superjeff:design <app_name>
```

Example:
```
/superjeff:design expenses
```

## What Happens

```
1. Read inputs
   - artifacts/specs/YYYY-MM-DD-<feature>.md      (brainstorm design artifact)
   - artifacts/requirements/<app>.json             (Requirements Agent output)
   - artifacts/ux/<app>_ux_spec.json               (existing spec, if any)

2. Design tokens
   - Define color palette (semantic names, contrast checked)
   - Type scale, spacing scale, border radius, shadows, breakpoints

3. Page inventory
   - Every page the app needs
   - Each page: layout, sections, 4 states (loading/empty/error/populated)
   - Accessibility: skip link, landmark regions, page title pattern

4. Component library
   - Every reusable partial: type, template path, 4 states, HTMX attributes
   - Accessibility: aria labels, keyboard navigation, focus management

5. Forms
   - Every field mapped to serializer field
   - Submission method: htmx|standard
   - Error display: inline|summary|toast
   - On-success behavior: redirect|replace|toast

6. HTMX patterns
   - Which patterns apply: live-search, infinite-scroll, inline-edit, etc.
   - Implementation notes per pattern

7. JS requirements (only if HTMX cannot do it)
   - Feature, reason HTMX insufficient, vanilla JS approach

8. Save artifact
   git commit: design(<app>): UX spec — <N> pages, <N> components, design tokens
```

## Output File

```
artifacts/ux/<app>_ux_spec.json
```

This file is consumed by:
- The Planning Skill (implementation tasks reference component templates and HTMX attributes)
- The Testing Skill (accessibility assertions, HTMX behavior tests)
- The Verification Skill (visual + interaction verification)

## Design Token Philosophy

Tokens are set once in the UX spec and referenced everywhere. Never hardcode colors or spacing in templates — always reference the token.

A good token set for a business app:

| Token | Value | Use |
| --- | --- | --- |
| `primary` | `#2563EB` | CTAs, active states, links |
| `surface` | `#FFFFFF` | Cards, panels, modals |
| `background` | `#F9FAFB` | Page background |
| `border` | `#E5E7EB` | Dividers, input borders |
| `text_primary` | `#111827` | Body text |
| `text_muted` | `#6B7280` | Labels, help text |
| `danger` | `#DC2626` | Errors, destructive actions |
| `success` | `#16A34A` | Confirmations |

## HTMX-First Rule

Every interaction is HTMX unless it physically cannot be. Common patterns:

| Need | HTMX solution |
| --- | --- |
| Filter/search | `hx-trigger="keyup changed delay:300ms"` |
| Load more | `hx-trigger="revealed"` on last item |
| Inline edit | `hx-get` on click, `hx-post` on submit |
| Delete with confirm | `hx-confirm="Are you sure?"` |
| Auto-refresh | `hx-trigger="every 30s"` |
| Form submit without reload | `hx-post` + `hx-target` |
| Tab switching | `hx-get` + `hx-push-url` |

Only add vanilla JS for drag-and-drop, complex client-side state, or browser APIs (clipboard, geolocation, file reading).

## When to Skip

Skip `/superjeff:design` only for:
- Pure API apps with no templates
- Bug fixes touching no UI
- Backend-only changes (model, service, migration)

For these, go straight to `/superjeff:build <app>`.

## After Design

```
/superjeff:build expenses   ← implements the UX spec alongside the backend
```

The build pipeline will now include template implementation tasks referencing the UX spec component names and HTMX patterns.
