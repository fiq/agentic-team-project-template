---
name: team-selection
description: Select the smallest useful agent roles and knowledge searches for a task.
---

# Team Selection

## Purpose

Choose the smallest useful set of perspectives before work begins.

## Inputs

- user request
- `AGENTS.md`
- `HANDOFF.toon`
- `PROJECT_PROFILE.toon`
- relevant active spec
- `.agents/knowledge/index.md`

## Procedure

1. Identify the task type, impact, ambiguity and reversibility.
2. Search knowledge before assigning roles.
3. Select only materially relevant roles.
4. Assign ownership for outputs.
5. Identify work that can run in parallel.
6. Identify ordered dependencies.
7. Choose model class by complexity and risk.
8. Record what knowledge should be captured after the work.

## Default Roles

Use only when useful:

- orchestrator: final synthesis and sequencing
- implementer: bounded code or documentation change
- spec reviewer: intent, acceptance evidence and non-goals
- code-quality reviewer: maintainability and test concerns

Conditional roles:

- product or domain expert
- architecture challenger
- data and contract expert
- security and privacy reviewer
- operations and SRE reviewer
- UX and accessibility reviewer
- test strategist
- knowledge curator

## Output

```yaml
roles:
  - role: implementer
    reason: bounded implementation
    owns:
      - code change
model_routing:
  implementer: midrange
knowledge_to_search:
  - domains
  - systems
parallel_work: []
ordered_dependencies: []
capture_after:
  - decisions
  - learnings
```

## Do Not

- Activate every role by default.
- Ask several agents to repeat discovery.
- Replace Superpowers planning, TDD, debugging or verification workflows.
