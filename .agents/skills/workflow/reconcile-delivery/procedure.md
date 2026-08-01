# Reconcile Delivery — Procedure

1. Read `PROJECT_PROFILE.toon`, `HANDOFF.toon`, `README.md`, `AGENTS.md`.
2. Read in-flight change proposals under `specs/changes/` and living
   requirements under `specs/capabilities/`.
3. Read architecture overview under `docs/architecture/`.
4. Read ADR summaries under `docs/decisions/`.
5. Walk the repository structure and compare against documented claims.
6. Classify each acceptance item:

   | classification | meaning                                                |
   |----------------|--------------------------------------------------------|
   | `delivered`    | present, tested, documented                            |
   | `changed`      | delivered but differs from the original spec           |
   | `deferred`     | intentionally postponed with a recorded revisit       |
   | `removed`      | intentionally dropped with a recorded reason           |
   | `missing`      | expected by a spec or README but absent without reason |

7. For each `missing` item, either implement it, move it to `deferred`, or
   update the spec to `removed` with a reason.
8. Update:

   - `README.md` runtime architecture, repository structure and delivery state;
   - `AGENTS.md` canonical commands and architecture rules;
   - `PROJECT_PROFILE.toon` facts, inferences and decisions;
   - `HANDOFF.toon` current objective and next actions;
   - architecture overview under `docs/architecture/`;
   - ADR links under `docs/decisions/`;
   - in-flight change status under `specs/changes/`.

9. Archive delivered changes: move `specs/changes/<id>/` to `specs/archive/`
   and fold their deltas into `specs/capabilities/`, or mark delivered in
   place.
