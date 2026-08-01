---
name: model-routing
description: Route work to appropriate agents and models with token efficiency and a handoff protocol.
id: SKILL-model-routing
triggers: [delegation, model_choice_needed, context_window_pressure, model_handoff]
default_task_risk: normal
required_runtime: [shell, repo_search]
layers:
  core: core.md
  procedure: procedure.md
  failure_modes: failure-modes.md
canonical_for: [model_classes, model_handoff_protocol]
verification:
  - .agentic-template/bin/project check
recovery_sources:
  - .agents/skills/CATALOG.toon
  - HANDOFF.toon
status: active
---

# Model Routing

## Outcome

Route by task complexity, uncertainty, impact and reversibility. Use the
cheapest model class likely to complete the bounded task reliably.
