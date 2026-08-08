---
name: local-sandbox
description: Add a local cloud-service sandbox (LocalStack, Azurite, GCP emulators, Supabase) when containers alone are insufficient.
---

# Specialise: Local Sandbox

## Outcome

Local development gains cloud-service semantics when plain containers are
insufficient or collaborators need a shared sandbox, recorded as part of local
topology.

## Method

1. Trigger when local development needs cloud service semantics beyond plain
   containers, or collaborators need a shared sandbox.
2. Choose the sandbox by target cloud (one question, recommendation first,
   Other offered):
   - AWS: LocalStack.
   - Azure: Azurite.
   - GCP: official emulators.
   - Supabase: `supabase` local stack.
3. Follow existing Compose rules: pinned images, health checks, health-aware
   ordering, deterministic cleanup, no committed secrets.
4. Record the sandbox in the profile as part of local topology.

## Do not

- Add a sandbox without an evidenced need.
- Commit secrets or leave containers running after a bounded smoke test.
