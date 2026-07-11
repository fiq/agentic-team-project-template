# Model Routing Policy

Route by task complexity, uncertainty, impact and reversibility. Use the
cheapest model class likely to complete the bounded task reliably.

## Defaults

Claude:
- persistent team coordination
- architecture synthesis
- product reasoning
- cross-cutting system design
- sustained context

Codex:
- bounded implementation
- repo inspection
- agreed spec implementation
- engineering red-team review
- independent code review
- build and CI repair

Other OpenAI-compatible or large-context models:
- broad corpus analysis
- contradiction detection
- option-space generation
- independent second opinion

Direct user routing wins. Do not secretly reroute a directly addressed task.

## Model Classes

Strong model:
- ambiguity resolution
- architecture synthesis
- risk assessment
- conflict resolution
- high-impact final review

Midrange model:
- bounded planning
- implementation
- test creation
- documentation
- routine review

Lesser or local model:
- mechanical edits
- narrow transformations
- test execution
- indexing
- metadata extraction
- knowledge-link maintenance

Escalate when assumptions conflict, knowledge is missing, architecture
boundaries are unclear, tests repeatedly fail, security or privacy risk is
material, a public contract changes, the task cannot be safely decomposed, or
reviewers disagree.
