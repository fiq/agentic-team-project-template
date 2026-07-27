# Wiki

This wiki is the project's durable knowledge base. It is organised into two
sections so you can quickly find what you need:

- **Method** — how we work here. These pages are inherited from the template and
  describe practices, roles and tooling. They change when practice changes.
- **Product** — what we are building. These pages are written by this project and
  describe the domain, architecture and operations. They change when the product
  changes.

New here? Start with [Agents](method/agents.md) for startup and roles, or
[Development](method/development.md) for the day-to-day command sequence.

## Method — how we work

| Page | Covers |
|---|---|
| [Agents](method/agents.md) | Startup, roles and delegation |
| [Development](method/development.md) | Day-to-day lifecycle and command sequence |
| [Testing](method/testing.md) | Validation strategy and layer selection |
| [Portable context router](method/context-router.md) | Why and how context depth is routed |
| [Method glossary](method/glossary.md) | Vocabulary for the way we work |

## Product — what we are building

| Page | Covers |
|---|---|
| [Architecture](product/architecture.md) | Runtime shape and boundaries |
| [Domain](product/domain.md) | Domain model and language |
| [Operations](product/operations.md) | Running and operating the system |
| [Product glossary](product/glossary.md) | Domain vocabulary |

## Elsewhere

- [Context store](../context-store.md) — how context is preserved across sessions.
- [Validation](../validation.md) — what checks prove.
- [Decisions](../decisions/) — ADRs.

## Rules

- Every page declares `axis: method` or `axis: product` matching its directory;
  `project context check` fails when they disagree.
- A fact has one canonical home. Other pages link to it.
- Generated projects rewrite `product/` and inherit `method/`. Changing a `method/` page
  is a change to how the team works, and belongs in a decision record.
