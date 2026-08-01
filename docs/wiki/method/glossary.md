---
axis: method
---

# Method Glossary

Vocabulary for how this repository works. Domain vocabulary lives in
[the product glossary](../product/glossary.md).

| Term | Meaning |
|---|---|
| Axis | Whether a page documents methodology (inherited) or the product (project-written) |
| Context profile | `lean`, `standard` or `guarded` — how much context is preloaded |
| Taxonomy layer | `summary`, `core`, `procedure`, `verification`, `examples`, `failure-modes`, `references` |
| Portable context router | The resolver that picks a profile and renders a context plan |
| Context plan | The preload set, deferred set, verification and recovery map for one task |
| Qualification | Fixture-scored evidence that a model-runtime pair handles this contract |
| Observation | A recorded qualification result and degradation history, scoped to a fingerprint |
| Task-risk floor | The minimum profile a risk class requires, applied after capability routing |
| Fitness function | A cheap deterministic check protecting an architecture characteristic |
| Context packet | A bounded, sourced hand-off of context to another agent or model |
| Static analysis | Automated analysis of source code without executing it; covers lint, type-check, security and complexity |
| Shift-left | Moving quality checks (static analysis, testing, security) earlier in the pipeline, before review and production |
| Lint gate | The `project lint` command that enforces static analysis deterministically in CI, before tests |
| Complexity budget | A recorded threshold for cyclomatic or cognitive complexity, enforced by `project lint` |
| SAST | Static application security testing — code-level security analysis without executing the application |
| DAST | Dynamic application security testing — runtime security testing of a running service |
| Dependency scanning (SCA) | Software composition analysis — scanning dependencies for known vulnerabilities |
| Pre-commit hook | A git hook that runs a fast subset of `project lint` before a commit is created |
| Budget appetite | Qualitative scale (`constrained` / `moderate` / `comfortable` / `generous`) influencing right-sizing and thin-slicing |
| Observability 2.0 | Correlated traces, logs and metrics (OTel), not siloed; local instrumentation works in dev and CI |
| Deployment pipeline | The CD flow: how built artefacts are promoted to environments; evolvable target (container, Lambda, etc.) |
| Build pipeline | Nix-first reproducible build producing deployable artefacts; evolvable build targets |
| Nix-first build | Nix owns the developer toolchain; `project build` runs inside the Nix shell for reproducibility |
