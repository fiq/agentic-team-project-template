# Repository Operating Contract

## 50,000-foot view

This repository is an AI-first project template. Agents should reduce decision
fatigue by inspecting evidence, recommending sensible defaults, and asking only
the smallest useful question set when material ambiguity remains.

## Canonical rule

`AGENTS.md` is the source of truth for repository behaviour. Other instruction
surfaces must point here instead of duplicating these rules.

## Working model

```
PROJECT
  |
  v
/init
  |
  v
evidence discovery
  |
  v
PROJECT_PROFILE.toon
  |
  +--> facts
  +--> inferences
  +--> decisions
  +--> unknowns
  |
  v
smallest useful architecture
  |
  v
thin slice -> tests -> implementation -> review -> HANDOFF.toon
```

## Required state files

- `PROJECT_PROFILE.toon` records current evidence-backed understanding.
- `HANDOFF.toon` records current semantic work state, not history.
- `CUSTOMIZE_THIS_PROJECT.toon` is the bootstrap contract for new projects.
- Material unknowns must be captured in `PROJECT_PROFILE.toon` as soon as they
  matter. Unknowns do not automatically block work.

## Decision rules

- Infer from repository evidence before asking preference questions.
- Recommend the smallest sufficient architecture.
- Keep facts separate from assumptions and model inference.
- Prefer experiments over long debate where evidence is cheap.
- Use Clean Architecture principles to protect meaningful boundaries, not to
  create ceremony.
- Do not add databases, brokers, Kubernetes, cloud emulators or extra runtimes
  without evidence.
- Developer tooling is Nix-owned. Runtime packaging may use containers when
  appropriate.
- CI must call repository commands instead of duplicating build logic.

## Test rules

- Default to test-first for meaningful behaviour.
- Use a testing trophy: strong unit/domain feedback, strong integration or
  component confidence, focused contracts, and a few high-value E2E paths.
- Unspecialised test targets must fail clearly and point to `make init`.
- Real dependency semantics should be tested when they are cheap and material.

## Agent rules

- Persistent roles are for continuing responsibility.
- Subagents are for bounded work.
- External models are workers, reviewers or consultants.
- Do not send the whole repository to every agent.
- Use `.agents/skills/CATALOG.toon` to lazy-load only relevant skills.
- The project lead owns final synthesis. Do not force consensus.
- Use stronger models only where added capability is likely to matter.

## Communication rules

- Put the most important conclusion first.
- Use concise sections, short paragraphs, small tables and ASCII diagrams.
- Use TOON for compact semantic state and Markdown for durable explanation.
- Prefer progressive disclosure over walls of text.

## Git provenance

Use real commit author and committer dates. Do not set `GIT_AUTHOR_DATE`,
`GIT_COMMITTER_DATE`, `--date`, system time, file mtimes, Makefiles, scripts or
CI to make new work appear to have been created earlier than it was.
