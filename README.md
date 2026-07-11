# AI-first Project Template

This is a reusable, opinionated template for software projects where AI agents
reduce decision fatigue. It favours evidence-driven `/init`, concise semantic
state, composable skills, Nix-owned developer tooling, thin vertical slices,
test-first work, and practical Clean Architecture boundaries.

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

Run:

```sh
.agentic-template/bin/project init
.agentic-template/bin/project check
.agentic-template/bin/project doctor
```

`/init` reads `AGENTS.md`, `HANDOFF.toon`, `PROJECT_PROFILE.toon`,
`CUSTOMIZE_THIS_PROJECT.toon`, repository evidence and `.agents/skills/CATALOG.toon`.
It loads only relevant skills, updates project facts and unknowns, recommends
the smallest useful architecture, then asks only high-impact unresolved
questions.

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
