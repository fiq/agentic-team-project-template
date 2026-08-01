# Ideate — Procedure

## Hard choices: persona stance

At a genuinely hard choice, attribute each relevant persona's stance:

```
choice: put persistence behind a port now vs. inline
  architect     encourages  (protects a volatile boundary)
  tech-lead     accepts     (small extra indirection, testable)
  product-owner discourages (no user-visible value this slice)
```

Lead owns synthesis; do not force consensus. Prefer ASCII and bullets; put the
conclusion first.

## Output

- `specs/changes/<id>/` with `proposal.md` (why) and a structured change
  artifact (deltas + `WHEN/THEN` scenarios + acceptance + tasks), validated by
  `project check-changes`;
- `HANDOFF.toon` updated;
- knowledge captured or questions recorded via `knowledge-capture`.
