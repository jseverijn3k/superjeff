---
name: "Business Case Decomposition"
description: "Analyze a free-text business case and decompose it into bounded Django app contexts"
version: "1.0"
origin: "superjeff"
---

## When to Activate

- User provides a business case, product description, or "build me X" prompt
- User runs `/superjeff:decompose`
- Orchestrator invokes the Product Decomposition Agent

## Decomposition Process

### Step 1: Domain Identification
Read the business case and extract all nouns that represent data or processes:
- "expense reports", "receipts", "approval workflows", "budgets" → candidate domains
- "users", "companies", "roles" → auth/tenant domain (always its own app)

### Step 2: Responsibility Mapping
For each domain, write a single sentence: "This app is responsible for ___"
- If the sentence has two independent clauses → split into two apps
- If two domains share the same models → merge them

### Step 3: Dependency Graph
For each app pair (A, B):
- Does A need to import a model from B? → A depends on B
- Does B also need to import a model from A? → circular dependency → redesign

### Step 4: External Services
For each app:
- Does it handle payments? → depends on Stripe / payment gateway
- Does it send email? → depends on SendGrid / SES
- Does it store files? → depends on S3-compatible storage

### Step 5: Output Validation
- Validate against `schemas/app_schema.json`
- Assert: no circular dependencies
- Assert: no model names duplicated across apps
- Assert: no app has more than 5 unrelated models

## Anti-Patterns

Avoid:
- `core` or `common` app that holds everything → split by domain
- Circular dependencies between apps → use signals or service layer
- Putting auth logic inside another app → `accounts` is always separate
- One app per model → group related models together

## Related Skills

- [Django App Specification](../django/SKILL.md)
- [Requirements Generation](../validation/SKILL.md)
