---
axis: method
---

# Testing

Drive design outside-in, from the boundary in (ATDD-aligned): a structured
change scenario's acceptance test is written first and fails for the right
reason before any implementation.

```
WHEN/THEN scenario ──► acceptance test (fails) ──► drive inward ──► passes
```

Acceptance tests are orthogonal to the testing trophy. They are not a layer
*inside* the pyramid — they are a separate dimension that drives design and
verifies behaviour from the outside in. The trophy governs the *balance of
supporting tests* underneath; acceptance tests govern *whether the right thing
was built*.

```
acceptance tests (orthogonal — drive design, verify intent)
    │
    │  orthogonal to ↓
    │
    ┌────────────────────┐
    │   E2E              │
    │  /few\             │
    │ /component\        │  testing trophy
    │/integration\       │  (balance of supporting tests)
    │/contract\          │
    │/unit/domain\       │
    └────────────────────┘
```

Choose the boundary test's fidelity by risk and known architectural direction:

```
acceptance (end-to-end)   high value / risk, user-visible
component-integration     bounded slice, real internal wiring
subcutaneous              logic under the UI where UI cost > its risk
```

Underneath, keep a testing-trophy balance and a thin real-dependency
confirmation layer where semantics matter:

```
                         E2E
                          /\
                         /few\
                       /------\
                      /component\
                    /integration\
                   /------------\
                  / contract     \
                 /----------------\
                / unit/domain      \
               /____________________\
```

Use real dependencies where semantics matter and cost is reasonable. Do not let
mocked tests overclaim confidence. See
`.agents/skills/workflow/outside-in-tdd/SKILL.md`.

## Static analysis

Static analysis is a shift-left gate that runs before tests in CI. It catches
defects, style violations, type errors, security issues and complexity drift
before they reach review or production.

```
project lint ──► project test ──► project ready
  (shift-left)     (behaviour)      (composite gate)
```

Generated projects must specialise `project lint` at `/specialise`. The
framework is opinionated about analysis *categories* (lint, type-check,
security, complexity) but adaptable about *tools* — pick the right ones per
runtime and pivot easily when better options emerge. See
`specialise/static-analysis`.

Architecture fitness functions cover conformance risks that ordinary behavior
tests do not express well: dependency direction, schema drift, boundary leaks,
deployability and important quality budgets. Put cheap automated fitness
functions behind `project check` or `project ready`; record manual checks in
`HANDOFF.toon.tests_run` until they can be automated.
