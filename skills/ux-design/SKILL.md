---
name: "UX Design"
description: "Translate a brainstorm design artifact into a structured UX spec for Django + HTMX: design tokens, page layouts, component states, HTMX interaction patterns, and accessibility requirements."
version: "1.0"
stack: "django-templates + htmx + vanilla-js"
origin: "superjeff"
---

## When to Activate

- `build_pipeline.yaml` enters the `design` stage
- The brainstorm artifact exists at `artifacts/specs/YYYY-MM-DD-<feature>.md`
- The Requirements Agent has produced its output for the app

## What This Skill Produces

A UX spec saved to `artifacts/ux/<app>_ux_spec.json` that the Frontend Agent and the implementation plan will consume. It covers:

1. **Design tokens** — the visual language (colors, type scale, spacing, radius, shadows)
2. **Page inventory** — every page, its sections, and its four states
3. **Component library** — reusable partials with HTMX attributes and accessibility
4. **HTMX interaction patterns** — which patterns apply and how to implement them
5. **Forms** — field-to-serializer mapping, error display, submission behavior
6. **JS requirements** — only when HTMX genuinely cannot do the job

---

## Process

### Step 1 — Read inputs

Load:
- `artifacts/specs/YYYY-MM-DD-<feature>.md` — design intent, user goals
- Requirements Agent output for the app — models, endpoints, serializer fields
- Any existing `artifacts/ux/<app>_ux_spec.json` — for incremental updates

Do NOT start writing until you have read all three.

### Step 2 — Define design tokens

Design tokens are the foundation. Define them first — everything else references them.

```json
{
  "design_tokens": {
    "colors": {
      "primary": "#2563EB",
      "secondary": "#64748B",
      "accent": "#F59E0B",
      "danger": "#DC2626",
      "warning": "#D97706",
      "success": "#16A34A",
      "text_primary": "#111827",
      "text_muted": "#6B7280",
      "background": "#F9FAFB",
      "surface": "#FFFFFF",
      "border": "#E5E7EB"
    }
  }
}
```

**Rules:**
- Choose a palette that fits the product domain (financial app → conservative blues; creative tool → bolder palette)
- Contrast ratio MUST be ≥ 4.5:1 for normal text (WCAG AA)
- Contrast ratio MUST be ≥ 3:1 for large text and UI components
- Every color token must have a clear semantic name — never `color1`, `color2`

### Step 3 — Inventory pages

List every page the app needs. For each page, define:

```json
{
  "name": "ExpenseList",
  "url_pattern": "/expenses/",
  "template": "templates/expenses/list.html",
  "title": "Expenses",
  "layout": "templates/layouts/dashboard.html",
  "sections": [
    {"name": "header", "role": "hero", "component": "PageHeader"},
    {"name": "filter-bar", "role": "form", "component": "FilterBar", "htmx_loaded": false},
    {"name": "expense-table", "role": "list", "component": "ExpenseTable", "htmx_loaded": true}
  ],
  "states": ["loading", "empty", "error", "populated"]
}
```

**Every page needs:**
- A skip link (`<a href="#main-content">Skip to content</a>`)
- A `<main id="main-content">` landmark
- A dynamic `<title>` pattern (e.g. `Expenses | AppName`)
- `aria-live="polite"` on every HTMX-swapped region

### Step 4 — Define components

For every component (page, partial, form, list item):

```json
{
  "name": "ExpenseTable",
  "type": "list",
  "template": "templates/expenses/partials/expense_table.html",
  "is_htmx_partial": true,
  "states": {
    "loading": "skeleton rows with animate-pulse",
    "empty": "illustration + 'No expenses yet' + CTA button",
    "error": "inline error banner with retry button",
    "populated": "sortable table rows with inline edit"
  },
  "htmx_attributes": [
    {
      "attribute": "hx-get",
      "value": "/api/v1/expenses/",
      "explanation": "Loads expense list on page load"
    },
    {
      "attribute": "hx-trigger",
      "value": "load, filterChanged from:body",
      "explanation": "Reloads when filter bar emits filterChanged event"
    },
    {
      "attribute": "hx-indicator",
      "value": "#expense-table-spinner",
      "explanation": "Shows spinner during load"
    }
  ]
}
```

**Rules:**
- Every component that can be empty MUST have an `empty` state — not just a blank screen
- Every HTMX request MUST have `hx-indicator` pointing to a loading element
- Every HTMX-swapped region MUST be a Django partial (separate `.html` file) — not inline HTML in views
- Keyboard navigation must work without a mouse on every interactive component

### Step 5 — Map HTMX patterns

Identify which HTMX patterns apply and document implementation:

