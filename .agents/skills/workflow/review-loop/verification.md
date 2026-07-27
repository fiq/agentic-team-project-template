# Review Loop — Verification

The gate, in order:

1. `.agentic-template/bin/project test` — green before and after every cleanup.
2. `.agentic-template/bin/project check` — repository contract, profile, handoff,
   knowledge, specs and router configuration.
3. `git diff --check` — no whitespace damage introduced by the pass.

Evidence to record in `HANDOFF.toon.tests_run`: the date, each command and its result.

Do not claim a clean-up without a green run. If the harness itself is broken, repair it
without losing representative coverage, and say so.
