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
