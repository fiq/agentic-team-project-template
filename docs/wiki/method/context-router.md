---
axis: method
---

# Portable Context Router

The portable context router decides how much context to load for a given task —
not by guessing from a model's name, but by measuring what the model can actually
do. This page explains why that matters and how it works.

## Why this exists

Anthropic removed over 80% of Claude Code's system prompt for Claude 5 generation models
with no measurable loss on coding evaluations ("The new rules of context engineering for
Claude 5 generation models", 2026-07-24). The tempting conclusion is "send less". That is
the wrong lesson to encode in a template that must serve many models and runtimes.

The article's actual findings are about *unhobbling*: rules that existed to stop weaker
models from failing now cost capable ones reasoning, because they must reconcile
overlapping and contradictory guidance before deciding anything. Excess static context
also buries the project-specific constraints that a model genuinely cannot infer.

But a template does not know which model will read it. The same repository is opened by a
frontier model in one session and a small local model in the next, in Claude Code today
and a bare shell harness tomorrow. A fixed context size is wrong for one of them
whichever size is chosen.

So this repository routes context instead of fixing it.

## The principle

**Route context depth and timing. Do not route required behaviour.**

```
varies by profile                    identical under every profile
─────────────────                    ────────────────────────────
what is preloaded                    acceptance criteria
what is deferred                      safety boundaries
when deeper sources load             deterministic validation
how explicit the procedure is        quality gates
how much verification is required    human approval points
                                     irreversible-action safeguards
```

A capable model on low-risk work should not receive a large procedural prompt it does not
need. A less reliable model, an unfamiliar runtime or high-risk work should receive
explicit process, verification and stopping conditions. Neither gets a different
definition of done.

## How it decides

Three profiles — `lean`, `standard`, `guarded` — chosen by a precedence chain in which
every step can only raise the profile: a maintainer override, then fixture-scored
qualification, then recorded degradation, then the task-risk floor, then a hard guard for
irreversible work. Uncertainty of any kind resolves to `standard`, never `lean`.

Capability is never inferred from a model's name, parameter count or reputation. It is
measured by `project context qualify`, which scores observable behaviour against a
synthetic fixture: does it read the contract from disk, resolve a skill path through the
catalog, use the command facade, honour a stop condition, ground an answer in a file, and
recover after being handed a wrong path. A model that claims capability and fails the
fixture is routed to `standard`.

## Why not a model registry

Cataloguing models does not survive contact with reality: new models appear weekly,
self-reported identity can be wrong or absent, and the same model behaves differently in
different runtimes. A registry would also make the router a maintenance burden with a
permanently stale table at its centre. Model identity is recorded for diagnostics and for
matching explicit overrides, and for nothing else.

## Why recovery comes before more context

When output degrades, the reflex is to add instructions. Usually the real fault is a
stale source: a guessed skill path, a missed operating rule, an outdated architecture
assumption. So the policy is to reload the authoritative source named in
`.agents/context/RECOVERY.toon`, allow one bounded retry, and only escalate the profile if
that fails. Every entry in a context plan carries its source path and digest so the
reload can be targeted rather than wholesale.

## Why methodology and product are separated

Documenting how we work and documenting what we are building are different jobs with
different owners. Methodology is inherited from the template and changes when practice
changes; product documentation is written by the project and changes when the domain
changes. Interleaving them means a generated project's users read template operating
procedure next to their own domain model, and agents cannot tell which pages they should
rewrite.

Every wiki page therefore declares an `axis` — `method` or `product` — matching its
directory, enforced by `project context check`. The axis is orthogonal to the taxonomy
layer: the axis says who owns a page, the layer says how much of it to load now.

## What this deliberately is not

- Not an exhaustive model registry.
- Not a benchmark platform.
- Not a vendor-specific prompt framework: adapters differ only in entry-point filename,
  skill loading, command invocation and tool discovery, never in workflow content.
- Not a hidden adaptive system: every decision is printed by `project context explain`
  with its reasons and precedence trace.
- Not host auto-memory. It is portable, versioned and reviewable in a pull request,
  which host-managed memory is not.
- Not an MCP server. The router is a file-based resolver that runs as a shell
  command; an agent runs `project context explain` and reads the output. Wrapping
  it in an MCP server would add a runtime dependency and a network boundary for
  no gain — the agent still needs filesystem access to read the preloaded files.

## Related

- [Wiki index](../index.md) — all durable project docs, split by axis.
- `docs/context-store.md` — the four repository layers the router draws sources from.
- `.agents/context/README.md` — configuration reference.
- `.agents/skills/tooling/context-qualification/SKILL.md` — running qualification.
