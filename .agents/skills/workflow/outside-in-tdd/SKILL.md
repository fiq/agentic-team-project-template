---
name: outside-in-tdd
description: Drive design from the boundary in, starting from a change scenario's acceptance test.
id: SKILL-outside-in-tdd
triggers: [implementing_a_change_scenario, meaningful_behaviour_change]
default_task_risk: normal
required_runtime: [shell, repo_search]
layers:
  core: core.md
canonical_for: [boundary_test_fidelity]
verification:
  - .agentic-template/bin/project test
recovery_sources:
  - .agents/skills/CATALOG.toon
  - docs/validation.md
status: active
---

# Outside-in TDD

## Outcome

Drive design from the boundary in. Each structured change scenario's acceptance
test is written first (ATDD) and fails for the right reason before any
implementation, then design pressure moves inward.
