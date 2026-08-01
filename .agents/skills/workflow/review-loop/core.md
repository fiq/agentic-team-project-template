# Review Loop — Core

## What to look for

```
boy-scout        dead code, stale TODOs, unclear names in the change's path
code smells      long method, large class, duplication, feature envy,
                 primitive obsession, shotgun surgery
language smells  load the matching specialise/runtime-* "Language smells"
                 section lazily for the project's language
architectural    dependency cycles, layering violations, god modules,
                 leaky abstractions (architect persona)
coupling         inappropriate coupling; wrong dependency direction; a change
                 that ripples across many modules
```

## Rules

- Follow the boy-scout rule: leave code in the path of a change cleaner than you found
  it.
- Reuse over duplication: extract shared utility at the second or later occurrence,
  never on a single one. Do not pre-abstract.
- Refactor only with tests green, and keep changes within the diff's scope.
- Pay down technical debt directly in the work's path. Record out-of-scope debt as a
  `RISK-` or `PAT-` knowledge entry or a follow-up change — never a silent TODO.
- Documentation lands in the same change as the behaviour it describes.
- Cap the pass at two rounds. Escalate a genuine design disagreement to
  `adversarial-debate` with a per-persona stance rather than a third round.
