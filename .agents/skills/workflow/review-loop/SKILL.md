---
name: review-loop
description: Bounded clean-up review for boy-scout, code and architectural smells and inappropriate coupling.
id: SKILL-review-loop
triggers: [before_merge, boy_scout_cleanup, diff_ready_for_review]
default_task_risk: normal
required_runtime: [shell, repo_search]
optional_runtime: [subagents]
layers:
  core: core.md
  procedure: procedure.md
  verification: verification.md
  failure_modes: failure-modes.md
canonical_for: [quality_boy_scout]
verification:
  - .agentic-template/bin/project test
  - .agentic-template/bin/project check
recovery_sources:
  - .agents/skills/CATALOG.toon
  - docs/validation.md
status: active
---

# Review Loop

## Outcome

A short, bounded pass that leaves the changed code cleaner than it was and surfaces
smells and coupling before merge. It enforces the standing quality rule; it does not
hunt for correctness bugs — code review does that.

## Use when

A diff is ready for merge, or a change touched code worth leaving cleaner.

Rules are in `core.md`, the two-pass sequence in `procedure.md`, the gate in
`verification.md`, and the ways this goes wrong in `failure-modes.md`.
