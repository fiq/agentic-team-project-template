# Ship Slice — Verification

The gate, in order:

1. `.agentic-template/bin/project test` — the acceptance scenario passes with the flag on.
2. The flag-off regression test passes — old behaviour is unchanged when the flag is off.
3. `git diff --check` — no whitespace damage.

Do not claim a slice is shipped without both tests green.