| Pattern | When to use | Key attributes |
| --- | --- | --- |
| `live-search` | Search input that filters results as you type | `hx-trigger="keyup changed delay:300ms"`, `hx-target="#results"` |
| `infinite-scroll` | Load more items on scroll | `hx-trigger="revealed"` on last list item |
| `inline-edit` | Edit a field in place | `hx-get` on click → renders form partial; `hx-post` on submit → renders value partial |
| `confirm-delete` | Confirm before delete | `hx-confirm="Are you sure?"` on delete button |
| `optimistic-update` | Show result before server confirms | `hx-swap="outerHTML"` + custom response swap |
| `polling` | Auto-refresh data | `hx-trigger="every 30s"` |
| `active-search` | Highlight matching results | `hx-trigger="keyup changed delay:200ms"` |
| `lazy-load` | Load content when it enters viewport | `hx-trigger="intersect once"` |

Document which patterns apply to which components.

### Step 6 — Define JS requirements

Only add a JS requirement when HTMX genuinely cannot handle it:

```json
{
  "feature": "drag-and-drop reordering of expense line items",
  "reason_htmx_insufficient": "HTMX has no drag event support — requires DOM manipulation during drag",
  "implementation": "SortableJS (CDN, <5KB gzip) — fires hx-post on drop to persist order"
}
```

**HTMX-first rule**: If you are tempted to add JS, first ask:
- Can `hx-trigger` handle this event?
- Can `hx-on:*` handle this DOM event?
- Can `_hyperscript` handle this? (hyperscript is acceptable as a JS alternative)

If the answer to all three is no, then add a JS requirement.

### Step 7 — Verify completeness

Before saving the artifact, check:

- [ ] All design tokens defined (no nulls)
- [ ] Every page has 4 states: loading, empty, error, populated
- [ ] Every HTMX request has `hx-indicator`
- [ ] Every HTMX-swapped region has `aria-live`
- [ ] Every form has all fields mapped to serializer fields
- [ ] Every form has error display method defined
- [ ] Every page has skip link and main landmark
- [ ] No JS requirement added where HTMX would suffice
- [ ] Color contrast checked (≥ 4.5:1 for text)

### Step 8 — Save artifact

```
artifacts/ux/<app>_ux_spec.json
```

Then commit:
```
design(<app>): UX spec — <N> pages, <N> components, design tokens
```

---

## Template Patterns for Django + HTMX

### Base template structure

```html
{# templates/base.html #}
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}AppName{% endblock %}</title>
  {% block css %}{% endblock %}
  <script src="https://unpkg.com/htmx.org@2.0.0" defer></script>
</head>
<body>
  <a href="#main-content" class="skip-link">Skip to content</a>
  {% include "partials/nav.html" %}
  <main id="main-content">
    {% block content %}{% endblock %}
  </main>
  {% include "partials/toast.html" %}
  {% block js %}{% endblock %}
</body>
</html>
```

### HTMX partial (fragment)

```html
{# templates/<app>/partials/expense_table.html #}
{# This file is returned by the view when hx-request header is present #}
<div id="expense-table" aria-live="polite" aria-label="Expense list">
  {% if expenses %}
    <table>...</table>
  {% else %}
    {% include "partials/empty_state.html" with message="No expenses yet" %}
  {% endif %}
</div>
```

### View pattern for HTMX partials

```python
# In the view, detect HTMX request and return partial
def expense_list(request):
    expenses = expense_service.list_expenses(user=request.user)
    if request.headers.get("HX-Request"):
        return render(request, "expenses/partials/expense_table.html", {"expenses": expenses})
    return render(request, "expenses/list.html", {"expenses": expenses})
```

### Loading indicator pattern

```html
<div id="expense-table-spinner"
     class="htmx-indicator"
     aria-label="Loading expenses"
     role="status">
  {# skeleton or spinner here #}
</div>
```

---

## Anti-Patterns

Avoid:
- Defining design tokens as empty or placeholder — always set real values
- Using JS when HTMX solves the problem
- Returning full-page HTML from HTMX endpoints — always return the specific partial
- Missing `hx-indicator` on any HTMX request
- Missing empty states — a blank screen is not a design
- Missing `aria-live` on dynamically updated regions
- Inline CSS instead of design token references
- `<div>` where a semantic element (`<button>`, `<nav>`, `<article>`) is appropriate

## Related Skills

- [Brainstorming](../brainstorming/SKILL.md) — design artifact is input to this skill
- [Planning](../planning/SKILL.md) — UX spec becomes implementation tasks
- [Testing](../testing/SKILL.md) — accessibility assertions in tests
- [Verification](../verification/SKILL.md) — visual + HTMX behavior verification
