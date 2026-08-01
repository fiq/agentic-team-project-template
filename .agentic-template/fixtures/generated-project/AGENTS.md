# Pricing Service — Operating Contract

## Session startup

Read `AGENTS.md` from disk before substantive answers or tool calls. Then run
`.agentic-template/bin/project context explain --skill <skill> --paths <files>` and load
what it lists.

## Project identity

A pricing service. Primary consumer: the checkout flow.

## Hard boundaries

- Never commit directly to `main`.
- Never change a published price rule without an approved change spec.

## Local gotchas

- Skill paths resolve through `.agents/skills/CATALOG.toon`; never guess one.
- Scripts under `.agentic-template/bin/` are internal; use `project <command>`.

## Commands

Run `.agentic-template/bin/project help`.
