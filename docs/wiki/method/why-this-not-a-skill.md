---
axis: method
---

# Why This, And Not Just A Skill File

The fair version of the objection, the one worth answering:

> I've been doing this a while. I have a `CLAUDE.md` I like, a few skill files,
> and my own conventions. I can commit those to any repo in about ten minutes.
> What does a whole template actually buy me?

Nothing, on day one, on one repo, working alone. That version of the objection
is correct and this page will not argue with it.

It stops being correct at the second repo, the second person, the second agent,
or the first time someone has to pick up work they did not start.

**The short answer: a skill file tells an agent what to do. This makes the
repository able to check whether it happened.** Everything else follows from
that one difference.

```
skill file        prose an agent may follow  ──►  drift is invisible
this template     prose + gates that fail    ──►  drift stops the build
```

---

## The seven things you cannot get from a file you write yourself

| | What it gives you | Why a skill file cannot |
|---|---|---|
| **1. Executable rules** | Contract violations fail a command | Prose has no failure mode |
| **2. A knowledge base with an ontology** | Decisions survive the session that made them, with provenance | Notes rot; nothing checks a broken reference or an untested claim |
| **3. Bounded subagents** | Independent challenge, controlled context | One agent reviewing itself is not review |
| **4. One contract, every agent** | Your teammate's Codex reads what your Claude reads | Per-tool files drift apart immediately |
| **5. Composes with your toolchain** | Uses Superpowers when present, works without it | No boundary to defer across |
| **6. A repeatable starting point** | Project two starts where project one ended | Copy-paste loses the reasoning |
| **7. Opinionated scaffolds** | Reversible decisions pre-made, so you think about the domain | You still make every call yourself, every time |

The rest of this page is the detail behind each.

---

## 1. Rules that fail, not rules that are merely written

This is the load-bearing difference. Everything else is downstream.

A hand-written contract is a request. The agent reads it, and then it either
complies or it doesn't — and nothing in your repository can tell the
difference. You find out in review, if the reviewer remembers what the rule
was. Usually you find out later than that.

Here the contract is backed by commands that pass or fail:

```
project check    9 gates: repo contract, profile, handoff, knowledge,
                 specs, tooling, MCP, secrets, context router
project ready    the above + lint, build, tests, container, compose, IaC
project hooks    the fast subset, concurrently, before a commit exists
```

Concretely, all of these stop being possible:

- an agent skipping a required section of `HANDOFF.toon` → `check-handoff` fails;
- an agent inventing a knowledge link to a node that was never written →
  `check-knowledge` fails;
- an agent quietly duplicating canonical guidance into a second file →
  the topic check fails;
- a credential reaching a commit → the pre-commit gate blocks it;
- a wiki page landing in the wrong place → the axis check fails.

None of those depend on a human noticing. That is the whole point:
**conformance moves out of reviewer memory and into the build.**

> **New to this?** The practical effect is a safety net. You can act
> confidently, because the repository will tell you when you have gone
> off-contract instead of letting you discover it in review three days later.
> The gates are also the fastest way to learn the conventions — they name the
> rule and the file when they fail.

---

## 2. A knowledge base with an actual ontology

`.agents/knowledge/` is not a notes folder with good intentions. It is a
small, git-native knowledge base with a declared ontology, typed edges,
provenance, a review lifecycle, and validation.

**Entities are typed and addressable.** `DOM-` domains, `SYS-` systems,
`CON-` contracts, `ARCH-` architecture, `ADR-` decisions, `PAT-` patterns,
`RISK-` risks, `Q-` open questions, `LRN-` learnings — plus `CAP-`
capabilities and `CHG-` changes from the spec system, and `INBOX-` for
unreviewed proposals.

**Relations are declared, not implied.** `relates_to`, `depends_on`,
`consumes`, `produces`, `decisions`, `patterns`, `risks`, `open_questions`,
and the lifecycle edges `supersedes` / `superseded_by` / `contradicts`:

```
CAP-004 ──consumes──► CON-002 ──produced_by──► SYS-001
   │                                              │
   └──decisions──► ADR-007 ◄──risks── RISK-003 ───┘
                      │
                      └──supersedes──► ADR-002
```

**The edges are checked.** A dangling reference fails `check-knowledge`. A
spec citing a knowledge ID nobody wrote fails `check-changes`. You cannot
accumulate a graph that quietly lies about itself.

