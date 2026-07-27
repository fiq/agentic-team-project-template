---
name: context-packet
description: Package bounded context for another agent or model without flooding the window or hiding sources.
id: SKILL-context-packet
triggers: [delegation, context_window_pressure, review_request, model_handoff]
default_task_risk: normal
required_runtime: [repo_search]
optional_runtime: [subagents, structured_output]
layers:
  core: core.md
  procedure: procedure.md
  references: references.md
canonical_for: [context_packet_transport]
verification: [".agentic-template/bin/project context explain --skill context_packet"]
recovery_sources: [.agents/skills/CATALOG.toon, .agents/context/RECOVERY.toon]
status: active
---

# Context Packet

## Outcome

The receiving agent has enough context to finish a bounded task, every claim is
traceable to a source, and the sender's whole window is not copied across.

## Use when

- delegating to a subagent or another model;
- handing off under context pressure;
- asking for review, critique or a second opinion;
- summarising repository evidence for long-running work.

Budgets, packet shape and transport rules are in `core.md`. The build sequence is in
`procedure.md`.
