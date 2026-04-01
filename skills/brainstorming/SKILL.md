---
name: "Brainstorming & Design Gate"
description: "Socratic design validation before any planning or implementation begins. Produces a design document that the build pipeline depends on."
version: "1.0"
origin: "superpowers-inspired"
---

## When to Activate

- User runs `/superjeff:brainstorm`
- Before any `/superjeff:build` command — the build pipeline checks for a design artifact
- When requirements seem ambiguous or the scope is unclear

## Why This Exists

Skipping design is the leading cause of wasted implementation cycles. A 15-minute design conversation prevents 3-hour rewrites. This skill forces that conversation before any code is planned.

The design document produced here becomes the anchor for all downstream decisions. If a task in the build pipeline contradicts the design document, the design document wins.

## Process

### Phase 1 — Understand Before Proposing

Before suggesting any solution, ask these questions (one at a time, not all at once):

1. **What problem are we solving?** — In one sentence, what does the user need to accomplish?
2. **Who is the actor?** — What user role triggers this? What are they trying to do?
3. **What does success look like?** — What is the system doing differently after this is built?
4. **What are the constraints?** — Performance, security, existing data, existing code?
5. **What are the failure modes?** — What can go wrong? What should the system do when it does?
6. **What is explicitly out of scope?** — What are we NOT building?

Do not move to Phase 2 until each question is answered clearly.

### Phase 2 — Design Proposal

Propose ONE design. Not alternatives — a concrete recommendation with a rationale.

Structure the proposal as:

```markdown
## Design: <Feature Name>

### Problem Statement
[One sentence]

### Approach
[Which Django apps are affected. What new models/services/views are needed. What existing code changes.]

### Key Decisions
[Why this approach, not the obvious alternative]

### Data Model Changes
[New fields, new models, changed relationships]

### Service Layer Changes
[New service methods, changed signatures, new exceptions]

### API Changes (if any)
[New endpoints, changed request/response shapes]

### Out of Scope
[What we are explicitly NOT building]

### Risks
[What could go wrong. What we don't know yet.]
```

### Phase 3 — Validation

Before saving the design document, verify:

- [ ] The problem statement is understood, not assumed
- [ ] The approach touches the minimum number of components
- [ ] All failure modes are named
- [ ] Out of scope is explicit
- [ ] No implementation details — this is design, not planning

### Phase 4 — Save Design Artifact

Save to: `artifacts/specs/YYYY-MM-DD-<feature-slug>.md`

This file is the input to `/superjeff:build`. The build pipeline will fail if no design artifact exists for the feature being built.

## Anti-Patterns

Avoid:
- Jumping to a solution before the problem is fully understood
- Proposing multiple alternatives — pick one and defend it
- Including code in the design document — save that for the plan
- Treating the design document as permanent — it can be revised, but the revision must be explicit
- Skipping this phase because "it's a small feature" — small features cause the biggest surprises

## Design Document Signals: Something Is Wrong

Stop and re-ask if:
- The problem statement has the word "and" (two problems, not one)
- The approach touches more than 3 Django apps
- You cannot name the out-of-scope items
- The risks section is empty

## Related Skills

- [Planning & Subtask Breakdown](../planning/SKILL.md) — next step after design
- [TDD Workflow](../testing/SKILL.md) — what tests follow from the design
