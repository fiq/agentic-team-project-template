---
name: ship-slice
description: Ship one thin vertical slice of pricing behaviour behind a flag.
id: SKILL-ship-slice
triggers: [thin_slice_ready_to_ship]
default_task_risk: normal
layers:
  core: core.md
  procedure: procedure.md
  verification: verification.md
  failure_modes: failure-modes.md
verification: [.agentic-template/bin/project test]
recovery_sources: [.agents/skills/CATALOG.toon]
status: active
---

# Ship Slice

## Outcome

One thin vertical slice of pricing behaviour is live behind a flag, with its acceptance
scenario proven.
