---
name: specialise-infra-k8s
description: Produce the smallest useful Kubernetes skeleton with kubeconform validation wired into project infra-check.
---

# Specialise: Kubernetes Infrastructure

## Outcome

The smallest useful Kubernetes skeleton exists, is statically validated, and is
never applied automatically.

## Method

1. Create a kustomize base plus overlay with pinned images, resource requests
   and probes.
2. Wire static validation via kubeconform into `project infra-check`
   (kustomization or `k8s/`, `deploy/`, `manifests/` manifests are detected and
   validated).
3. Offer kind or k3d for local smoke testing when Kubernetes is the deployment
   target.

## Guards

- Never applied automatically.
- No cloud credentials required for validation.
- Add kubeconform to the Nix devshell so `project infra-check` can validate.

## Do not

- Apply infrastructure from generic template CI.
- Require cloud credentials for static validation.
