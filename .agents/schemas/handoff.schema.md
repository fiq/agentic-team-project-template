# Handoff Schema

`HANDOFF.toon` is active session state, not a wiki.

It should contain:

- current objective;
- current phase;
- completed work;
- next actions;
- active assumptions and decisions;
- blocking questions;
- known risks;
- files changed;
- tests run;
- branch, worktree and commit state;
- team or model fallback state where relevant;
- knowledge consulted by ID;
- knowledge proposals created by ID or path;
- handoff warnings.

It should not contain:

- full canonical knowledge entries;
- chronological session logs;
- copied wiki pages;
- duplicate architecture policy;
- trivial implementation notes.

Prefer knowledge IDs over copied content.

Before changing model or provider, preserve bounded context with
`context-packet` so the receiving agent can continue without reconstructing
intent.

`knowledge` must include:

- `consulted`: IDs or paths used before planning/implementation;
- `proposals`: new or updated knowledge entries, or `[]`;
- `no_record`: reason when meaningful work produced no durable knowledge.

## Optional: loop_state

While a `coordination/loop-engineering-advisory` fallback loop is active
(no `/loop`-style tooling or `superpowers:subagent-driven-development`
available), `HANDOFF.toon` may additionally carry:

```toon
loop_state:
  plan: docs/superpowers/plans/<plan-file>.md
  task: "<task name>"
  iteration: <current iteration number>
  of: <total iterations>
  last_step_completed: "<short description>"
  next_step: "<short description>"
```

This block is optional. Remove it once the loop completes; do not leave it
as stale state after the last iteration.
