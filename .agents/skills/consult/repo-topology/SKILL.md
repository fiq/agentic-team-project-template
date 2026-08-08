---
name: repo-topology
description: Choose monorepo versus separate repositories and record the resulting topology decision.
---

# Consult: Repository Topology

## Outcome

Decide monorepo versus separate repositories and record the decision. When
splitting, produce per-component repositories and a thin top-level coordination
repo, without losing template state.

## Method

1. Ask monorepo vs separate repos. Recommend monorepo for small teams and
   single-runtime projects.
2. Separate repos: each component directory gets its own `git init`, its own
   `flake.nix` devshell, Dockerfile, CI workflow, and a sliced README/AGENTS.
   The top-level checkout becomes a thin coordination repo that tracks the
   component repos as git submodules and keeps `HANDOFF.toon`, cross-repo
   compose topology, and cross-cutting docs.
3. Register submodules with relative paths immediately; fix up remote URLs when
   the sub-repos are pushed. If remotes are unknown, record a revisit trigger in
   the profile rather than blocking.

## Guards

- A dirty working tree blocks the split: ask the user to commit or stash first.
- Never remove a dirty worktree.

## Outcome recording

- Write the monorepo-vs-separate-repos decision to `PROJECT_PROFILE.toon` as a
  decision entry, ending in a documented decision. Never leave it resolved
  only in conversation.
- This is the most irreversible decision in the consult cluster: splitting
  runs `git init` per component and converts the top-level checkout into a
  submodule tracker. Record it as an ADR under `docs/decisions/`, not only a
  profile entry.
- When splitting, also record per-component repo state (registered
  submodules, pending remote URLs, any revisit trigger) in
  `PROJECT_PROFILE.toon`.

## Do not

- Split without an explicit decision.
- Discard `.agents/`, `.agentic-template/`, `PROJECT_PROFILE.toon` or
  `HANDOFF.toon` when carving components.
