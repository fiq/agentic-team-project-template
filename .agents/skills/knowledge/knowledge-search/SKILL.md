---
name: knowledge-search
description: Search repository knowledge before planning or implementation.
---

# Knowledge Search

## Purpose

Find relevant durable knowledge before acting, while loading the smallest useful
subset.

## Search Order

1. `.agents/knowledge/index.md`
2. candidate category folders
3. directly related IDs from frontmatter
4. relevant questions and risks
5. inbox proposals only when they may affect the task

Use `rg` before opening files.

## What To Report

```yaml
knowledge_used:
  - id: SYS-001
    reason: target system
conflicts: []
stale_entries: []
open_questions:
  - Q-017
missing_knowledge: []
```

## Rules

- Distinguish `canonical` from `proposed`, `experimental`, `deprecated`,
  `superseded` and `stale`.
- Treat proposed knowledge as a lead, not authority.
- Report conflicts and stale entries.
- Do not load the whole knowledge tree unless the task is knowledge-index work.
- Fall back gracefully when no relevant knowledge exists.
- Record the IDs that influenced the task in `HANDOFF.toon` when material.
