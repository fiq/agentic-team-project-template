# Learning Proposal Schema

Learning proposals start in `.agents/knowledge/inbox/` or
`.agents/knowledge/learnings/` until reviewed.

Required fields:

```yaml
id: LRN-001
type: learning
title: Short discovery
status: proposed
summary: One sentence.
evidence:
  - command, test, source or incident reference
discovered_during: task or session reference
candidate_promotion:
  - pattern
  - risk
```

Useful optional fields:

```yaml
relates_to:
  - SYS-001
contradicts:
  - ADR-004
open_questions:
  - Q-017
review_after: 2026-10-11
```

Reject trivial implementation details. Capture only knowledge that is likely to
help future work.
