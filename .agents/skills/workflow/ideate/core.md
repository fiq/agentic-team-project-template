# Ideate — Core

## Loop

```
knowledge-search ──► team-selection ──► rounds ──► structured spec ──► update-handoff
                                          │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                 ▼                ▼                 ▼
      Intent           Boundary         Delivery         Quality gate
    product-owner      architect        tech-lead        all active
    domain-expert                                         personas
         └──── one concise summary + one bounded question per round ────┘
```

- Cap at 3–4 rounds. Seed with a narrative via `narrative-intake` when given.
- Choose participation per round via `agent-team-fallback`: independent
  subagents for high-stakes/ambiguous rounds, `/sudo` persona switches for
  cheap ones. Record which mode was used and what independence was lost.
- Escalate a genuine deadlock to `adversarial-debate`, not another round.

## Rounds

1. **Intent** — who benefits, first valuable behaviour, explicit non-goals.
2. **Boundary** — smallest sufficient architecture, coupling, dependency
   direction; right-size against the calibrated audience (state exclusions,
   get buy-in).
3. **Delivery** — thin slice, first failing boundary test, cheapest check.
4. **Quality gate** — re-check the standing quality rule: reuse over
   duplication, in-path debt, docs-in-change, no silent TODOs.
