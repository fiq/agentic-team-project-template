---
name: infra-local-compose
description: Specialise local Compose topology only when runtime dependencies require it.
---

# Infrastructure: Local Compose

Use Compose only when local runtime topology needs services. Keep developer
tooling in Nix. Prefer Testcontainers or equivalent for lifecycle-managed
integration dependencies where the stack supports it.