### The ontology is extensible, on purpose

`TAXONOMY.md` defines the node and edge types;
`.agents/schemas/knowledge-entry.schema.md` defines the entry format and the
type-to-prefix registry; `.agents/knowledge/templates/` holds a template per
type. Adding a type to your project's ontology is a documented five-step
procedure, not a fork:

```
1. add a folder under .agents/knowledge/
2. add a concise template in templates/
3. register the type and ID prefix in the schema
4. extend check-knowledge if validation rules change
5. link the type from the knowledge index
```

So the ontology starts general and becomes *yours*. A payments platform grows
`OBLIG-` regulatory obligations; a games studio grows `MECH-` mechanics; a
data platform grows `DATASET-` lineage nodes. The template ships the shape and
the enforcement — your domain supplies the vocabulary.

### Provenance and epistemic hygiene

This is the part that matters once agents are writing into the graph. Every
entry carries `evidence`, a `status`, and review dates:

| Status | Means |
|---|---|
| `canonical` | reviewed and currently trusted |
| `proposed` | plausible, not yet validated |
| `experimental` | deliberately temporary |
| `deprecated` | retained, no longer recommended |
| `superseded` | replaced by another entry |
| `stale` | `review_after` has passed; evidence may no longer hold |

Two rules keep this honest, and both are enforced or checked:

- **Agents must treat non-canonical entries as input, not authority.** A
  proposal does not get to act like a fact because it is written down.
- **Agents cannot self-certify.** Task discoveries go to
  `.agents/knowledge/inbox/` as `INBOX-` proposals and are promoted to
  canonical only with evidence, repetition or review:

```
discovery ──► INBOX proposal ──► review ──► canonical knowledge
              (status: proposed)            (status: canonical)
```

That distinction — between "an agent concluded this once" and "this is what we
know" — is exactly what a flat notes file cannot represent, and it is the
difference between a knowledge base that gets more trustworthy over time and
one that fills with confident guesses.

After meaningful work, `knowledge-capture` runs and `HANDOFF.toon` must record
what was consulted, what was proposed, or a concrete reason nothing was worth
recording. `check-handoff` enforces that the checkpoint exists — you cannot
silently skip the learning step.

### Why this pays off

The payoff is retrieval. *"Which risks touch this capability, and which
decision accepted them, and has that decision been superseded?"* is a
traversal, not a grep — answerable by an agent that was not present when any
of it was decided, and which can tell trusted knowledge from an untested
hunch.

Six months on, the expensive question is never "what does this code do" — you
can read the code. It is **"why is it like this, and what did we already rule
out?"** A folder of notes cannot answer that. A typed graph with enforced
edges, recorded provenance and a promotion gate can.

---

## 3. Subagents: independent challenge, on purpose

Reviewing your own work is weak, whoever "you" are. An agent that wrote a
design and is then asked to critique it will mostly agree with itself.

The template ships **seven bounded subagents** — researcher, repository
explorer, evidence checker, red-team reviewer, test reviewer, and security and
performance reviewers activated by risk. Each declares a task boundary,
required input, expected output, context budget, and a completion condition:

```
Red-team Reviewer
  boundary:   adversarial review of a bounded proposal or patch
  input:      proposal, relevant evidence, acceptance criteria
  output:     findings first, severity, evidence, suggested fix
  budget:     relevant diff and contracts only
  done when:  no further material issues in scope
```

Two things fall out of that shape, and both matter to anyone running agents
seriously:

**Context economy.** A subagent gets the diff and the contracts, not your
repository. Skills are lazy-loaded from a catalog of **68** rather than
pasted in wholesale, and each is layered (`summary` → `core` → `procedure` →
`verification` → `failure-modes`) so only the needed depth is loaded. You are
not paying attention-tax on guidance irrelevant to the task.

**Real disagreement.** Above the subagents sit five persistent roles — product
owner, architect, tech lead, domain expert, knowledge curator. At a hard
choice they take positions rather than merging into consensus mush:

```
choice: add a message broker now
  architect     discourages (no evidence of async need yet)
  tech-lead     accepts     (isolated, reversible)
  product-owner encourages  (unblocks the next capability)
  -> human decides
```

Consensus is never forced. And when the full topology is not available, the
fallback ladder is explicit — persistent team → independent subagents →
sequential role passes → one agent with a checklist — while **recording which
independent challenge was lost on the way down.** Degrading is fine.
Pretending you did not degrade is not.

