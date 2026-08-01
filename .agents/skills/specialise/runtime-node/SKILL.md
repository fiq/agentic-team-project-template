---
name: runtime-node
description: Specialise Node, TypeScript, React and package-manager conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Node or TypeScript

Detect package manager from lock files first. Respect existing Nix runtime
pinning. Do not add NVM by default on NixOS.

Specialise repository commands from real scripts. Recognise React, Vite,
Next.js and server-side Node separately. Configure tests from the project
tooling rather than adding a second harness.

## Build and tooling

- Detect the package manager from the lock file: `package-lock.json` (npm),
  `pnpm-lock.yaml` (pnpm), `yarn.lock` (Yarn), `bun.lockb` (Bun).
- Derive repository commands from real `package.json` scripts; do not invent
  a parallel command surface.
- Detect workspaces (`workspaces` in `package.json`, `pnpm-workspace.yaml`,
  Nx, Turborepo) and respect the existing monorepo structure.
- TypeScript config lives in `tsconfig.json`; detect project references and
  strictness settings rather than overriding them.
- Nix owns the developer toolchain; do not introduce NVM, fnm or Volta on
  NixOS.
- Treat `npx` as a convenience, never as a runtime.

## Static analysis (see specialise/static-analysis)

The Node ecosystem is consolidating around flat ESLint config and faster
Rust-based tooling. The per-runtime defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | ESLint | flat config (`eslint.config.js`) in v9+; Biome is a fast alternative |
| type_check | `tsc --noEmit` | the compiler is the type checker; do not skip it in CI |
| sast | eslint-plugin-security | plus `eslint-plugin-no-unsanitized` for DOM sinks |
| dependency_scan | `npm audit` / `osv-scanner` | `audit-ci` to gate CI on severity |
| complexity | ESLint | `complexity` and `max-depth` rules |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. Biome, oxlint, knip, ts-prune, dependency-cruiser), record
it in `PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

`any` escaping the type system; floating promises / missing `await`; unhandled
rejections; `==` over `===`; mutable module-level state; deep prop drilling and
oversized components; effect hooks with missing or wrong dependency arrays;
barrel-file import cycles; swallowing errors in `catch`.

## Testing

- Detect the existing runner: Vitest, Jest, node:test, Mocha. Do not add a
  second harness alongside one that already works.
- Component tests: React Testing Library; prefer user-visible queries over
  implementation details.
- E2E: Playwright is the common default; Cypress is also widely used.
- Real dependencies: Testcontainers for lifecycle-managed integration tests.
- Mock at module boundaries, not deep internals; MSW for HTTP boundaries.

## Ecosystem openness

The Node ecosystem changes faster than most. This skill provides defaults, not
a closed list. When encountering a tool or convention not covered here:

- inspect the project's `package.json`, lock file, `tsconfig.json`,
  `eslint.config.js` and `.nvmrc` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
