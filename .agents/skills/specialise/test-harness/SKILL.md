---
name: test-harness
description: Specialise a testing trophy harness from runtime, framework and risk evidence.
---

# Test Harness

Inspect language, framework, application shape, existing tests and CI. Identify
behavioural and integration risks, then select a small testing trophy.

Expose stable commands:

- `.agentic-template/bin/project test`
- `.agentic-template/bin/project integration-test`
- `.agentic-template/bin/project check`
- optional `.agentic-template/bin/project contract-test`
- optional `.agentic-template/bin/project component-test`
- optional `.agentic-template/bin/project e2e-test`

Do not leave generic placeholders after customisation. Unspecialised targets
must fail clearly.
