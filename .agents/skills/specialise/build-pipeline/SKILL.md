---
name: build-pipeline
description: Nix-first reproducible builds combined with container builds; evolvable build targets recorded from /specialise.
---

# Build Pipeline

## Policy

Every generated project must make an explicit build decision at `/specialise`.
Nix owns the developer toolchain and provides a reproducible build
environment. The container build produces the deployable artefact when
applicable. Build targets are evolvable — record the target and revisit trigger.

Repeatability is the core principle: the same commit must produce the same
build artefact, locally and in CI.

## Nix-first build

The `flake.nix` provides a reproducible build environment. The build command
(`project build`) produces artefacts deterministically from the Nix shell.

- prefer Nix for developer tooling and build reproducibility;
- the `flake.nix` is the source of truth for the toolchain;
- `project build` runs inside the Nix shell so local and CI builds match;
- do not introduce NVM, pyenv, asdf or similar version managers on NixOS.

## Container build

When a deployable service, the container build uses the Nix environment (or a
multi-stage Dockerfile) to produce a pinned, reproducible image. See
[`specialise/container-build`](../container-build/SKILL.md) for container-specific
requirements (non-root user, health check, `.dockerignore`, `image-test`).

The container build is one build target, not the only one. The build target
may evolve: container, Lambda zip, static binary, etc.

## Evolvability

Build targets are evolvable. Record the target and a revisit trigger in
`PROJECT_PROFILE.toon.build`. Changing the base image or build target later
is expected — the skill provides the decision framework, not a fixed target.

## Required artifacts (when applicable)

- `.agentic-template/bin/project build`;
- `Dockerfile` or `Containerfile` when the target is a container;
- pinned base image or a documented update policy;
- `.agentic-template/bin/project image` / `project image-test` when applicable.

## Command surface

Expose `.agentic-template/bin/project build`. It must:

- run inside the Nix shell for reproducibility;
- produce the build artefact deterministically;
- fail loudly on build errors.

Libraries, mobile apps, desktop apps and Godot projects may record `build` as
`not_applicable` with a reason, but must not leave it unspecialised after
`/specialise`.

## Profile state

Record in `PROJECT_PROFILE.toon`:

```toon
build:
  nix_first: true
  target: container | lambda_zip | static_binary | not_applicable
  container_base_image: ...
  revisit_trigger: deployment_target_change_or_base_image_deprecation
  enforce_in_ci: true
```

## CI integration

CI must call `project build` before `project test` when applicable. See
[`specialise/ci`](../ci/SKILL.md).

## Do not

- Leave `build` unspecialised after `/specialise` for deployable services.
- Commit unpinned base images without an update policy.
- Duplicate build logic between Nix and Dockerfile — the Dockerfile should
  consume the Nix-built artefact where practical.
- Introduce version managers (NVM, pyenv, asdf) on NixOS.
- Treat `npx` as a runtime.
