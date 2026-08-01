# Validation

What checks prove and where to record them.

## Checks

- `.agentic-template/bin/project context check` — validates router config, taxonomy and
  canonical sources.
- `.agentic-template/bin/project context explain --skill <skill> --risk <risk>` — renders
  the context plan for a task.

## Recording

Record test results in `HANDOFF.toon.tests_run`: the date, each command and its result.