---

## 4. One contract, every agent — including the ones that don't exist yet

Your teammate uses Codex. You use Claude. Someone opens the repo in Cursor.
Copilot is reviewing the PR.

Without a shared contract that is four sets of conventions drifting apart, and
whichever agent you did not configure quietly does its own thing.

Here there is one contract — `AGENTS.md` — and the adapters are entry points
into it, not copies of it:

```
CLAUDE.md ──symlink──► AGENTS.md ◄── .codex/README.md
                          ▲   ▲
   .github/copilot-instructions.md   .cursor/rules/*.mdc
```

`CLAUDE.md` is literally a symlink. There is no second copy to drift.

Two consequences worth naming:

- **Mixed-agent teams work.** People bring their own tools to the same
  repository and land on the same conventions.
- **Tool churn stops being a migration.** The 2027 agent landscape will not
  look like today's. When it changes, you add an entry point — the contract,
  the knowledge graph, the specs and the checks are plain files in your repo
  that any agent that can read Markdown and run a shell command will
  understand. Nothing here calls a proprietary API.

Portability framed as insurance, not as a headline feature. You are not
betting your process on a vendor.

---

## 5. It composes with what you already run — it does not absorb it

A fair worry about anything calling itself a template: *does it want to own my
whole workflow, and will it reinvent the tools I already have?*

No. The template defines the **AI development lifecycle** — who participates,
what context they get, what must be true before work is accepted, what
survives the session — and then **defers the engineering workflow to a better
layer when one is present.**

Superpowers is the worked example:

```
Superpowers (when available)      This template (always)
──────────────────────────        ──────────────────────
brainstorming                     who participates (roles, subagents)
planning                          what context to load (router, packets)
TDD                               project knowledge and retrieval
debugging                         what changed and what was learned
implementation                    handoff and promotion rules
review, verification              the gates that must pass
```

The boundary is written down and enforced by convention in the skills
themselves: `team-selection` explicitly must not *"replace Superpowers
planning, TDD, debugging or verification workflows"*, and the knowledge
curator role must not replace *"Superpowers review or verification"*. The
template adds local context around that layer; it does not compete with it.

**What "fold in" means here, precisely — and what it does not:**

- **Detected, never assumed.** `tooling/detect-superpowers` checks for
  available capability. `project check` reports it alongside git, Nix, Python
  and Docker as a plain availability line.
- **Nothing is vendored.** No Superpowers skill is copied into this
  repository. There is no bundled fork, no snapshot, no "compatible
  reimplementation" that quietly drifts from upstream.
- **No stand-in, no imitation.** If it is absent, the template does not fake
  the workflow with a lookalike. It simply runs its own loop, which is
  designed to be sufficient on its own.
- **Your global state is not touched.** The detection skill is explicit: *do
  not overwrite global configuration or auto-update user-global plugin
  state.* It records project-local compatibility notes only. A template has no
  business editing your machine.
- **Degradation is graceful and honest.** Claude, Codex, Copilot and CI must
  all still be able to start from `AGENTS.md`, `PROJECT_PROFILE.toon`,
  `HANDOFF.toon` and the repository commands with nothing else installed. CI
  in particular is barred from requiring Superpowers, MCP servers or any
  interactive AI tooling — otherwise the pipeline would depend on a developer
  laptop's configuration.

The same posture applies to MCP servers: declared as `required` or `optional`
in project state, detected rather than assumed, and never silently depended
upon.

This is what makes the template safe to adopt incrementally. It is a layer
that plays well with the ecosystem, not a walled garden that needs to own
everything to be useful. If something better than Superpowers appears next
year, the boundary is already drawn — you swap the workflow layer without
touching the contract, the knowledge graph, or the gates.

---

## 6. Repeatable projects: the pattern is the asset

This is the part most people underestimate.

A skill file is per-repository. Start something new and you copy it, tweak it,
and lose the reasoning behind every decision you made last time. Your third
project is not meaningfully wiser than your first.

The template inverts that. `/specialise` runs an evidence-driven bootstrap:
inspect what is actually in the repository, infer the runtime, recommend the
smallest sufficient architecture, ask only the questions that genuinely change
the answer, and record the result as project state:

```
evidence ──► inference ──► smallest sufficient design ──► recorded decision
   (what's        (what it        (with what is             (+ revisit
    in the repo)   implies)        deliberately excluded)     trigger)
```

