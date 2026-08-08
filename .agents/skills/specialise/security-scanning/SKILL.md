---
name: security-scanning
description: Wire the project dep-audit dependency vulnerability scan into project check and generated CI.
---

# Specialise: Security Scanning

## Outcome

Runtime dependency vulnerability scanning is available through
`project dep-audit` and runs as part of `project check` and generated CI.

## Method

1. `project dep-audit` wraps osv-scanner (or the ecosystem-native audit tool
   when clearly better), executed via the same Nix-or-container ladder used by
   scaffold execution.
2. It is already part of the `project check` composite; ensure generated CI
   runs `project check` so the audit is exercised.
3. Add osv-scanner to the Nix devshell for specialised projects so the native
   ladder rung is available.

## Degradation

Offline or network-restricted environments skip with an explicit warning, never
a silent pass. A skip is visibly reported and records its reason; it is not a
green result.

## Do not

- Treat a skipped scan as a pass.
- Duplicate build logic in CI instead of calling `project` commands.
