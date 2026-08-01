---
name: reconcile-delivery
description: Reconcile planned architecture and acceptance criteria against what was actually delivered.
id: SKILL-reconcile-delivery
triggers: [before_delivery_pr, material_scope_change, project_delivery, documentation_drift]
default_task_risk: normal
required_runtime: [shell, repo_search]
layers:
  core: core.md
  procedure: procedure.md
  verification: verification.md
  failure_modes: failure-modes.md
verification:
  - .agentic-template/bin/project ready
  - .agentic-template/bin/project check
recovery_sources:
  - .agents/skills/CATALOG.toon
  - HANDOFF.toon
status: active
---

# Reconcile Delivery

## Outcome

Ensure documentation, specs, profiles and handoff state truthfully reflect
the delivered repository, not stale intentions.
