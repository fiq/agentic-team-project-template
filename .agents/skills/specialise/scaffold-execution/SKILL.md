---
name: specialise-scaffold-execution
description: Run the official project scaffolder repeatably via a Nix-then-container-then-one-shot ladder and merge into the template.
---

# Specialise: Scaffold Execution

## Outcome

Run the official scaffolder (Spring Initializr, create-vite, mix phx.new, etc.)
repeatably and merge its output into the template structure without losing
template state.

## Execution ladder

1. Tool provided by the Nix devshell, if the flake provides it and Nix is
   present.
2. Pinned official container (`docker run` with a pinned tag or digest).
3. Documented one-shot execution with exact tool versions recorded.

A failed rung falls back one level with the reason recorded.

## Merge

1. Scaffold into a temporary directory.
2. Merge into the template structure, preserving `.agents/`,
   `.agentic-template/`, `PROJECT_PROFILE.toon`, `HANDOFF.toon` and related
   state files.
3. Record the exact scaffold command, image digest and tool versions in the
   ADR.

## Invariants

- Local Nix devshell is always retained; Nix is never the only path.
- Prefer proven scaffold tools over hand-rolled skeletons.
- Every deployable component must build and smoke-test in both Nix and Docker.

## Do not

- Overwrite template state files during merge.
- Use an unpinned scaffold container.
