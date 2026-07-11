# Knowledge Entry Schema

Knowledge entries are Markdown files with YAML-like frontmatter. The format is
plain text by design and can later be indexed into a graph or retrieval system.

Required fields:

```yaml
id: SYS-001
type: system
title: Example system
status: canonical
summary: One sentence summary.
```

Common optional fields:

```yaml
owners:
  - team-name
tags:
  - tag
relates_to:
  - DOM-001
depends_on:
  - SYS-002
consumes:
  - CON-003
produces: []
decisions:
  - ADR-004
patterns:
  - PAT-002
risks:
  - RISK-006
open_questions:
  - Q-017
evidence:
  - source or validation reference
reviewed_at: 2026-07-11
review_after: 2026-10-11
superseded_by: null
```

Types and prefixes:

| Type | Prefix |
|---|---|
| `domain` | `DOM-` |
| `system` | `SYS-` |
| `contract` | `CON-` |
| `architecture` | `ARCH-` |
| `decision` | `ADR-` |
| `pattern` | `PAT-` |
| `risk` | `RISK-` |
| `question` | `Q-` |
| `learning` | `LRN-` |
| `inbox` | `INBOX-` |

Canonical entries need review metadata: `reviewed_at` and `review_after`.
Superseded entries need `superseded_by`.
