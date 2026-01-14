# Custos

Custos is a lightweight, policy-driven helper library for applying explicit, auditable guardrails to common data transformations at ingestion time.

Custos helps data engineers make routine transformations—such as JSON flattening, schema normalization, PII handling, and row-level quality checks—consistent, visible, and safe, without replacing existing tools or platforms.

Custos is Latin for “guardian.”

### Design choice: explicit over inferred

Custos does not attempt to infer schemas, repair data, or guess intent.
All transformations are explicitly declared in policy.
If a value is changed, dropped, or rejected, it is recorded and reported.


## Why Custos exists

In many data pipelines, the same transformation logic is repeatedly rewritten:

- flattening nested JSON

- renaming columns

- casting types

- masking or dropping PII

- filtering invalid rows

These transformations are often:

- implicit

- scattered across scripts

- hard to audit

- easy to change accidentally

Custos makes these decisions explicit by defining them once, as policy, and applying them consistently.

## What Custos is (and is not)
✅ Custos is

- A helper library, not a platform

- Policy-driven and explicit

- Designed for ingestion-time transformations

- Focused on correctness and auditability

- Easy to add — and easy to remove

❌ Custos is not

- A replacement for dbt, Spark, or SQL

- A data modeling tool

- An orchestration framework

- An auto-fixing or inference engine

- A governance or compliance platform

Custos deliberately avoids “magic.”
If data is changed, dropped, or rejected, it is logged and reported.

## Core features

- Controlled JSON flattening (with depth and array handling)

- Column renaming and schema normalization

- Type casting with explicit failure modes

- PII masking, hashing, or dropping

- Row-level data quality enforcement

- Structured audit reports for every run

## Design principles

- Explicit over clever

- Fail loudly or drop safely — never guess

- Policy as code

- Guardrails, not inference

- Low friction for developers

Custos is designed to complement existing pipelines, not redefine them.

## Quick example

```python
from custos import PolicyTransformer

transformer = PolicyTransformer(
    policy="policy.yml",
    mode="strict"  # strict | dry_run
)

df_out, report = transformer.apply(df_in)
```

A single policy file controls what happens.
A structured report explains exactly what changed and why.

### When to use Custos

- In ingestion or staging pipelines

- When transforming semi-structured data

- When enforcing basic correctness early

- When you want repeatable, auditable transformations

### When not to use Custos

- For warehouse modeling (use dbt)

- For cross-table validation

- For complex business logic

- For inference-based data repair

### Status

Custos is currently early-stage and intentionally small.
Its feature set is deliberately constrained to remain predictable and auditable.

## Installation

```bash
pip install custos-guardrails
```
## Example: ingestion guardrails in action

Input data (what you receive)
```python
import pandas as pd

df_in = pd.DataFrame({
    "Order ID": ["101", "102", "x"],
    "Total Price": ["10.5", "oops", "30.25"],
    "email": ["john@test.com", "bad-email", None],
    "payload": [
        {"user": {"name": "Ann", "roles": ["admin"]}},
        {"user": {"name": "Bob"}},
        None,
    ],
})
```
This data has:

- mixed types

- invalid values

- PII

- nested JSON

- rows that should not pass ingestion

### Policy (what you declare once)
```yaml
version: 1

json_flatten:
  rules:
    - column: payload
      prefix: payload
      max_depth: 2
      arrays: stringify
      drop_source: true

schema:
  rename:
    "Order ID": "order_id"
    "Total Price": "total_price"

  types:
    order_id: int
    total_price: float

  cast:
    on_cast_fail: set_null

pii:
  rules:
    - column: email
      action: mask
      mask_style: email

quality:
  default_on_fail: drop_row
  rules:
    - name: total_price_non_negative
      column: total_price
      not_null: true
      min: 0

    - name: order_id_required
      column: order_id
      not_null: true
```
This policy explicitly states:

- how JSON should be flattened

- how columns should be renamed

- how types should be enforced

- how PII should be handled

- which rows are allowed to pass

### Apply the policy
```python
from custos import PolicyTransformer

transformer = PolicyTransformer(
    policy="policy.yml",
    mode="strict"
)

df_out, report = transformer.apply(df_in)
```

### Output data (what continues downstream)
```text
   payload.user.name payload.user.roles  total_price  order_id          email
0                Ann           ["admin"]         10.5       101  j***@test.com
```

What happened:

- JSON was flattened

- invalid casts became null

- PII was masked

- rows failing quality checks were dropped

- only clean, explicit, auditable data passed through

### Audit report (what Custos records)
```text
rename_applied
cast_failures
pii_masked
quality_violations
rows_dropped_due_to_quality
```
Each step includes structured details:

- which columns were affected

- how many rows failed

- why rows were dropped

Nothing is implicit. Nothing is hidden.

### Why this matters

Without Custos, this logic is usually:

- scattered across scripts

- partially undocumented

- easy to change accidentally

- difficult to audit later

With Custos:

- the transformation intent is explicit

- the behavior is repeatable

- the outcome is explainable

That’s the core value.