# AI-first Project Template

This is a reusable, opinionated template for software projects where AI agents
reduce decision fatigue. It favours evidence-driven `/init`, concise semantic
state, composable skills, Nix-owned developer tooling, thin vertical slices,
test-first work, optional Superpowers workflow support, and practical Clean
Architecture boundaries.

It is not an internal developer platform. It does not install a default
database, broker, cloud emulator, Kubernetes stack, Java, Python, Node, Elixir
or Godot. Those choices are inferred from project evidence when the template is
instantiated.

```
                      AGENTS.md
                    operating rules
                          |
                          v
                         /init
                          |
                  evidence discovery
                          |
                          v
                PROJECT_PROFILE.toon
                          |
         +----------------+----------------+
         |                |                |
         v                v                v
       facts          inferences        unknowns
         |                |                |
         +----------------+----------------+
                          |
                          v
                composable subskills
                          |
         +----------------+----------------+
         |                |                |
         v                v                v
      runtime          testing       persistence
         |                |                |
         +----------------+----------------+
                          |
                          v
                     active spec
                          |
                          v
                     thin slice
                          |
                          v
                  acceptance evidence
                          |
                          v
                    HANDOFF.toon
                          |
                +---------+---------+
                |                   |
                v                   v
               wiki                ADRs
```

## Start

Use this repository as the starting point for a new project, then let the
agentic bootstrap inspect evidence before choosing runtime, persistence,
messaging, deployment or test harness details.

### 1. Create your project from this template repo

Start by creating a new project repository from this template repository.

- On GitHub, use **Use this template** and clone the generated repository.
  Choose **Private** during repository creation if the project should not be
  public.
- Locally, copy or clone this repository into a new project directory and point
  `origin` at the new project repository.

Do the remaining steps inside the new project repository, not in the template
source repository.

### 2. Provide briefs, artifacts and intent

Bring whatever project material exists. It does not need to be polished.

- Update `CUSTOMIZE_THIS_PROJECT.toon` with anything already known: name,
  purpose, users, core capabilities, non-goals and hard constraints.
- Add briefs, product notes, research notes, architecture sketches, API drafts,
  source files, package manifests, deployment constraints, screenshots or links
  to relevant external systems.
- If the intent is still fuzzy, ask the agent to interview you. It should use
  the material you provided, ask the smallest useful question set, capture
  assumptions and unknowns, then turn the answers into project state.

### 3. Start the agent-guided setup

In Claude, Codex or another coding agent, ask it to read `AGENTS.md` and run the
template bootstrap if the repo instructions were not loaded automatically. A
useful first prompt is:

```text
Help me initialise this project from the template.
If AGENTS.md or CLAUDE.md was not loaded automatically, read it first.
Run .agentic-template/bin/project init, inspect the result, and guide me through
the smallest useful next setup steps. If my project intent is unclear, interview
me and help convert my answers, briefs and artifacts into project state.
```

Enter the Nix development shell if you use flakes:

```sh
nix develop
```

Run the project bootstrap and checks:

```sh
.agentic-template/bin/project init
.agentic-template/bin/project check
.agentic-template/bin/project doctor
```

`init` reads `AGENTS.md`, `HANDOFF.toon`, `PROJECT_PROFILE.toon`,
`CUSTOMIZE_THIS_PROJECT.toon`, repository evidence and
`.agents/skills/CATALOG.toon`. It loads only relevant skills, inspects project
evidence, recommends the smallest useful architecture, and asks only
high-impact unresolved questions.

### Illustrative example

This is README-only sample input, not project state committed elsewhere in the
template. For a new project called `field-notes`, create the repository from
this template, then make the first project intent explicit in
`CUSTOMIZE_THIS_PROJECT.toon`:

```toon
project:
  name: field-notes
  purpose: offline-first notes for field researchers
  status: bootstrap

domain:
  summary: capture, tag and sync field observations
  primary_users:
    - field researcher
    - research coordinator
  core_capabilities:
    - write notes offline
    - attach photos and locations
    - sync when connectivity returns
  non_goals:
    - public social publishing
    - real-time multiplayer editing
```

Then run:

```sh
.agentic-template/bin/project init
.agentic-template/bin/project inspect
.agentic-template/bin/project check
```

If no application evidence exists yet, the template should remain
unspecialised. Add the smallest useful evidence next, such as
`docs/product/README.md` or a runtime manifest like `package.json`,
`pyproject.toml`, `pom.xml`, `mix.exs` or `project.godot`, then rerun `init`.

## Core files

| File | Purpose |
|---|---|
| `AGENTS.md` | Canonical operating contract |
| `CLAUDE.md` | Symlink to `AGENTS.md` |
| `PROJECT_PROFILE.toon` | Current project facts, inferences, decisions and unknowns |
| `HANDOFF.toon` | Current semantic work state |
| `CUSTOMIZE_THIS_PROJECT.toon` | Bootstrap contract for generated projects |
| `.agents/skills/CATALOG.toon` | Lazy-loading skill router |
| `.agents/knowledge/` | Durable knowledge, questions, learnings and proposals |
| `.agentic-template/bin/project` | Hidden boilerplate command dispatcher |

## Practices

- Use TOON for compact current state and coordination contracts.
- Use Markdown for durable explanation, wiki, specs and ADRs.
- Capture material unknowns immediately in `PROJECT_PROFILE.toon`.
- Search `.agents/knowledge/` before creating new guidance.
- Capture new learnings as proposals before promoting them to canonical
  knowledge.
- Prefer recommendations with evidence over technology shopping lists.
- Prefer thin slices, acceptance evidence and local feedback.
- Use test-first development where behaviour can be specified usefully.
- Use the testing trophy: strong fast feedback plus integration confidence.
- Use Clean Architecture only where boundaries reduce coupling.
- Use migrations for production relational schema evolution.

## Agents and models

The default topology supports a project lead with Product, Architect and Tech
Lead responsibilities. Subagents handle bounded research, exploration, review,
security, testing and performance checks. Claude, Codex and other large-context
models are routed by task suitability, but direct user addressing wins.

## Tooling

Nix owns developer tooling. Containers are for application packaging or local
runtime topology when evidence justifies them. Compose starts empty. CI calls
`.agentic-template/bin/project` commands and does not require interactive AI tooling,
Superpowers, MCP servers or external models.

The template works with Superpowers when it is available: agents may use it for
brainstorming, planning, TDD, debugging, implementation, review and
verification. Superpowers is detected as optional tooling, so a new project can
still start cleanly in Claude, Codex, Copilot or CI without it.
