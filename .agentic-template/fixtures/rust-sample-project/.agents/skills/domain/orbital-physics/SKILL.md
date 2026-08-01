---
name: orbital-physics
description: Domain guidance for the Orbit orbital physics sandbox.
id: SKILL-orbital-physics
triggers: [physics_change, orbit_tuning, trajectory_work]
default_task_risk: normal
required_runtime: [shell]
layers:
  core: core.md
  failure_modes: failure-modes.md
verification:
  - cargo build
recovery_sources:
  - .agents/skills/CATALOG.toon
status: active
---

# Orbital Physics

## Outcome

Keep the toy universe deterministic and the game feel intact while changing
physics or trajectory behaviour.
