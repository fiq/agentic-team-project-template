---
name: init
---

# /init Orchestrator

## Outcome

Specialise the project from evidence, not preference shopping.

## Procedure

1. Read `AGENTS.md`.
2. Read `HANDOFF.toon`.
3. Read `PROJECT_PROFILE.toon` if present.
4. Read `CUSTOMIZE_THIS_PROJECT.toon`.
5. Inspect repository evidence with `scripts/inspect-project`.
6. Load `.agents/skills/CATALOG.toon`.
7. Load only relevant discovery skills.
8. Update `PROJECT_PROFILE.toon` with facts, inferences, decisions and unknowns.
9. Classify unknowns as blocking or non-blocking.
10. Re-evaluate `LICENSE`; keep MIT only if compatible with project intent,
    dependencies and copied upstream code. Remove temporarily when uncertain.
11. Invoke only relevant specialisation skills.
12. Recommend the smallest useful architecture with confidence and evidence.
13. Ask only remaining high-impact questions.
14. Specialise test harness.
15. Specialise SQL migrations if relational persistence exists.
16. Specialise container build only when packaging or deployment requires it.
17. Specialise CI through repository commands.
18. Inspect tooling, Superpowers and MCP expectations.
19. Run validation.
20. Update `HANDOFF.toon`.

## Do not

- Load every skill.
- Ask a giant technology checklist.
- Treat `npx` as a runtime.
- Add infrastructure merely because it is available.
- Duplicate `AGENTS.md` into tool-specific files.
