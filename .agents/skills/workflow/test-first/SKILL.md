---
name: test-first
description: Drive meaningful behaviour changes with the smallest useful failing test.
---

# Test-first Workflow

```
behaviour -> smallest failing test -> minimal implementation
  -> test passes -> refactor if useful -> increase fidelity for remaining risk
```

Ask:

1. What behaviour are we proving?
2. What is the cheapest test that can fail for the right reason?
3. Which integration semantics remain untested?
4. Is a real dependency cheap enough to use?
5. What added fidelity buys real confidence?

Do not force theatre when work is exploratory or test cost exceeds learning.

## Structure: Arrange-Act-Assert

Every test has three visible parts, in order:

- **Arrange** — build the starting state from a real fixture: a
  setup/teardown method, a fixture function, or a factory. Never reuse
  another test's shared mutable state (a module-level object, a leftover
  database row, a file another test wrote) — that is what makes tests
  order-dependent and flaky.
- **Act** — exercise exactly one behaviour.
- **Assert** — check the specific outcome the test names, not incidental
  side effects.

A test whose arrange step is copy-pasted setup with no isolation, or that
silently depends on a previous test having run first, is not arranged — it
is coupled.

## FIRST

| | Property | Means |
|---|---|---|
| F | Fast | runs in the feedback loop a developer actually uses, not just CI |
| I | Independent | no ordering dependency, no shared fixture state between tests |
| R | Repeatable | deterministic — no unseeded randomness, wall clock or live network |
| S | Self-validating | pass/fail is programmatic; no reading log output to decide |
| T | Timely | written with the behaviour it guards, not backfilled long after |

A suite that only passes in file order, or that needs a human to eyeball
output, has failed FIRST even if every assertion is individually correct.
