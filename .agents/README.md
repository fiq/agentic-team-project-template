# Agent System

This directory holds project-local agent topology, coordination policies and
lazy-loaded skills. `AGENTS.md` remains canonical.

Load only the files needed for the current task.

## Knowledge Layer

Use `.agents/knowledge/` for durable reviewed project knowledge and
`.agents/knowledge/inbox/` for unreviewed proposals. Keep `HANDOFF.toon`
limited to active task state and reference knowledge IDs instead of copying
entries.

```
request -> team selection -> knowledge search -> Superpowers workflow
        -> implementation/review -> handoff -> knowledge capture
        -> inbox proposal -> review -> canonical knowledge
```

Superpowers owns engineering workflow. This repository owns local roles,
knowledge retrieval, learning capture and promotion rules.