**27 specialisation skills** cover runtimes (JVM, Python, Node/TS, Go, Rust,
C#, Ruby, PHP, Perl, Elixir, Godot), persistence, messaging, containers,
static analysis, build, deployment, observability, CI and infrastructure. Not
a closed list — the pattern for adding a runtime is documented and enforced by
tests, so the twelfth language is held to the same bar as the first.

What compounds is not the code. It is the *shape*: the same command surface,
the same state files, the same review loop, the same handoff protocol. Project
two starts where project one ended, and the improvements you made last time
are still there.

---

## 7. Opinionated scaffolds, so you think about the problem instead of the plumbing

Every reversible decision you re-litigate is attention taken from the actual
problem. Where to put tests. Whether to containerise. What the lint config
should be. How to write a handoff. Where architecture decisions live.

None of that is your product. All of it has a defensible default.

So the template decides — and tells you it decided, and tells you how to
change its mind:

| Pre-decided | Left to you |
|---|---|
| Command surface (`project <verb>`) | Your domain model |
| Where state, specs, knowledge live | What you are building and for whom |
| Test posture (trophy + outside-in ATDD) | Which risks deserve which layer |
| Nix owns the toolchain | Your runtime and framework |
| Structured state (TOON) and rules (S-expr) | Your capabilities and contracts |

Opinionated is not rigid. The rules live in readable Markdown you can disagree
with, and right-sizing is explicit: the smaller architecture is a **conscious,
recorded, bought-into** choice, with what was deliberately excluded and the
conditions that would justify revisiting it written down. YAGNI stops being an
unexamined shrug and becomes a decision with a trigger.

There is also a deliberate list of things this is **not**: not an internal
developer platform, not a code generator, not a default database or broker or
Kubernetes. Nothing is added without evidence that the project needs it.

> **New to this?** This is the part that helps most. You are not asked to have
> an opinion about test taxonomy or repository layout before you have written
> anything. The scaffold has a sensible answer, the agent explains it in plain
> language, and `/specialise` calibrates to your experience level rather than
> assuming it. You get to spend your thinking on your problem.

---

## What it costs

The honest side of the trade:

- **More structure to learn** than one file — a command surface, state files,
  a skill catalog.
- **Checks that fail**, which is the point, and is friction when you are
  spiking something throwaway.
- **Ceremony you will not want** on a scratch script or a weekend prototype.
- **Discipline the template cannot supply.** It can enforce that a handoff has
  the required sections. It cannot make them thoughtful.

---

## Who this is for

**Reach for it when** the work has consequences and continuity — decisions are
expensive to reverse, more than one person or agent touches the repository,
sessions need to hand off cleanly, and you expect to still be maintaining this
in a year.

**Skip it when** you are prototyping alone, throwing the code away next week,
or exploring an idea that has not earned structure yet. For a weekend hack, a
skill file genuinely is enough — and this page is not going to pretend
otherwise.

The test is simple: **if losing the reasoning behind a decision would cost
you, the machinery pays for itself. If it wouldn't, it won't.**

---

## The bottom line

Strip away the machinery and the argument is about where your attention goes.

Agentic development has made writing code cheap. It has not made *deciding
what to build, and living with those decisions* cheap. That is where projects
still go wrong: the boundary nobody argued about, the trade-off nobody wrote
down, the reasoning that left with whoever was in the session.

Every mechanism on this page points the same direction:

```
the template handles          so your attention goes to
────────────────────          ─────────────────────────
scaffolding and conventions   the domain and its rules
conformance and drift         the problem worth solving
context and delegation        the trade-offs that are actually yours
memory and provenance         the decisions only you can make
```

A skill file makes an agent more useful in a session. This makes a *project*
that gets sharper over time — where the plumbing is settled, the reasoning is
retrievable, disagreement is structural rather than accidental, and the work
that needs human judgement is the work you actually spend your time on.

That is the pitch. Everything above is just the evidence for it.

---

## Related

- [Portable context router](context-router.md) — why context depth is routed
  by observed behaviour rather than fixed or guessed from model identity.
- [Development](development.md) — the day-to-day loop and the pre-commit gate.
- [Testing](testing.md) — outside-in ATDD, the trophy, and static analysis.
- [Method glossary](glossary.md) — vocabulary for all of the above.
