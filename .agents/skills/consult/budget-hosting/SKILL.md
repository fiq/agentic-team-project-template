---
name: budget-hosting
description: Map a budget tier to a hosting shortlist and record the resulting infrastructure decision.
---

# Consult: Budget and Hosting

## Outcome

Resolve the hosting and budget dimension into the `infrastructure:` block of
`PROJECT_PROFILE.toon` and route to the matching specialise skill, ending in a
documented decision and ADR for material choices.

## Method

1. Ask the budget tier: hobby, pre-seed, startup, scaleup, enterprise
   (plus Other). One question, recommendation first.
2. Map the tier to a hosting shortlist, always including a Kubernetes option
   where viable and always including Other. The shortlist is a starting point,
   refreshed by live research when available, not a frozen list:
   - hobby: GitHub Pages (static), Fly.io, Supabase, Cloudflare Pages/Workers,
     SQLite-class persistence.
   - pre-seed: Fly.io, Supabase, Render/Railway-class PaaS, managed Postgres
     (e.g. Neon); minimal ops.
   - startup: PaaS vs managed Kubernetes (GKE/EKS/AKS) trade-off, managed
     database.
   - scaleup: managed Kubernetes, IaC status `required`.
   - enterprise: managed or on-prem Kubernetes, compliance-aware defaults,
     IaC status `required`.
3. Write `local_topology`, `deployment_target` and `iac.status` to the
   `infrastructure:` block and route to `specialise/infra-fly`,
   `specialise/infra-aws`, or `specialise/infra-k8s`. `specialise/infra-decision`
   then formalises the recorded target into the profile's required shape.
4. Assume infra and container best practice rather than interrogating it:
   pinned images, health checks, no secrets, deterministic cleanup.

## Do not

- Add cloud resources or credentials without a deployment target.
- Freeze the shortlist; refresh with live research when available.
- Leave the infrastructure decision implicit.
