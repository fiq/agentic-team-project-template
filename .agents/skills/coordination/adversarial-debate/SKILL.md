---
name: adversarial-debate
description: Run a structured advocate-vs-critic debate on a bounded proposal or decision.
id: SKILL-adversarial-debate
triggers: [irreversible_decision, reviewer_disagreement, high_stakes_no_opposition]
default_task_risk: high
required_runtime: [shell, repo_search]
optional_runtime: [subagents]
layers:
  core: core.md
  procedure: procedure.md
  failure_modes: failure-modes.md
verification:
  - .agentic-template/bin/project check
recovery_sources:
  - .agents/skills/CATALOG.toon
  - HANDOFF.toon
status: active
---

# Adversarial Debate

## Outcome

Force explicit advocate and critic perspectives on a single bounded proposal
or decision before committing. Prevents groupthink and shallow agreement in
single-agent or sequential-pass workflows.
