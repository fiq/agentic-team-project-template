---
name: consult-repo-topology
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

## Do not

- Split without an explicit decision.
- Discard `.agents/`, `.agentic-template/`, `PROJECT_PROFILE.toon` or
  `HANDOFF.toon` when carving components.
