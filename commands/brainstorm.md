---
name: brainstorm
command: /superjeff:brainstorm
description: Design gate — Socratic validation of a feature idea before planning or implementation begins
input: Feature description (free text) or problem statement
output: artifacts/specs/YYYY-MM-DD-<feature-slug>.md
skill: skills/brainstorming/SKILL.md
---

## Purpose

Forces a design conversation before any code is planned. Produces a design document that the build pipeline depends on.

**This is not optional.** `/superjeff:build` will warn if no design artifact exists.

## Usage

```
/superjeff:brainstorm
```

Then describe the feature or problem in free text. The agent will ask clarifying questions before proposing a design.

## What Happens

1. Agent asks up to 6 clarifying questions (one at a time)
2. Based on your answers, proposes ONE concrete design
3. Design is validated (problem statement, approach, failure modes, out-of-scope)
4. Design artifact saved to `artifacts/specs/YYYY-MM-DD-<feature-slug>.md`

## Output Format

```markdown
## Design: <Feature Name>

### Problem Statement
[One sentence]

### Approach
[Django apps affected. New models/services/views needed. Existing code changes.]

### Key Decisions
[Why this approach]

### Data Model Changes
[New fields, models, relationships]

### Service Layer Changes
[New service methods, changed signatures, new exceptions]

### API Changes
[New endpoints, changed shapes — if any]

### Out of Scope
[Explicitly NOT building]

### Risks
[What could go wrong. What is unknown.]
```

## Next Step

Run `/superjeff:specify <app>` to generate the implementation spec, then `/superjeff:build <app>` to run the build pipeline.

## When to Skip

You may skip brainstorm for:
- Bug fixes with a clear, isolated root cause
- Pure config or migration changes
- Trivial additions (e.g., adding one field to an existing model)

For anything that introduces new behavior, a new service method, or a new API endpoint — do not skip.
