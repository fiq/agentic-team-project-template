# Ship Slice — Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| Flag flipped on but behaviour unchanged | the slice was not wired behind the flag | verify the flag gate is on the correct code path |
| Old behaviour broken with flag off | the slice touched shared code without guarding | revert and re-implement behind the flag |
| Scenario passes but production breaks | the test did not cover the real data path | add a test against production-shaped data before flipping |
