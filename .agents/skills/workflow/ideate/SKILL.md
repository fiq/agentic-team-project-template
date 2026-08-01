---
name: ideate
description: Short-cycle multi-persona session that turns an idea or narrative into a validated change proposal.
id: SKILL-ideate
triggers: [ambiguous_feature_request, unspecified_feature_request, narrative_provided]
default_task_risk: normal
required_runtime: [shell, repo_search]
optional_runtime: [subagents]
layers:
  core: core.md
  procedure: procedure.md
  failure_modes: failure-modes.md
verification:
  - .agentic-template/bin/project check-changes
recovery_sources:
  - .agents/skills/CATALOG.toon
  - specs/README.md
status: active
---

# Ideate

## Outcome

Turn an idea — or a narrative (prompt or file) — into a validated
structured change proposal through a short, bounded, multi-persona loop.
Auto-suggest this when a feature request is ambiguous or unspecified.
