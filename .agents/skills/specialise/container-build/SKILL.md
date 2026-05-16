---
name: container-build
---

# Container Build

Create `Dockerfile` or `Containerfile` only when useful. Prefer multi-stage
builds, non-root runtime users, project-standard dependency caching, a
meaningful `.dockerignore`, `make image`, and optional `make image-test`.

Nix owns developer tooling. Containers package deployable applications.
