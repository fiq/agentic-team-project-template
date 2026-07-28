# Context Router Configuration

`project context explain` decides how much of this repository to load for a task and
prints why. Reasoning and design live in
[the method wiki](../../docs/wiki/method/context-router.md).

| File | Owner | Purpose |
|---|---|---|
| `ROUTER.toon` | template | Profiles, precedence, risk floors, effort directives |
| `runtimes.toon` | template | Runtime detection and capability declarations |
| `RECOVERY.toon` | template | Symptom to authoritative source; stop conditions |
| `qualification/` | template | Probe contract, expected answers, answer schema |
| `overrides.toon` | template | Shared overrides; ships empty |
| `TOPICS.toon` | project | One canonical home per topic; `candidates` is the dedupe ledger |
| `risk-rules.toon` | project | Path globs to task risk |
| `overrides.local.toon` | project | Project overrides; never scaffolded over |
| `observations/` | project | Recorded qualification and degradation evidence |

## Commands

| Command | Effect |
|---|---|
| `project context explain` | Print the decision and the context plan |
| `project context qualify` | Emit the probe pack; `--score <file>` grades it |
| `project context observe` | Record a degradation or a clean run |
| `project context check` | Validate config, taxonomy, wiki axes and canonical sources |
| `project context scaffold --into <dir>` | Install the router into a project |
| `project context test` | Run the router test suite |

## Committing observations

The template ignores `observations/*.toon` because they describe one machine's
environment. A project with a stable CI runtime may commit them instead, to share
qualification evidence across the team. Record the choice in `PROJECT_PROFILE.toon`.
