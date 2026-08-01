# Review Loop — Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| The pass grew into a refactor of untouched code | scope taken from the repository rather than the diff | reset the out-of-scope edits; record them as a follow-up change |
| Cleanups applied with tests red | verification skipped between passes | revert to the last green state and re-apply one cleanup at a time |
| A shared utility extracted on a single occurrence | pre-abstraction | inline it; extract at the second occurrence |
| Findings disappear after the session | recorded in prose instead of the knowledge graph | re-record as `RISK-` or `PAT-`, or as a change proposal |
| Third and fourth passes with diminishing findings | a design disagreement being relitigated | escalate to `adversarial-debate` with a per-persona stance |
| Correctness bugs reported as smells | review-loop used in place of code review | run code review; keep this pass on quality |
