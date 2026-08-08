---
name: infra-k8s
description: Produce the smallest useful Kubernetes skeleton with kubeconform validation wired into project infra-check.
---

# Specialise: Kubernetes Infrastructure

## Outcome

The smallest useful Kubernetes skeleton exists, is statically validated, and is
never applied automatically.

## Method

1. Create a kustomize base plus overlay with pinned images, resource requests
   and probes.
2. `project infra-check` wires static validation via kubeconform. When a
   `kustomization.yaml`/`kustomization.yml` is detected, it renders the
   overlay with `kustomize build` and validates the rendered output — not the
   raw kustomize source directory. Kustomize overlays are strategic-merge
   patches that omit required fields (e.g. an image patch omitting
   `spec.selector`), so raw-directory validation would reject valid overlays.
   Plain manifest directories (`k8s/`, `deploy/`, `manifests/` with no
   kustomization) are validated directly, with no render step.
3. Offer kind or k3d for local smoke testing when Kubernetes is the deployment
   target.

## Guards

- Never applied automatically.
- No cloud credentials required for validation.
- Add kubeconform to the Nix devshell so `project infra-check` can validate;
  add kustomize too when the skeleton uses a kustomize base/overlay, since
  rendering happens before validation.

## Do not

- Apply infrastructure from generic template CI.
- Require cloud credentials for static validation.
