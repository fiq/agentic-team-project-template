---
name: capture-unknowns
description: Capture material unknowns in PROJECT_PROFILE.toon with impact and validation path.
---

# Capture Unknowns

When a material unknown appears, add it to `PROJECT_PROFILE.toon` immediately.

Each unknown needs:

- `id`
- `question`
- `why_it_matters`
- `evidence`
- `working_assumption`
- `consequence_if_wrong`
- `blocking`
- `validation`
- `status`

An unknown does not automatically block work. If non-blocking, continue with an
explicit working assumption.
