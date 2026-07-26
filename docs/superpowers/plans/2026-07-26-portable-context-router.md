# Portable Context Router Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a portable, explainable context router into this template so that
generated projects can route the depth and timing of their own workflow, skill,
knowledge, verification and recovery context across Claude Code, Codex, OpenCode, Roo
and plain shell harnesses — without vendor-specific copies of any workflow or skill.

**Architecture:** The router is a deterministic resolver, not a prompt framework. A pure
function maps `(environment, task, router config, overrides, observations)` to one of three
context profiles (`lean` / `standard` / `guarded`), and the profile selects which
*taxonomy layers* of already-existing documentation get preloaded versus deferred. It
never changes required outcomes. `project context explain` renders the decision, the
preload/defer sets with source provenance, the required verification and the recovery
map. `project context qualify` scores observable behaviour against a synthetic fixture
repository rather than trusting model self-reports.

**Tech Stack:** Python 3 standard library only (matches the existing
`.agentic-template/bin/` tooling), TOON for state and contracts, YAML frontmatter for
skill metadata, `unittest` for the test suite.

## Global Constraints

- Python 3 standard library only. No new runtime dependencies, no external spec CLI, no
  vector store, database or SaaS memory layer.
- The router routes *context depth and timing only*. Acceptance criteria, safety
  boundaries, deterministic validation, quality gates, human approval points and
  irreversible-action safeguards are identical under every profile.
- No vendor-specific copies of any workflow or skill. Adapters may differ only in
  entry-point filename, skill-loading mechanism, command invocation, tool discovery and
  structured-output shape.
- No exhaustive model registry. Model identity is recorded for diagnostics and explicit
  override matching only, and must never be a capability signal.
- Agents invoke `.agentic-template/bin/project <command>`; scripts under
  `.agentic-template/bin/` are internal. Skill paths resolve through
  `.agents/skills/CATALOG.toon` and are never guessed.
- Each fact has exactly one canonical home. Other files summarise, sequence, verify,
  illustrate or link — never redefine.
- Do not create empty layer files to satisfy the taxonomy.
- Structured data: TOON for state and contracts, per
  `PROJECT_PROFILE.toon.structured_data`. Skill frontmatter stays YAML (see assumption
  ASM-4).
- Real commit author/committer dates. No `GIT_AUTHOR_DATE`, `--date` or mtime rewriting.
- Terminology in all documentation: **portable context router**.

---

# Part A — Design Review (approve before Part B executes)

The spec asked to stop before broad migration and show the architecture. Part A is that
review. Part B is the thin slice only; the broad migration is scoped in "Deferred scope"
and is not implemented by this plan.

## A1. Evidence inspected

`project startup`; `AGENTS.md` (367 lines, 21 sections); `PROJECT_PROFILE.toon` (274);
`HANDOFF.toon`; `CUSTOMIZE_THIS_PROJECT.toon`; `.agents/skills/CATALOG.toon` (223, 50
entries); all 58 `SKILL.md` files; the seven `.agents/coordination/*_POLICY.md` files;
`.agents/knowledge/TAXONOMY.md`; `docs/README.md`, `docs/context-store.md`,
`docs/validation.md`; `.agentic-template/bin/{project,startup,check-repo-contract,project-ready,self-test,bootstrap-project,check-tooling}`;
`.agentic-template/templates/{AGENTS_TEMPLATE,README_TEMPLATE}.md`; the four host shims
(`.claude/`, `.codex/`, `.cursor/`, `.github/copilot-instructions.md`); `nix/checks.nix`;
`.github/workflows/ci.yml`.

Plus the source article: Thariq Shihipar, "The new rules of context engineering for
Claude 5 generation models", Anthropic blog, 2026-07-24.

### Article principles mapped to design elements

Each row is a claim from the article and the part of this design that carries it as a
*portable* principle rather than a Claude-specific rule.

| Article principle | Where it lands |
|---|---|
| Rules → judgement; deleted guardrails newer models no longer need | `lean` preloads summary only; A2 marks generic advice for deletion, not relocation |
| Conflicting messages across system prompt, skills and requests cost reasoning | D1-D9; `TOPICS.toon` canonical-marker check makes single-home enforceable (A7) |
| Examples → expressive interfaces; examples constrain the exploration space | A4; argparse enums for risk/effort/profile; `examples` layer is never preloaded and is optional |
| Everything upfront → progressive disclosure, including deferred tool loading | The seven-layer taxonomy; `preload`/`defer` sets per profile |
| Repeat yourself → put guidance in the tool description | D6; command table moves into `project help`; per-command purpose text |
| Memory in CLAUDE.md → auto-memory | **Deliberately not adopted** — see exclusion X1 |
| Simple specs → rich references (test suites, rubrics, artifacts, code) | `references` layer defined as tests, schemas, rubrics, artifacts and executable examples; `review_rubric` is a first-class `guarded` preload |
| Lightweight CLAUDE.md: repo purpose plus gotchas; avoid stating the obvious | A3's target shape — Session startup / Project identity / Hard boundaries / Local gotchas / Commands / Context routing / Where things live |
| Split long skills across many files | Task 10 and Task 11 migrate the two example skills exactly this way |
| Skills encode opinions particular to you, your team or product | A6's template-owns-mechanism / project-owns-facts boundary |
| `claude doctor` rightsizes skills and CLAUDE.md automatically | This repo already has `project doctor`; extending it to report router rightsizing is deferred scope item 6 |

Two article points deserve explicit treatment because they cut against a naive reading of
the spec. First, the article's lesson is *unhobbling*, not token minimisation — which is
why this design's ladder can raise a profile as easily as lower it, and why `standard`,
not `lean`, is the default under any uncertainty. Second, the article's `/doctor` is a
Claude Code feature; the portable equivalent here is a repository command any runtime can
execute, which is the whole reason the router lives behind `project context`.

## A2. Duplication, conflicts and prescriptiveness found

Each finding names the file that should keep the fact (canonical) and the files that
should shrink to a pointer.

| # | Finding | Canonical home | Duplicates |
|---|---|---|---|
| D1 | The model-class lists (strong / midrange / lesser, plus the escalation trigger list) appear three times, near-verbatim | `.agents/skills/tooling/model-routing/SKILL.md` | `.agents/coordination/MODEL_ROUTING_POLICY.md` (lines 26-58), `AGENTS.md` "Team and model fallback" (39 lines) |
| D2 | The handoff protocol before switching model/provider appears twice, as identical 7-step lists | `.agents/schemas/handoff.schema.md` | `AGENTS.md` "Team and model fallback", `tooling/model-routing/SKILL.md` |
| D3 | Context-packet rules (summarise meaning not bytes, source refs, no opaque blobs, do not resend) appear twice | `.agents/skills/tooling/context-packet/SKILL.md` | `.agents/coordination/CONTEXT_POLICY.md` items 4-6, 9, 10 |
| D4 | The architecture-fitness-function candidate list appears three times, near-verbatim | `docs/validation.md` | `docs/context-store.md` "Fitness Functions", `AGENTS.md` "Context store", `README_TEMPLATE.md` item 8 |
| D5 | Communication structure and style rules appear twice | `.agents/coordination/COMMUNICATION_POLICY.md` | `AGENTS.md` "Communication rules" (20 lines) |
| D6 | The canonical-command table (21 rows) is maintained by hand in Markdown while `project help` prints the same surface from code | `project help` output | `AGENTS.md` "Canonical commands" (34 lines) |
| D7 | The session-startup paragraph is copied into six files and pinned by eight `check_required_text` assertions in `check-repo-contract` | `AGENTS.md` "Session startup" | `AGENTS_TEMPLATE.md`, `.codex/README.md`, `.claude/README.md`, `.claude/skills/agentic-template/SKILL.md`, `.cursor/rules/agentic-startup-and-skills.mdc`, `.github/copilot-instructions.md` |
| D8 | Quality/boy-scout rules appear twice | `workflow/review-loop/SKILL.md` | `AGENTS.md` "Quality and technical debt" (18 lines) |
| D9 | Testing-trophy and boundary-fidelity guidance appears twice | `workflow/outside-in-tdd/SKILL.md` | `AGENTS.md` "Testing expectations" (19 lines) |

**Conflicts**

- **C1 — unreachable skills.** `AGENTS.md` says skill paths must resolve through
  `CATALOG.toon` and must never be guessed, but eight skills are absent from the catalog:
  `workflow/architecture-review`, `workflow/discover`, `workflow/implement-slice`,
  `workflow/plan-task`, `workflow/promote-knowledge`, `workflow/red-team`,
  `workflow/specify`, `workflow/test-change`. Following the contract makes them
  unreachable; reaching them requires breaking the contract. The router cannot be
  correct while this holds — it resolves paths through the catalog by construction.
- **C2 — unenforced contract.** `check-repo-contract` requires 33 named skills and
  validates frontmatter, but never checks catalog↔filesystem agreement, which is why C1
  survived.
- **C3 — tests outside CI.** `project self-test` (754 lines) is in neither
  `project check` nor `project ready` nor `.github/workflows/ci.yml`. The template's
  richest behavioural suite never runs automatically.
- **C4 — preload volume.** `CLAUDE.md` symlinks to `AGENTS.md`, so every Claude Code
  session in this repository preloads all 367 lines before any task is known. Codex,
  Cursor and Copilot shims each pull it too. This is the single largest instance of the
  problem the router exists to solve, and D1-D9 mean much of it is redundant with
  content the agent may load again from skills.

**Unnecessarily prescriptive context** (candidates for deletion, not relocation): generic
Clean Architecture advice, generic testing-pyramid rationale, and generic "prefer reuse"
statements in `AGENTS.md` restate what any competent model already does. What is *not*
inferable and must stay: the `project` facade (not Make, not npm scripts), `CLAUDE.md`
being a symlink, `.agentic-template/bin/*` being internal, catalog-resolved skill paths,
TOON control files, and the git-provenance ban.

## A3. Root-file content that should move (migration map)

Every overflow section already has a canonical home elsewhere. **The fix is deletion plus
a pointer, not a new documentation tree** — which also avoids the "duplicated short and
long documentation trees" outcome the spec forbids.

| `AGENTS.md` section | Lines | Disposition | Destination (already exists) |
|---|---|---|---|
| Session startup | 15 | Keep, shrink to 6 | — (boot invariant) |
| Project identity | 8 | Keep, shrink to 3 | — |
| Canonical commands | 34 | Delete table, keep 3-line pointer | `project help` |
| Architecture and dependency rules | 14 | Keep 4 "do not add without evidence" lines; drop generic advice | `workflow/architecture-review` |
| Quality and technical debt | 18 | Delete | `workflow/review-loop` core |
| Right-sizing and over-engineering | 15 | Delete | `workflow/ideate` core (round 2) |
| Testing expectations | 19 | Delete | `workflow/outside-in-tdd`, `workflow/test-first` |
| Container and infrastructure rules | 19 | Delete | `specialise/container-build`, `specialise/infra-decision` |
| Documentation update triggers | 13 | Delete | `workflow/wiki-tidy` procedure |
| Structured data formats | 12 | Delete | `docs/structured-data.md` |
| Spec system | 18 | Delete | `workflow/specify` (once catalogued — C1) |
| Knowledge graph and taxonomy | 13 | Keep 2-line pointer | `.agents/knowledge/TAXONOMY.md` |
| Context store | 24 | Keep 2-line pointer | `docs/context-store.md` |
| Branch and PR workflow | 7 | Keep — hard boundary (`main`, force-push) | — |
| Worktree rules | 9 | Keep 2 lines (never remove dirty); rest to skill | `coordination/worktree-status` |
| Agent roles and ownership | 18 | Delete | `coordination/team-selection`, `tooling/context-packet` |
| Team and model fallback | 39 | Delete | `coordination/agent-team-fallback`, `tooling/model-routing` |
| Required state files | 9 | Keep 4-line list | — |
| Handoff requirements | 16 | Delete | `.agents/schemas/handoff.schema.md` |
| Communication rules | 20 | Delete | `COMMUNICATION_POLICY.md` |
| Git provenance | 4 | Keep — hard boundary | — |
| *(new)* Context routing | — | Add 8 lines | `docs/context-router.md` |

Target: **367 → ~85 lines**, structured as Session startup / Project identity / Hard
boundaries / Local gotchas / Commands / Context routing / Where things live.

**This migration is deferred**, not in the thin slice. See "Deferred scope".

## A4. Tool guidance that belongs in the command interface

| Guidance now in prose | Moves into |
|---|---|
| D6 command table | `project help`, extended to print each command's purpose (it currently prints bare names) |
| "unspecialised commands fail clearly and point to init" | already the behaviour of `fail_unspecialised()`; delete the prose |
| Which checks `project check` runs | `project check --list` |
| Context-packet budget table (`small`/`medium`/`large`) | `project context explain` `effort_directives`, computed from profile + effort |
| "search knowledge before planning" | `project context explain` emits the knowledge index in every profile's preload set |
| Valid values for risk/effort/profile | argparse enums with deterministic error text, plus `.agents/context/ROUTER.toon` as the schema |

## A5. Proposed architecture (smallest coherent form)

```
         inputs (all optional, all explicit)
         ┌───────────────────────────────────────────────┐
         │ AGENTIC_MODEL_ID / --model   (diagnostics +    │
         │                               override match)  │
         │ runtime detection / --runtime                  │
         │ --risk {low,normal,high,irreversible}          │
         │ --effort {minimal,standard,deep}               │
         │ --skill <id> | --trigger <trigger>             │
         └───────────────────────────────────────────────┘
                            │
                            ▼
  ┌──────────────────────── resolve() — pure, no I/O ─────────────────────────┐
  │ 1 force override      .agents/context/overrides.local.toon > overrides.toon│
  │ 2 qualification       observation for this fingerprint: pass/fail/uncertain│
  │ 3 degradation floor   escalation recorded against this fingerprint         │
  │ 4 task-risk floor     ROUTER.toon risk_floors                              │
  │ 5 irreversible guard  high|irreversible ⇒ at least guarded                 │
  │                       (each step can only raise: max() over the ladder)    │
  └───────────────────────────────────────────────────────────────────────────┘
                            │  profile ∈ {lean, standard, guarded}
                            ▼
  ┌────────────────── plan() — profile selects taxonomy layers ───────────────┐
  │ preload  = always_preload[profile] + layers[profile] ∩ skill.layers        │
  │ defer    = skill.layers − preload                                          │
  │ verify   = skill.verification            (identical in every profile)      │
  │ recover  = RECOVERY.toon symptom → authoritative source                    │
  │ effort   = effort directives             (never alters profile)            │
  │ every entry carries source path + sha256 for targeted recovery             │
  └───────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        project context explain            (human + TOON output)
```

Three properties make this the smallest form that satisfies the spec:

1. **The profile is an index into the taxonomy, not a content set.** No profile owns any
   text. Adding a profile means adding a row of layer names; adding a skill means adding
   layer files. There is no short/long duplicate tree.
2. **`resolve()` is pure and total.** Every input is data; the only I/O is loading TOON.
   That is what makes the 15-case precedence table testable as a unit.
3. **Runtime capability is data, not code.** `.agents/context/runtimes.toon` declares what
   each host can do. An unknown runtime resolves to minimal capability and therefore to
   `standard`. No vendor branches exist anywhere in the workflow or skill tree.

## A6. Template versus generated-project responsibilities

| | Template owns (mechanism + defaults, updatable) | Generated project owns (facts + policy values) |
|---|---|---|
| Policy | `.agents/context/ROUTER.toon` profiles, precedence, risk floors, effort directives | edits to risk floors with a recorded profile decision |
| Overrides | `.agents/context/overrides.toon` (ships empty) | `.agents/context/overrides.local.toon` |
| Risk | `.agents/context/risk-rules.toon` starter globs | its real task-risk rules |
| Runtimes | `.agents/context/runtimes.toon` defaults for claude-code, codex, opencode, roo, shell, unknown | added runtimes and adapter entry points |
| Recovery | `.agents/context/RECOVERY.toon` symptom→source defaults | project-specific authoritative sources |
| Qualification | contract, probe pack, scorer, synthetic fixture repo | nothing (may add project probes) |
| Observations | format + invalidation + escalation rules | the observation files themselves |
| Taxonomy | layer names, frontmatter schema, validators | its own skills and layer content |
| Commands | `project context {explain,qualify,observe,check,scaffold,test}` | specialised verification commands the plan cites |
| Examples | two migrated skills as reference | its real workflows and skills |

**Rule of thumb:** if changing it would change what the router *is*, it is template-owned;
if changing it would change what the router *decides for this project*, it is
project-owned. Template-owned files carry `# template-owned: replace via scaffold` as
their first line so `context scaffold` can refresh them without clobbering project config.

## A7. Documentation taxonomy

Layers, applied to skills first and to any progressively disclosed document later:

| Layer | File | Holds | Preloaded in |
|---|---|---|---|
| `summary` | `SKILL.md` body | intent, trigger, expected outcome — 10-25 lines | lean, standard, guarded |
| `core` | `core.md` | canonical rules, boundaries, invariants | standard, guarded |
| `procedure` | `procedure.md` | explicit execution sequence | guarded |
| `verification` | `verification.md` | required checks and evidence | guarded |
| `examples` | `examples.md` | worked examples, only where they materially help | none (always on demand) |
| `failure-modes` | `failure-modes.md` | common mistakes, diagnostics, recovery | guarded |
| `references` | `references.md` | tests, schemas, rubrics, artifacts, related nodes | none (always on demand) |

`SKILL.md` is always the summary layer and always carries the frontmatter. Missing layers
are legal and are simply absent from both preload and defer sets. Empty layer files fail
validation.

**Canonical-source uniqueness** is enforced mechanically, not by review: each topic in
`.agents/context/TOPICS.toon` declares one `canonical` path and one distinctive `marker`
phrase; `project context check` fails when the marker appears in more than one scanned
file. D1-D9 above are exactly what this check catches.

## A8. Routing decision table

`order = [lean, standard, guarded]`; every step applies `max()` over that ladder, so no
step can lower a profile another step raised.

| # | Override | Qualification | Degradation | Risk | Effort | Result | Governing rule |
|---|---|---|---|---|---|---|---|
| 1 | lean (match) | absent | none | low | standard | **lean** | force override precedes qualification |
| 2 | lean (match) | fail | none | normal | standard | **lean** | override precedes qualification |
| 3 | lean (match) | pass | none | high | standard | **guarded** | risk floor applies after override |
| 4 | lean (match) | pass | none | irreversible | standard | **guarded** | irreversible guard |
| 5 | guarded (match) | pass | none | low | standard | **guarded** | guarded override raises |
| 6 | expired lean | pass | none | low | standard | **lean** | expired override dropped by `load_overrides`; qualification pass |
| 7 | expired lean | absent | none | low | standard | **standard** | expired dropped on load; uncertain ⇒ standard |
| 8 | none | pass | none | low | standard | **lean** | qualification pass ⇒ lean |
| 9 | none | fail | none | low | standard | **standard** | qualification fail ⇒ standard |
| 10 | none | uncertain | none | low | standard | **standard** | uncertainty is not qualification |
| 11 | none | pass, stale fingerprint | none | low | standard | **standard** | observation invalidated ⇒ uncertain |
| 12 | none | pass | none | normal | standard | **lean** | `normal` floor is lean |
| 13 | none | fail | none | high | standard | **guarded** | floor raises above standard |
| 14 | local lean, shared guarded | absent | none | low | standard | **lean** | project-local override wins |
| 15 | none | pass | none | low | **deep** | **lean** | effort never changes the profile |
| 16 | none | pass | 1 event, retry unused | low | standard | **lean** + `recover_first` | reload source before inflating context |
| 17 | none | pass | 2 events, retry spent | low | standard | **standard** | escalate one step after recovery+retry fail |
| 18 | none | pass | escalated, 5 successes | low | standard | **lean** | reduction only after sustained success |

Rows 1-15 are unit-testable against `resolve()`, except 6 and 7: expiry is filtered by
`load_overrides`, so those two are proven against real override files at the I/O layer,
which keeps `resolve()` pure and its decisions reproducible on any date. Rows 16-18
additionally exercise the observation state machine.

## A9. Files to add, change, move or delete

**Add — library and commands**

```
.agentic-template/lib/toon.py            read/write the TOON subset used by control files
.agentic-template/lib/environment.py     runtime detection, capability lookup, fingerprint
.agentic-template/lib/router.py          resolve() — pure precedence function
.agentic-template/lib/observations.py    observation store, invalidation, escalation ladder
.agentic-template/lib/skills.py          frontmatter parsing, catalog resolution, layer sets
.agentic-template/lib/plan.py            context plan assembly and rendering
.agentic-template/lib/qualification.py   probe pack emission and deterministic scoring
.agentic-template/bin/context            subcommand dispatcher (internal)
.agentic-template/bin/context-test       runs the unittest suite (internal)
```

**Add — router configuration (`.agents/context/`)**

```
README.md                       what the router is, how to configure it
ROUTER.toon                     profiles, precedence, risk floors, effort directives
TOPICS.toon                     canonical-source registry with marker phrases
RECOVERY.toon                   symptom → authoritative source
runtimes.toon                   runtime capability declarations
risk-rules.toon                 path globs → task risk
overrides.toon                  shared overrides (ships empty)
observations/.gitkeep           observation store
qualification/QUALIFICATION.toon  probe definitions, gating flags, version
qualification/expected.toon       expected answers
qualification/answers.schema.toon answer schema
```

**Add — fixtures and tests**

```
.agentic-template/fixtures/qualification-repo/    synthetic repo the probes run against
.agentic-template/fixtures/generated-project/     acceptance fixture for the 10 slice outcomes
.agentic-template/tests/_support.py
.agentic-template/tests/test_toon.py
.agentic-template/tests/test_router_precedence.py
.agentic-template/tests/test_environment.py
.agentic-template/tests/test_observations.py
.agentic-template/tests/test_skill_layers.py
.agentic-template/tests/test_explain.py
.agentic-template/tests/test_taxonomy_check.py
.agentic-template/tests/test_qualification.py
.agentic-template/tests/test_scaffold_acceptance.py
```

**Add — skills and docs**

```
.agents/skills/tooling/context-qualification/SKILL.md   the capability qualification skill
.agents/skills/tooling/context-packet/{core,procedure,verification,references}.md
.agents/skills/workflow/review-loop/{core,procedure,verification,failure-modes}.md
docs/wiki/method/context-router.md    why context depth is routed (canonical narrative)
docs/wiki/method/glossary.md          method vocabulary
.agents/context/README.md             configuration reference
```

The narrative and the configuration reference are deliberately the only two homes: the
wiki page answers "why", `.agents/context/README.md` answers "which file do I edit", and
neither restates the other.

**Change**

```
.agentic-template/bin/project              + context command; check gains `context check`
.agentic-template/bin/check-repo-contract  + new required files; delegate catalog completeness
.agentic-template/bin/self-test            + invoke context-test
.agentic-template/bin/docs-map             + Context Router route
.agents/skills/CATALOG.toon                + 8 missing skills (C1), + id field, + 2 new skills
.agents/skills/tooling/context-packet/SKILL.md   → summary layer + router frontmatter
.agents/skills/workflow/review-loop/SKILL.md     → summary layer + router frontmatter
AGENTS.md                                  + 8-line "Context routing" section only
.agentic-template/templates/AGENTS_TEMPLATE.md   + required Context routing section
.agentic-template/templates/README_TEMPLATE.md   + required router mention
PROJECT_PROFILE.toon                       + context_router policy + 2 decisions
HANDOFF.toon                               session state
docs/README.md                             + Context Router route
.github/workflows/ci.yml                   + self-test step (C3)
```

**Move / delete — deferred to Phase 1, not this plan**

```
.agents/coordination/MODEL_ROUTING_POLICY.md  → pointer; content to tooling/model-routing layers (D1)
.agents/coordination/CONTEXT_POLICY.md        → pointer; content to context-packet layers (D3)
AGENTS.md sections per A3                     → deleted, pointers added
docs/context-store.md fitness list            → pointer to docs/validation.md (D4)
```

Nothing is deleted in the thin slice. Phase 1 deletes only after the router demonstrably
resolves the same content through layers.

## A10. First thin slice

The two migration skills are **`tooling/context-packet`** and **`workflow/review-loop`**.

Rationale: `context-packet` is the provenance carrier the router depends on (its packet
shape gains the `provenance` field that makes targeted recovery possible), and it is
already reference-shaped. `review-loop` is procedure-, verification- and
failure-mode-shaped, so between them the pair exercises every taxonomy layer. Neither sits
on the `init` critical path, so a botched migration cannot break project bootstrap. Both
are small (72 and 49 lines), so each migrates inside one reviewable task.

The slice proves the spec's ten outcomes through the acceptance fixture in Task 12/13:
inherit the scaffold, define one project-local workflow, define one project-local skill,
divide guidance into the taxonomy, route it lean/standard/guarded, apply a local
override, run qualification, apply a task-risk floor, recover from an induced degradation
by reloading an authoritative source, and explain the decision.

## A11. Acceptance scenarios

The fixture `.agentic-template/fixtures/generated-project/` is a minimal *generated*
project (project-facing `AGENTS.md`, no template markers) with one project-local workflow
skill `workflow/ship-slice` and one project-local domain skill `domain/pricing-rules`,
both layered.

| ID | WHEN | THEN |
|---|---|---|
| AC-1 | `project context scaffold --into <fixture>` runs on a project without `.agents/context/` | every template-owned router file is present and byte-identical to the template's |
| AC-2 | the fixture declares `workflow/ship-slice` in its catalog with layered files | `project context check` passes in the fixture |
| AC-3 | `context explain --skill ship-slice --risk low` with a passing observation | profile is `lean`; preload contains only the summary layer plus always-preload sources |
| AC-4 | the same call with no observation | profile is `standard`; preload adds `core.md`; `procedure.md` appears in `defer` |
| AC-5 | the same call with `--risk high` | profile is `guarded`; preload adds procedure, verification and failure-modes; `independent_review` is set |
| AC-6 | `overrides.local.toon` forces `lean` for the active model and risk is `low` | profile is `lean` and the reason names the local override file |
| AC-7 | `context qualify` then `--score answers.toon` with correct fixture answers | result `pass`, exit 0, per-probe breakdown printed |
| AC-8 | the same with a wrong `AGENTS.md` sha | result `fail`, exit 1, the failing probe named |
| AC-9 | `risk-rules.toon` maps `specs/capabilities/**` to `high` and `--paths specs/capabilities/CAP-001.toon` is passed | risk floor raises the profile to `guarded` without any flag |
| AC-10 | `context observe --event degraded --symptom skill_path_wrong` then `context explain` | output keeps the profile, sets `recover_first: true` and names `.agents/skills/CATALOG.toon` as the reload source |
| AC-11 | a second `degraded` event before any success | profile escalates exactly one step and the reason names the degradation |
| AC-12 | `AGENTS.md` in the fixture is edited after an observation was recorded | fingerprint changes, observation is reported as invalidated, profile falls back to `standard` |
| AC-13 | `context explain --format toon` | output parses with `lib/toon.py` and contains `decision`, `environment`, `task`, `preload`, `defer`, `verification`, `recovery`, `effort_directives` |
| AC-14 | required verification is compared across all three profiles for one skill | the `verification.required` list is identical in all three |

AC-14 is the guard on the architectural principle: the router must never change required
outcomes.

## A12. The method/product convention

The router exposes a problem the wiki already had: `docs/wiki/` mixes two kinds of
knowledge that have different owners, different lifecycles and different audiences.

```
METHODOLOGY                              PRODUCT
how this team works                      what this team is building
inherited from the template              written by the project
changes when practice changes            changes when the domain changes
audience: whoever works on the repo      audience: whoever uses or operates the thing
agents.md, development.md, testing.md    architecture.md, domain.md, operations.md
```

Today `docs/wiki/agents.md` (methodology) and `docs/wiki/domain.md` (product) sit side by
side with nothing marking the difference. After `/specialise` this is actively harmful:
the generated project's users open the wiki and find template operating procedure
interleaved with their own domain documentation, and agents cannot tell which pages they
are expected to rewrite and which they inherit.

**Convention.** Every wiki page belongs to exactly one axis, recorded two ways so that
both humans and tools can act on it:

```
docs/wiki/
  index.md                  routes to both axes; owned by neither
  method/                   how we work — inherited, rarely rewritten by a project
    agents.md
    development.md
    testing.md
    context-router.md       (new: the reasoning behind this change)
    glossary.md             method vocabulary only
  product/                  what we are building — written by the project
    architecture.md
    domain.md
    operations.md
    glossary.md             domain vocabulary only
```

plus a required frontmatter field on every page:

```yaml
---
axis: method | product
---
```

The directory is what a human sees; the frontmatter is what `check-wiki` and the router
read. `check-wiki` fails when a page has no `axis`, when `axis` disagrees with its
directory, or when a `product/` page still carries template content after
`/specialise`.

**Why both.** Directories alone break if a page moves; frontmatter alone is invisible in
a file listing. Requiring agreement between them makes accidental drift a check failure
rather than a slow erosion.

**How the router uses it.** Methodology pages are candidates for progressive disclosure
through the taxonomy — a `method/` page can grow layer files exactly like a skill.
Product pages are evidence, cited by path from a context plan, not layered. This is also
why `lean` can preload so little: methodology the model already knows does not need
restating, while product facts it cannot infer are always cited.

**Boundary with the taxonomy (A7).** The two are orthogonal and must not be conflated:
the *axis* says who owns a page and whether a project rewrites it; the *layer* says how
much of it to load right now. A `method/` page may have layers; a `product/` page
usually has one.

Task 12 applies the convention and writes the reasoning page.

## A13. Assumptions, exclusions and revisit conditions

**Assumptions**

- **ASM-1** — The article's findings generalise beyond Claude. It reports one vendor's
  evaluation of its own models, and this design treats "capable models need less
  prescriptive context" as a hypothesis to be *measured per model-runtime pair* through
  qualification and observations, never assumed from a model name. *Revisit when*
  observations from two or more runtimes either confirm or contradict it; if they
  contradict it, the fix is to change `risk_floors` defaults, not the mechanism.
- **ASM-2** — Three profiles are sufficient. *Revisit when* a project needs a fourth
  distinct preload set rather than an effort adjustment.
- **ASM-3** — Model identity is available only by self-report (`AGENTIC_MODEL_ID` or
  `--model`) and can be wrong or absent. It is therefore used only for diagnostics and
  override matching, never as a capability signal. *Revisit when* a runtime exposes a
  trustworthy attested identity.
- **ASM-4** — Skill frontmatter stays YAML despite the TOON default, because
  `.claude/skills/` and comparable native loaders parse YAML. Recorded as a deliberate
  deviation in `PROJECT_PROFILE.toon.decisions`. *Revisit when* the hosts we target read
  TOON frontmatter.
- **ASM-5** — Agents will honour a context plan they are shown. The router cannot enforce
  what a model loads; it makes the intended set explicit, provenanced and checkable.
  Qualification and observations are the compensating control. *Revisit when* a runtime
  offers enforceable context scoping.
- **ASM-6** — `sha256` over `AGENTS.md`, `CATALOG.toon`, `TAXONOMY.md` and `ROUTER.toon` is a
  good enough proxy for "contract revision", removing manual revision bookkeeping.
  *Revisit when* churn in those files invalidates observations faster than qualification
  can be rerun.

**Exclusions (deliberately not built)**

- **X1 — host auto-memory is not adopted.** The article recommends letting the host save
  memories automatically instead of writing to `CLAUDE.md`. That is correct for Claude
  Code and wrong for this template: auto-memory is host-specific, invisible to Codex,
  OpenCode and Roo, unversioned, unreviewable and unavailable to CI. It would silently
  become a second source of truth competing with the repo-native context store. The
  portable equivalent is what already exists — `HANDOFF.toon`, `.agents/knowledge/` and
  `PROJECT_PROFILE.toon`, all versioned and diffable. Host auto-memory may be used for
  *personal* preferences; it must not carry project facts. *Revisit when* a memory
  mechanism exists that is portable across runtimes and reviewable in a pull request.
- No model registry, benchmark harness or capability leaderboard.
- No action-pattern matching in `risk-rules.toon` for the slice — path globs and the
  explicit `--risk` flag only. *Revisit when* a project needs risk derived from the verb
  rather than the target.
- No automatic profile application: the router explains, the agent complies. No hidden
  adaptation.
- No `examples` layer for either migrated skill — neither currently has examples that
  materially help, and the taxonomy forbids empty files.
- No migration of `AGENTS.md` or the other 56 skills (Phase 1).
- No new documentation tree; overflow content returns to existing canonical homes.

**Deferred scope (Phase 1, requires separate approval)**

1. Slim `AGENTS.md` 367 → ~85 lines per A3, and update `check-repo-contract` and
   `self-test` assertions that pin the removed sections.
2. Resolve D1-D9 by reducing each duplicate to a pointer, with `TOPICS.toon` markers
   added first so the check proves the duplication is gone.
3. Migrate the remaining skills to the taxonomy, catalog-first.
4. Rewrite `AGENTS_TEMPLATE.md`'s 20 required sections into the lean shape so generated
   projects inherit a lightweight contract.
5. Shrink the six host shims (D7) to a single sentence plus `project startup`.
6. Extend `project doctor` to report context-router rightsizing — oversized `AGENTS.md`,
   skills with no layer split, topics with duplicate markers, stale observations — the
   portable counterpart to the article's `claude doctor`.

**Risks and unknowns**

- **R1** — The article's evidence is Anthropic's own coding evaluations on Claude models.
  Applying it to Codex, OpenCode or Roo is extrapolation. Mitigation: the router is
  symmetric — it raises as readily as it lowers — `standard` is the default under any
  uncertainty, and per-runtime observations are what actually license `lean`.
- **R2** — Qualification measures a fixture, not the real task. A model can pass the
  fixture and still fail in the project. Mitigation: fast escalation on one contract or
  verification failure; slow reduction requiring five successes.
- **R3** — Self-reported answers (probe P4, disclosure discipline) are gameable.
  Mitigation: P4 is advisory and never gating.
- **R4** — Scaffold refresh could clobber project configuration. Mitigation: the
  `# template-owned` marker plus `scaffold --dry-run` defaulting to report-only.
- **R5** — `TOPICS.toon` marker matching can produce false positives on common phrases.
  Mitigation: markers must be ≥ 20 characters and the check prints every hit, so a bad
  marker fails loudly rather than silently.
- **R6** — The router adds a command surface that agents must remember to call. If they
  do not, nothing improves. Mitigation: `project startup` prints the one-line routing
  hint; `AGENTS.md` gains the 8-line section; the fixture proves the loop.
- **U1** — Unknown whether Codex, OpenCode and Roo can be detected reliably from
  environment variables alone. The `unknown` runtime path (⇒ `standard`) is the safe
  default, and `--runtime` is always available.
- **U2** — Unknown how expensive a full qualification run is in practice. If it exceeds a
  few minutes, drop the advisory probe and consider a shorter gating subset.

---

# Part B — Implementation Plan (thin slice)

## File structure and responsibilities

```
.agentic-template/lib/            pure Python, importable, no side effects at import
  toon.py            parse/emit the TOON subset; the only file that knows TOON syntax
  environment.py     detect runtime, load capabilities, compute the fingerprint
  router.py          resolve() — the precedence function; no file I/O
  observations.py    read/write observations; invalidation and the escalation ladder
  skills.py          catalog lookup, frontmatter parsing, layer discovery
  plan.py            build and render a context plan from a decision plus a skill
  qualification.py   emit the probe pack, score answers deterministically

.agentic-template/bin/
  context            argparse dispatcher: explain|qualify|observe|check|scaffold|test
  context-test       runs `python3 -m unittest discover .agentic-template/tests`

.agentic-template/tests/          one module per behaviour, unittest, stdlib only
.agentic-template/fixtures/       synthetic repos; never imported, only executed against
.agents/context/                  configuration data; no logic
```

Boundary rule: `lib/` never reads `sys.argv` or prints; `bin/context` never contains
routing logic. That split is what makes the precedence table testable without a
filesystem.

---

### Task 1: TOON reader and writer

**Files:**
- Create: `.agentic-template/lib/toon.py`
- Create: `.agentic-template/tests/_support.py`
- Test: `.agentic-template/tests/test_toon.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `toon.loads(text) -> dict`, `toon.dumps(value) -> str`,
  `toon.ToonError(ValueError)`. Every later task uses these two functions and nothing
  else from this module.

- [ ] **Step 1: Write the failing test**

`.agentic-template/tests/_support.py`:

```python
"""Shared test helpers. Puts the template library on the import path."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / ".agentic-template" / "lib"
BIN = ROOT / ".agentic-template" / "bin"

if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))
```

`.agentic-template/tests/test_toon.py`:

```python
import unittest

import _support  # noqa: F401  (import for the sys.path side effect)
import toon


class TestToonScalars(unittest.TestCase):
    def test_reads_scalar_types(self):
        text = "name: router\ncount: 3\nenabled: true\nmissing: null\n"
        self.assertEqual(
            toon.loads(text),
            {"name": "router", "count": 3, "enabled": True, "missing": None},
        )

    def test_reads_quoted_string_verbatim(self):
        self.assertEqual(toon.loads('marker: "a: b"\n'), {"marker": "a: b"})


class TestToonCollections(unittest.TestCase):
    def test_reads_nested_map(self):
        text = "profiles:\n  lean:\n    review: none\n"
        self.assertEqual(toon.loads(text), {"profiles": {"lean": {"review": "none"}}})

    def test_reads_inline_and_empty_lists(self):
        text = "order: [lean, standard, guarded]\nnone: []\nblank: {}\n"
        self.assertEqual(
            toon.loads(text),
            {"order": ["lean", "standard", "guarded"], "none": [], "blank": {}},
        )

    def test_reads_list_of_maps_with_nested_children(self):
        text = (
            "overrides:\n"
            "  - match:\n"
            "      model: claude-fable-5\n"
            "    profile: lean\n"
            "    reason: fixture run\n"
            "  - match:\n"
            "      model: other\n"
            "    profile: guarded\n"
            "    reason: unverified\n"
        )
        self.assertEqual(
            toon.loads(text),
            {
                "overrides": [
                    {
                        "match": {"model": "claude-fable-5"},
                        "profile": "lean",
                        "reason": "fixture run",
                    },
                    {
                        "match": {"model": "other"},
                        "profile": "guarded",
                        "reason": "unverified",
                    },
                ]
            },
        )

    def test_list_item_with_colon_in_prose_stays_a_string(self):
        text = "tests_run:\n  - 2026-07-26 project check: pass\n"
        self.assertEqual(
            toon.loads(text), {"tests_run": ["2026-07-26 project check: pass"]}
        )

    def test_url_list_item_stays_a_string(self):
        text = "refs:\n  - https://example.com/a\n"
        self.assertEqual(toon.loads(text), {"refs": ["https://example.com/a"]})


class TestToonErrors(unittest.TestCase):
    def test_odd_indent_is_rejected_with_line_number(self):
        with self.assertRaises(toon.ToonError) as caught:
            toon.loads("a:\n   b: 1\n")
        self.assertIn("line 2", str(caught.exception))

    def test_tab_indent_is_rejected_with_line_number(self):
        with self.assertRaises(toon.ToonError) as caught:
            toon.loads("key:\n\tvalue: 1\n")
        self.assertIn("line 2", str(caught.exception))
        self.assertIn("tab", str(caught.exception).lower())


class TestToonLenience(unittest.TestCase):
    def test_duplicate_keys_resolve_last_wins(self):
        self.assertEqual(toon.loads("a: 1\na: 2\n"), {"a": 2})

    def test_unterminated_quote_is_treated_as_literal(self):
        self.assertEqual(toon.loads('marker: "a: b\n'), {"marker": '"a: b'})


class TestToonRoundTrip(unittest.TestCase):
    def test_dumps_then_loads_is_identity(self):
        value = {
            "version": 1,
            "order": ["lean", "standard"],
            "profiles": {"lean": {"preload_layers": ["summary"]}},
            "runs": [{"date": "2026-07-26", "outcome": "success"}],
        }
        self.assertEqual(toon.loads(toon.dumps(value)), value)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'toon'`

- [ ] **Step 3: Write the implementation**

`.agentic-template/lib/toon.py`:

```python
"""Reader and writer for the TOON subset used by template control files.

Supported:
    key: value            scalar (string, int, true, false, null)
    key: "quoted"         string kept verbatim, colons allowed
    key:                  nested map, indented by two spaces
    key: []  /  key: {}   empty list / empty map
    key: [a, b, c]        inline list of scalars
    key:                  block list, items indented by two spaces
      - scalar
      - key: value        list of maps; continuation keys align under the key
        other: value

Not supported: anchors, multi-line strings, inline maps with content, tabs.

Lenient by design:
    Duplicate keys resolve last-wins; earlier values with the same key are
    silently overwritten.
    Unterminated quotes are treated as literal characters (e.g., "a: b is
    accepted as the string "a: b without raising an error).
"""
import re

_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*$")
_INT = re.compile(r"-?\d+$")


class ToonError(ValueError):
    """Raised with a line number whenever input leaves the supported subset."""


def _scalar(raw):
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if _INT.match(text):
        return int(text)
    return text


def _split_key(text):
    """Return (key, rest) when text opens a mapping entry, else None."""
    key, separator, rest = text.partition(":")
    if not separator or not _KEY.match(key.strip()):
        return None
    if rest.startswith("//"):
        return None
    return key.strip(), rest.strip()


def _significant_lines(text):
    lines = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        leading = raw[:len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in leading:
            raise ToonError(f"line {number}: tabs are not supported; use spaces only")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ToonError(f"line {number}: indent {indent} is not a multiple of two")
        lines.append((indent, stripped, number))
    return lines


def _parse_value(lines, index, indent, key_rest):
    """Resolve the value for a mapping entry. Returns (value, next_index)."""
    if key_rest == "[]":
        return [], index
    if key_rest == "{}":
        return {}, index
    if key_rest.startswith("[") and key_rest.endswith("]"):
        body = key_rest[1:-1].strip()
        return ([_scalar(part) for part in body.split(",")] if body else []), index
    if key_rest:
        return _scalar(key_rest), index
    child = indent + 2
    if index < len(lines) and lines[index][0] == child:
        if lines[index][1].startswith("- "):
            return _parse_list(lines, index, child)
        return _parse_map(lines, index, child)
    if index < len(lines) and lines[index][0] > indent:
        raise ToonError(f"line {lines[index][2]}: unexpected indent")
    return {}, index


def _parse_map(lines, index, indent):
    result = {}
    while index < len(lines):
        line_indent, text, number = lines[index]
        if line_indent < indent or text.startswith("- "):
            break
        if line_indent > indent:
            raise ToonError(f"line {number}: unexpected indent")
        entry = _split_key(text)
        if entry is None:
            raise ToonError(f"line {number}: expected 'key: value'")
        key, rest = entry
        index += 1
        result[key], index = _parse_value(lines, index, indent, rest)
    return result, index


def _parse_list(lines, index, indent):
    result = []
    while index < len(lines):
        line_indent, text, number = lines[index]
        if line_indent < indent or not text.startswith("- "):
            break
        if line_indent > indent:
            raise ToonError(f"line {number}: unexpected indent")
        body = text[2:].strip()
        index += 1
        entry = _split_key(body)
        if entry is None:
            result.append(_scalar(body))
            continue
        key, rest = entry
        item = {}
        item[key], index = _parse_value(lines, index, indent + 2, rest)
        continuation, index = _parse_map(lines, index, indent + 2)
        item.update(continuation)
        result.append(item)
    return result, index


def loads(text):
    """Parse TOON text into Python data. Raises ToonError with a line number."""
    lines = _significant_lines(text)
    value, index = _parse_map(lines, 0, 0)
    if index != len(lines):
        raise ToonError(f"line {lines[index][2]}: unexpected content")
    return value


def _emit_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or ":" in text or text.strip() != text:
        return '"' + text.replace('"', "'") + '"'
    return text


def _emit(value, indent, out):
    pad = " " * indent
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, dict) and child:
                out.append(f"{pad}{key}:")
                _emit(child, indent + 2, out)
            elif isinstance(child, dict):
                out.append(f"{pad}{key}: {{}}")
            elif isinstance(child, list) and child:
                out.append(f"{pad}{key}:")
                _emit(child, indent + 2, out)
            elif isinstance(child, list):
                out.append(f"{pad}{key}: []")
            else:
                out.append(f"{pad}{key}: {_emit_scalar(child)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                keys = list(item)
                first = keys[0]
                head = item[first]
                if isinstance(head, (dict, list)) and head:
                    out.append(f"{pad}- {first}:")
                    _emit(head, indent + 4, out)
                else:
                    out.append(f"{pad}- {first}: {_emit_scalar(head)}")
                _emit({key: item[key] for key in keys[1:]}, indent + 2, out)
            else:
                out.append(f"{pad}- {_emit_scalar(item)}")


def dumps(value):
    """Emit TOON text for data that stays inside the supported subset."""
    out = []
    _emit(value, 0, out)
    return "\n".join(out) + "\n"
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS, 12 tests

- [ ] **Step 5: Verify the parser reads the repository's real control files**

Run:
```bash
python3 -c "
import sys; sys.path.insert(0, '.agentic-template/lib')
import toon
for path in ['PROJECT_PROFILE.toon', 'HANDOFF.toon', 'CUSTOMIZE_THIS_PROJECT.toon', '.agents/skills/CATALOG.toon']:
    data = toon.loads(open(path).read())
    print(path, 'ok', sorted(data)[:4])
"
```
Expected: four `ok` lines. If any file raises, fix `toon.py` and add the failing
construct as a test case — do not edit the control file.

- [ ] **Step 6: Commit**

```bash
git add .agentic-template/lib/toon.py .agentic-template/tests/_support.py .agentic-template/tests/test_toon.py
git commit -m "feat(context-router): add TOON reader and writer for control files"
```

---

### Task 2: Router configuration and the precedence resolver

**Files:**
- Create: `.agents/context/ROUTER.toon`
- Create: `.agents/context/overrides.toon`
- Create: `.agentic-template/lib/router.py`
- Test: `.agentic-template/tests/test_router_precedence.py`

**Interfaces:**
- Consumes: `toon.loads` (Task 1).
- Produces:
  - `router.Environment(model_id, runtime, capabilities, fingerprint)` — a
    `dataclasses.dataclass`, all fields `str` except `capabilities: list[str]`.
  - `router.Task(risk, effort, skill_id, paths)` — `risk` in
    `{"low","normal","high","irreversible"}`, `effort` in
    `{"minimal","standard","deep"}`, `skill_id: str | None`, `paths: list[str]`.
  - `router.Decision(profile, reasons, trace)` — `profile: str`, `reasons: list[str]`,
    `trace: list[tuple[str, str]]` of `(step_name, outcome)`.
  - `router.resolve(env, task, config, overrides, observation) -> Decision`, pure, no I/O.
    `observation` is `None` or a dict with keys `result` (`"pass"`/`"fail"`/`"uncertain"`)
    and `escalated_profile` (`str | None`).
  - `router.load_config(root) -> dict` and `router.load_overrides(root) -> list[dict]`,
    the only functions here that touch the filesystem.

- [ ] **Step 1: Write the router configuration**

`.agents/context/ROUTER.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
version: 1

order: [lean, standard, guarded]

precedence:
  - force_override
  - qualification
  - degradation_floor
  - risk_floor
  - irreversible_guard

profiles:
  lean:
    preload_layers: [summary]
    defer_layers: [core, procedure, verification, examples, failure_modes, references]
    always_preload: [invariants, gotchas, required_verification]
    independent_review: not_required
  standard:
    preload_layers: [summary, core]
    defer_layers: [procedure, examples, failure_modes, references]
    always_preload: [invariants, gotchas, boundaries, required_verification]
    independent_review: not_required
  guarded:
    preload_layers: [summary, core, procedure, verification, failure_modes]
    defer_layers: [examples, references]
    always_preload: [invariants, gotchas, boundaries, required_verification, stop_conditions, review_rubric]
    independent_review: required_when_project_policy_demands

risk_floors:
  low: lean
  normal: lean
  high: guarded
  irreversible: guarded

effort:
  minimal:
    evidence_depth: 1
    alternatives: 0
    review_intensity: light
  standard:
    evidence_depth: 2
    alternatives: 2
    review_intensity: normal
  deep:
    evidence_depth: 3
    alternatives: 3
    review_intensity: strong

always_preload_sources:
  invariants: AGENTS.md
  gotchas: AGENTS.md
  boundaries: AGENTS.md
  required_verification: docs/validation.md
  stop_conditions: .agents/context/RECOVERY.toon
  review_rubric: .agents/coordination/REVIEW_POLICY.md

degradation:
  retry_budget: 1
  reduce_after_successes: 5
```

`.agents/context/overrides.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
# Escape hatch, not the architecture. Projects add entries to overrides.local.toon.
version: 1
overrides: []
```

- [ ] **Step 2: Write the failing test**

`.agentic-template/tests/test_router_precedence.py`:

```python
import tempfile
import unittest
from pathlib import Path

import _support  # noqa: F401
import router
import toon

CONFIG = toon.loads(open(_support.ROOT / ".agents/context/ROUTER.toon").read())

LEAN_OVERRIDE = {
    "match": {"model": "test-model", "runtime": "*"},
    "profile": "lean",
    "reason": "maintainer qualified",
    "expires": "2099-01-01",
}
GUARDED_OVERRIDE = {
    "match": {"model": "test-model", "runtime": "*"},
    "profile": "guarded",
    "reason": "unverified runtime",
    "expires": "2099-01-01",
}


def env(model="test-model", runtime="claude-code", fingerprint="fp-1"):
    return router.Environment(
        model_id=model,
        runtime=runtime,
        capabilities=["shell", "repo_search"],
        fingerprint=fingerprint,
    )


def task(risk="low", effort="standard"):
    return router.Task(risk=risk, effort=effort, skill_id="review-loop", paths=[])


def observation(result, escalated=None):
    return {"result": result, "escalated_profile": escalated}


def profile_for(overrides=(), obs=None, risk="low", effort="standard", model="test-model"):
    decision = router.resolve(env(model=model), task(risk, effort), CONFIG, list(overrides), obs)
    return decision.profile


class TestPrecedenceTable(unittest.TestCase):
    def test_01_override_beats_absent_qualification(self):
        self.assertEqual(profile_for([LEAN_OVERRIDE], None, "low"), "lean")

    def test_02_override_beats_failed_qualification(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("fail"), "normal"), "lean"
        )

    def test_03_risk_floor_applies_after_override(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("pass"), "high"), "guarded"
        )

    def test_04_irreversible_work_is_always_guarded(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("pass"), "irreversible"), "guarded"
        )

    def test_05_guarded_override_raises(self):
        self.assertEqual(
            profile_for([GUARDED_OVERRIDE], observation("pass"), "low"), "guarded"
        )

    def test_08_qualification_pass_is_lean(self):
        self.assertEqual(profile_for([], observation("pass"), "low"), "lean")

    def test_09_qualification_fail_is_standard(self):
        self.assertEqual(profile_for([], observation("fail"), "low"), "standard")

    def test_10_qualification_uncertain_is_standard(self):
        self.assertEqual(profile_for([], observation("uncertain"), "low"), "standard")

    def test_12_normal_risk_floor_is_lean(self):
        self.assertEqual(profile_for([], observation("pass"), "normal"), "lean")

    def test_13_floor_raises_standard_to_guarded(self):
        self.assertEqual(profile_for([], observation("fail"), "high"), "guarded")

    def test_15_effort_never_changes_the_profile(self):
        for effort in ("minimal", "standard", "deep"):
            self.assertEqual(
                profile_for([], observation("pass"), "low", effort), "lean", effort
            )

    def test_17_degradation_escalation_is_a_floor(self):
        self.assertEqual(
            profile_for([], observation("pass", escalated="standard"), "low"), "standard"
        )

    def test_local_override_precedes_shared_override(self):
        # load_overrides puts local entries first; resolve takes the first match.
        self.assertEqual(
            profile_for([LEAN_OVERRIDE, GUARDED_OVERRIDE], None, "low"), "lean"
        )

    def test_risk_floor_raises_above_the_qualification_result(self):
        # The shipped config floors low and normal at lean, which can never raise
        # anything, and _validate clamps high and irreversible to guarded, which
        # irreversible_guard would produce anyway. Raising the normal floor is the
        # only configuration under which the risk_floor step is observable — without
        # this test, deleting the step entirely leaves the suite green.
        config = dict(CONFIG, risk_floors=dict(CONFIG["risk_floors"], normal="standard"))
        decision = router.resolve(env(), task("normal"), config, [], observation("pass"))
        self.assertEqual(decision.profile, "standard")
        self.assertIn("floors the profile at standard", " ".join(decision.reasons))

    def test_irreversible_guard_is_recorded_in_the_trace(self):
        applied = router.resolve(env(), task("irreversible"), CONFIG, [], observation("pass"))
        self.assertIn(("irreversible_guard", "applied"), applied.trace)
        skipped = router.resolve(env(), task("low"), CONFIG, [], observation("pass"))
        self.assertIn(("irreversible_guard", "not_applicable"), skipped.trace)

    def test_override_matching_is_case_sensitive_on_every_platform(self):
        # fnmatch normalises case through os.path.normcase, so it is case-insensitive
        # on Windows. The same override file must route identically on every host.
        entry = dict(LEAN_OVERRIDE, match={"model": "Test-Model", "runtime": "*"})
        decision = router.resolve(env(), task("low"), CONFIG, [entry], observation("fail"))
        self.assertEqual(decision.profile, "standard")


class TestOverrideLoading(unittest.TestCase):
    """Expiry lives in the I/O layer, so it is proven against real files.

    resolve() is pure and never consults the clock; an expired override is one
    that load_overrides declined to return.
    """

    def _root_with(self, filename, body):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".agents/context").mkdir(parents=True, exist_ok=True)
        (root / ".agents/context" / filename).write_text(body)
        return root

    def _entry(self, profile, expires):
        return (
            "version: 1\noverrides:\n"
            "  - match:\n      model: test-model\n"
            f"    profile: {profile}\n"
            "    reason: recorded for the test suite\n"
            f"    expires: {expires}\n"
        )

    def test_expired_override_is_dropped_on_load(self):
        root = self._root_with("overrides.toon", self._entry("lean", "2020-01-01"))
        self.assertEqual(router.load_overrides(root), [])

    def test_expired_override_leaves_routing_to_qualification(self):
        root = self._root_with("overrides.toon", self._entry("lean", "2020-01-01"))
        decision = router.resolve(env(), task("low"), CONFIG, router.load_overrides(root), None)
        self.assertEqual(decision.profile, "standard")

    def test_live_override_survives_load_and_routes(self):
        root = self._root_with("overrides.toon", self._entry("lean", "2099-01-01"))
        loaded = router.load_overrides(root)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["source"], ".agents/context/overrides.toon")
        decision = router.resolve(env(), task("low"), CONFIG, loaded, None)
        self.assertEqual(decision.profile, "lean")

    def test_local_overrides_load_before_shared(self):
        root = self._root_with("overrides.toon", self._entry("guarded", "2099-01-01"))
        (root / ".agents/context/overrides.local.toon").write_text(
            self._entry("lean", "2099-01-01")
        )
        loaded = router.load_overrides(root)
        self.assertEqual([entry["profile"] for entry in loaded], ["lean", "guarded"])


class TestModelIdentityIsNotCapability(unittest.TestCase):
    def test_unknown_model_without_override_routes_identically(self):
        known = profile_for([], observation("pass"), "low", model="test-model")
        unknown = profile_for([], observation("pass"), "low", model="mystery-model-9")
        self.assertEqual(known, unknown)


class TestExplainability(unittest.TestCase):
    def test_every_precedence_step_appears_in_the_trace(self):
        decision = router.resolve(
            env(), task("high"), CONFIG, [LEAN_OVERRIDE], observation("pass")
        )
        self.assertEqual([step for step, _ in decision.trace], CONFIG["precedence"])

    def test_reasons_name_the_deciding_inputs(self):
        decision = router.resolve(env(), task("low"), CONFIG, [], None)
        joined = " ".join(decision.reasons)
        self.assertIn("no force override matched", joined)
        self.assertIn("uncertain", joined)


class TestConfigValidation(unittest.TestCase):
    def test_unknown_risk_is_rejected(self):
        with self.assertRaises(router.RouterError):
            router.resolve(
                env(),
                router.Task(risk="apocalyptic", effort="standard", skill_id=None, paths=[]),
                CONFIG,
                [],
                None,
            )

    def test_high_risk_floor_below_guarded_is_rejected(self):
        broken = dict(CONFIG, risk_floors=dict(CONFIG["risk_floors"], high="lean"))
        with self.assertRaises(router.RouterError):
            router.resolve(env(), task("high"), broken, [], None)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'router'`

- [ ] **Step 4: Write the implementation**

`.agentic-template/lib/router.py`:

```python
"""Deterministic context-profile resolution.

resolve() is pure: it takes already-loaded data and returns a Decision. Every
precedence step may only raise the profile along ROUTER.toon's `order` ladder, so
the result never depends on step ordering beyond what the trace records.
"""
from dataclasses import dataclass, field
from datetime import date
from fnmatch import fnmatchcase
from pathlib import Path

import toon

RISKS = ("low", "normal", "high", "irreversible")
EFFORTS = ("minimal", "standard", "deep")
HIGH_RISKS = ("high", "irreversible")


class RouterError(ValueError):
    """Raised when router inputs or configuration are invalid."""


@dataclass(frozen=True)
class Environment:
    model_id: str
    runtime: str
    capabilities: list
    fingerprint: str


@dataclass(frozen=True)
class Task:
    risk: str
    effort: str
    skill_id: str
    paths: list = field(default_factory=list)


@dataclass
class Decision:
    profile: str
    reasons: list
    trace: list


def load_config(root):
    path = Path(root) / ".agents/context/ROUTER.toon"
    if not path.exists():
        raise RouterError(f"missing router config: {path}")
    return toon.loads(path.read_text())


def load_overrides(root, today=None):
    """Local overrides first, then shared. Expired entries are dropped."""
    root = Path(root)
    entries = []
    for name in ("overrides.local.toon", "overrides.toon"):
        path = root / ".agents/context" / name
        if not path.exists():
            continue
        data = toon.loads(path.read_text())
        for entry in data.get("overrides") or []:
            entries.append(dict(entry, source=str(path.relative_to(root))))
    return [entry for entry in entries if not _expired(entry, today)]


def _expired(entry, today=None):
    expires = entry.get("expires")
    if not expires:
        return False
    return str(expires) < (today or date.today().isoformat())


def _rank(config, profile):
    order = config["order"]
    if profile not in order:
        raise RouterError(f"unknown profile: {profile}")
    return order.index(profile)


def _raise_to(config, current, candidate):
    if candidate is None:
        return current
    if current is None:
        return candidate
    return candidate if _rank(config, candidate) > _rank(config, current) else current


def _matches(entry, env):
    match = entry.get("match") or {}
    model = str(match.get("model", "*"))
    runtime = str(match.get("runtime", "*"))
    return fnmatchcase(env.model_id or "", model) and fnmatchcase(env.runtime or "", runtime)


def _validate(config, task):
    if task.risk not in RISKS:
        raise RouterError(f"unknown risk: {task.risk}; expected one of {list(RISKS)}")
    if task.effort not in EFFORTS:
        raise RouterError(f"unknown effort: {task.effort}; expected one of {list(EFFORTS)}")
    for risk in HIGH_RISKS:
        floor = config["risk_floors"].get(risk)
        if _rank(config, floor) < _rank(config, "guarded"):
            raise RouterError(
                f"risk_floors.{risk} is {floor}; {risk} work must floor at guarded"
            )


def resolve(env, task, config, overrides, observation):
    """Return the Decision for this environment, task and recorded state."""
    _validate(config, task)
    reasons = []
    trace = []
    profile = None

    override = next((entry for entry in overrides if _matches(entry, env)), None)
    if override:
        profile = override["profile"]
        trace.append(("force_override", f"hit:{profile}"))
        reasons.append(
            f"force override in {override.get('source', 'overrides')} selected "
            f"{profile} ({override.get('reason', 'no reason recorded')})"
        )
    else:
        trace.append(("force_override", "miss"))
        reasons.append("no force override matched the active model and runtime")

    result = (observation or {}).get("result") or "uncertain"
    if profile is None:
        profile = "lean" if result == "pass" else "standard"
        reasons.append(f"qualification result is {result}, routing to {profile}")
    trace.append(("qualification", result))

    escalated = (observation or {}).get("escalated_profile")
    if escalated:
        raised = _raise_to(config, profile, escalated)
        if raised != profile:
            reasons.append(f"recorded degradation escalated the profile to {escalated}")
        profile = raised
        trace.append(("degradation_floor", escalated))
    else:
        trace.append(("degradation_floor", "none"))

    floor = config["risk_floors"][task.risk]
    raised = _raise_to(config, profile, floor)
    if raised != profile:
        reasons.append(f"task risk {task.risk} floors the profile at {floor}")
    profile = raised
    trace.append(("risk_floor", floor))

    # irreversible_guard is redundant under _validate but keeps the trace complete and
    # survives a future ladder with more than three profiles.
    if task.risk in HIGH_RISKS:
        raised = _raise_to(config, profile, "guarded")
        if raised != profile:
            reasons.append(f"{task.risk} work is guarded regardless of other inputs")
        profile = raised
        trace.append(("irreversible_guard", "applied"))
    else:
        trace.append(("irreversible_guard", "not_applicable"))

    return Decision(profile=profile, reasons=reasons, trace=trace)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS, 12 + 25 tests

- [ ] **Step 6: Commit**

```bash
git add .agents/context/ROUTER.toon .agents/context/overrides.toon \
        .agentic-template/lib/router.py .agentic-template/tests/test_router_precedence.py
git commit -m "feat(context-router): add profile config and deterministic precedence resolver"
```

---

### Task 3: Runtime detection, capabilities and environment fingerprint

**Files:**
- Create: `.agents/context/runtimes.toon`
- Create: `.agentic-template/lib/environment.py`
- Test: `.agentic-template/tests/test_environment.py`

**Interfaces:**
- Consumes: `toon.loads` (Task 1), `router.Environment` (Task 2).
- Produces:
  - `environment.detect_runtime(env_vars) -> str` — a runtime id or `"unknown"`.
  - `environment.capabilities(root, runtime) -> list[str]`.
  - `environment.contract_fingerprint(root) -> str` — 16 hex chars over the contract
    files, independent of model and runtime.
  - `environment.build(root, env_vars, model=None, runtime=None) -> router.Environment`.
  - `environment.CONTRACT_FILES` — the tuple of paths hashed into the fingerprint.

- [ ] **Step 1: Write the runtime capability declarations**

`.agents/context/runtimes.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
# Capability is a property of the host, not of the model. Unknown hosts get the
# minimal set, which routes to standard because qualification cannot be trusted.
version: 1

detect:
  - runtime: claude-code
    env: CLAUDECODE
  - runtime: codex
    env: CODEX_HOME
  - runtime: codex
    env: CODEX_SANDBOX
  - runtime: opencode
    env: OPENCODE
  - runtime: roo
    env: ROO_CODE_IPC_SOCKET_PATH

runtimes:
  claude-code:
    capabilities: [shell, repo_search, linked_references, native_skills, deferred_tools, subagents, structured_output]
    entry_point: CLAUDE.md
    skill_loading: native
  codex:
    capabilities: [shell, repo_search, linked_references, structured_output]
    entry_point: AGENTS.md
    skill_loading: filesystem
  opencode:
    capabilities: [shell, repo_search, linked_references, structured_output]
    entry_point: AGENTS.md
    skill_loading: filesystem
  roo:
    capabilities: [shell, repo_search, linked_references]
    entry_point: AGENTS.md
    skill_loading: filesystem
  shell:
    capabilities: [shell, repo_search]
    entry_point: AGENTS.md
    skill_loading: filesystem
  unknown:
    capabilities: [repo_search]
    entry_point: AGENTS.md
    skill_loading: filesystem
```

- [ ] **Step 2: Write the failing test**

`.agentic-template/tests/test_environment.py`:

```python
import unittest

import _support  # noqa: F401
import environment

ROOT = _support.ROOT


class TestRuntimeDetection(unittest.TestCase):
    def test_detects_claude_code(self):
        self.assertEqual(environment.detect_runtime(ROOT, {"CLAUDECODE": "1"}), "claude-code")

    def test_detects_codex_from_either_variable(self):
        self.assertEqual(environment.detect_runtime(ROOT, {"CODEX_HOME": "/x"}), "codex")
        self.assertEqual(environment.detect_runtime(ROOT, {"CODEX_SANDBOX": "1"}), "codex")

    def test_explicit_variable_wins(self):
        self.assertEqual(
            environment.detect_runtime(ROOT, {"AGENTIC_RUNTIME": "roo", "CLAUDECODE": "1"}),
            "roo",
        )

    def test_unrecognised_host_is_unknown(self):
        self.assertEqual(environment.detect_runtime(ROOT, {}), "unknown")


class TestCapabilities(unittest.TestCase):
    def test_unknown_runtime_gets_the_minimal_set(self):
        self.assertEqual(environment.capabilities(ROOT, "unknown"), ["repo_search"])

    def test_declared_runtime_gets_its_declared_set(self):
        self.assertIn("native_skills", environment.capabilities(ROOT, "claude-code"))

    def test_undeclared_runtime_falls_back_to_unknown(self):
        self.assertEqual(
            environment.capabilities(ROOT, "some-new-agent"),
            environment.capabilities(ROOT, "unknown"),
        )


class TestFingerprint(unittest.TestCase):
    def test_is_stable_across_calls(self):
        self.assertEqual(
            environment.contract_fingerprint(ROOT), environment.contract_fingerprint(ROOT)
        )

    def test_changes_when_a_contract_file_changes(self):
        import shutil
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(ROOT, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            before = environment.contract_fingerprint(copy)
            agents = copy / "AGENTS.md"
            agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
            self.assertNotEqual(before, environment.contract_fingerprint(copy))

    def test_is_independent_of_model_and_runtime(self):
        first = environment.build(ROOT, {"CLAUDECODE": "1"}, model="a")
        second = environment.build(ROOT, {}, model="b", runtime="codex")
        self.assertEqual(first.contract_fingerprint, second.contract_fingerprint)
        self.assertNotEqual(first.fingerprint, second.fingerprint)


class TestBuild(unittest.TestCase):
    def test_model_comes_from_the_environment_variable(self):
        built = environment.build(ROOT, {"AGENTIC_MODEL_ID": "claude-fable-5"})
        self.assertEqual(built.model_id, "claude-fable-5")

    def test_missing_model_is_recorded_as_unreported(self):
        self.assertEqual(environment.build(ROOT, {}).model_id, "unreported")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'environment'`

- [ ] **Step 4: Write the implementation**

`.agentic-template/lib/environment.py`:

```python
"""Runtime detection, capability lookup and contract fingerprinting.

Model identity is captured for diagnostics and override matching only. It never
feeds capability lookup: that is a property of the host runtime.
"""
import hashlib
from dataclasses import dataclass
from pathlib import Path

import router
import toon

CONTRACT_FILES = (
    "AGENTS.md",
    ".agents/skills/CATALOG.toon",
    ".agents/knowledge/TAXONOMY.md",
    ".agents/context/ROUTER.toon",
)

UNREPORTED_MODEL = "unreported"


@dataclass(frozen=True)
class Context(router.Environment):
    contract_fingerprint: str = ""


def _config(root):
    path = Path(root) / ".agents/context/runtimes.toon"
    if not path.exists():
        raise router.RouterError(f"missing runtime config: {path}")
    return toon.loads(path.read_text())


def detect_runtime(root, env_vars):
    """Map host environment variables to a runtime id declared in runtimes.toon."""
    explicit = env_vars.get("AGENTIC_RUNTIME")
    if explicit:
        return explicit
    for rule in _config(root).get("detect") or []:
        if env_vars.get(rule["env"]):
            return rule["runtime"]
    return "unknown"


def capabilities(root, runtime):
    runtimes = _config(root)["runtimes"]
    entry = runtimes.get(runtime) or runtimes["unknown"]
    return list(entry["capabilities"])


def contract_fingerprint(root):
    """Hash the files whose change should invalidate recorded observations."""
    digest = hashlib.sha256()
    for relative in CONTRACT_FILES:
        path = Path(root) / relative
        digest.update(relative.encode())
        digest.update(path.read_bytes() if path.exists() else b"<absent>")
    return digest.hexdigest()[:16]


def build(root, env_vars, model=None, runtime=None):
    """Assemble the Environment the router resolves against."""
    resolved_runtime = runtime or detect_runtime(root, env_vars)
    resolved_model = model or env_vars.get("AGENTIC_MODEL_ID") or UNREPORTED_MODEL
    caps = capabilities(root, resolved_runtime)
    contract = contract_fingerprint(root)
    digest = hashlib.sha256()
    for part in (resolved_model, resolved_runtime, ",".join(sorted(caps)), contract):
        digest.update(part.encode())
        digest.update(b"\x00")
    return Context(
        model_id=resolved_model,
        runtime=resolved_runtime,
        capabilities=caps,
        fingerprint=digest.hexdigest()[:16],
        contract_fingerprint=contract,
    )
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS, 49 tests

- [ ] **Step 6: Commit**

```bash
git add .agents/context/runtimes.toon .agentic-template/lib/environment.py \
        .agentic-template/tests/test_environment.py
git commit -m "feat(context-router): detect runtime capability and fingerprint the contract"
```

---

### Task 4: Observation store, invalidation and the escalation ladder

**Files:**
- Create: `.agents/context/RECOVERY.toon`
- Create: `.agents/context/observations/.gitkeep`
- Create: `.agentic-template/lib/observations.py`
- Test: `.agentic-template/tests/test_observations.py`

**Interfaces:**
- Consumes: `toon` (Task 1), `router.Decision` (Task 2), `environment.Context` (Task 3).
- Produces:
  - `observations.Lookup(observation, status, stale_reason)` — `status` is
    `"current"`, `"invalidated"` or `"absent"`; `observation` is `None` unless
    `status == "current"`.
  - `observations.lookup(root, env) -> Lookup`.
  - `observations.record_qualification(root, env, result, probes, today) -> dict`.
  - `observations.record_event(root, env, event, symptom, config, current_profile) -> Outcome`
    where `event` is `"degraded"` or `"success"`, and
    `Outcome(action, reload_source, escalated_profile, message)` has `action` in
    `{"recover_and_retry", "escalate", "recorded", "reduced"}`.
  - `observations.recovery_source(root, symptom) -> str`.

- [ ] **Step 1: Write the recovery map**

`.agents/context/RECOVERY.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
# When execution degrades, reload the authoritative source before inflating the
# prompt. One bounded retry follows. Escalate only if recovery and retry fail.
version: 1

symptoms:
  skill_path_wrong: .agents/skills/CATALOG.toon
  operating_rule_missed: AGENTS.md
  behaviour_incorrect: specs/capabilities/
  architecture_assumption_wrong: PROJECT_PROFILE.toon
  verification_inadequate: docs/validation.md
  command_misused: .agentic-template/bin/project help
  knowledge_missing: .agents/knowledge/index.md
  unknown: AGENTS.md

stop_conditions:
  - an irreversible action is requested without explicit authorisation
  - a required verification command cannot be run and no alternative is recorded
  - the authoritative source contradicts the working assumption
```

Create the store directory:

```bash
mkdir -p .agents/context/observations && touch .agents/context/observations/.gitkeep
```

- [ ] **Step 2: Write the failing test**

First add the scratch-repository helper to `.agentic-template/tests/_support.py`, since
this is the first test module that needs a mutable copy of the repository (Tasks 6, 8 and
13 reuse it):

```python
import shutil
import tempfile


def temp_repo():
    """Copy the repository to a scratch directory. Returns (TemporaryDirectory, Path).

    The caller keeps the TemporaryDirectory alive and calls cleanup() in tearDown.
    """
    tmp = tempfile.TemporaryDirectory(prefix="context-router-test-")
    root = Path(tmp.name) / "repo"
    shutil.copytree(
        ROOT, root, symlinks=True, ignore=shutil.ignore_patterns(".git", ".superpowers")
    )
    return tmp, root
```

Then replace the inline `copytree` in `test_environment.py`'s
`test_changes_when_a_contract_file_changes` with a call to it — this is its second
occurrence, which is where the shared helper earns its place.

`.agentic-template/tests/test_observations.py`:

```python
import unittest
from pathlib import Path

import _support
import environment
import observations
import router
import toon

CONFIG = toon.loads(open(_support.ROOT / ".agents/context/ROUTER.toon").read())


class ObservationTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = _support.temp_repo()
        for stale in (self.root / ".agents/context/observations").glob("*.toon"):
            stale.unlink()
        self.env = environment.build(self.root, {}, model="test-model", runtime="codex")

    def tearDown(self):
        self.tmp.cleanup()


class TestLookup(ObservationTestCase):
    def test_absent_when_nothing_recorded(self):
        found = observations.lookup(self.root, self.env)
        self.assertEqual(found.status, "absent")
        self.assertIsNone(found.observation)

    def test_current_after_recording(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        found = observations.lookup(self.root, self.env)
        self.assertEqual(found.status, "current")
        self.assertEqual(found.observation["result"], "pass")

    def test_invalidated_when_the_contract_changes(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        moved = environment.build(self.root, {}, model="test-model", runtime="codex")
        found = observations.lookup(self.root, moved)
        self.assertEqual(found.status, "invalidated")
        self.assertIsNone(found.observation)
        self.assertIn("AGENTS.md", found.stale_reason)

    def test_invalidated_observation_routes_to_standard(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        moved = environment.build(self.root, {}, model="test-model", runtime="codex")
        found = observations.lookup(self.root, moved)
        decision = router.resolve(
            moved,
            router.Task(risk="low", effort="standard", skill_id=None, paths=[]),
            CONFIG,
            [],
            found.observation,
        )
        self.assertEqual(decision.profile, "standard")


class TestDegradationLadder(ObservationTestCase):
    def setUp(self):
        super().setUp()
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")

    def test_first_degradation_recovers_before_escalating(self):
        outcome = observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        self.assertEqual(outcome.action, "recover_and_retry")
        self.assertEqual(outcome.reload_source, ".agents/skills/CATALOG.toon")
        self.assertIsNone(outcome.escalated_profile)
        self.assertIsNone(
            observations.lookup(self.root, self.env).observation["escalated_profile"]
        )

    def test_second_degradation_escalates_exactly_one_step(self):
        observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        outcome = observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        self.assertEqual(outcome.action, "escalate")
        self.assertEqual(outcome.escalated_profile, "standard")

    def test_escalation_stops_at_guarded(self):
        for _ in range(8):
            observations.record_event(
                self.root, self.env, "degraded", "unknown", CONFIG, "guarded"
            )
        self.assertEqual(
            observations.lookup(self.root, self.env).observation["escalated_profile"],
            "guarded",
        )

    def test_reduction_needs_the_configured_run_of_successes(self):
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        needed = CONFIG["degradation"]["reduce_after_successes"]
        for index in range(needed - 1):
            outcome = observations.record_event(
                self.root, self.env, "success", None, CONFIG, "standard"
            )
            self.assertEqual(outcome.action, "recorded", f"success {index + 1}")
        outcome = observations.record_event(
            self.root, self.env, "success", None, CONFIG, "standard"
        )
        self.assertEqual(outcome.action, "reduced")
        self.assertIsNone(outcome.escalated_profile)

    def test_reduction_is_refused_while_qualification_is_not_passing(self):
        # Asserts on every iteration, not just the last: checking only the final
        # action lets a missing `result == "pass"` guard hide, because reduction
        # fires mid-loop and then falls back to "recorded" once the escalation
        # has already been cleared.
        observations.record_qualification(self.root, self.env, "fail", {}, "2026-07-26")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        escalated = observations.lookup(self.root, self.env).observation["escalated_profile"]
        self.assertIsNotNone(escalated, "two degradations must have escalated")
        needed = CONFIG["degradation"]["reduce_after_successes"]
        for index in range(needed + 2):
            outcome = observations.record_event(
                self.root, self.env, "success", None, CONFIG, "standard"
            )
            with self.subTest(success=index + 1):
                self.assertEqual(outcome.action, "recorded")
                self.assertEqual(
                    observations.lookup(self.root, self.env).observation["escalated_profile"],
                    escalated,
                )

    def test_recorded_file_is_valid_toon(self):
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        path = observations.path_for(self.root, self.env)
        data = toon.loads(path.read_text())
        self.assertEqual(data["observation"]["model_id"], "test-model")
        self.assertEqual(data["observation"]["runtime"], "codex")


class TestRecoverySource(ObservationTestCase):
    def test_known_symptom_maps_to_its_source(self):
        self.assertEqual(
            observations.recovery_source(self.root, "verification_inadequate"),
            "docs/validation.md",
        )

    def test_unknown_symptom_falls_back_to_the_contract(self):
        self.assertEqual(
            observations.recovery_source(self.root, "something-new"), "AGENTS.md"
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'observations'`

- [ ] **Step 4: Write the implementation**

`.agentic-template/lib/observations.py`:

```python
"""Recorded evidence about how a model-runtime pair actually behaves here.

Observations are scoped to a fingerprint over model, runtime, tools and the
contract files. Any material change to those invalidates the record rather than
silently carrying a stale capability claim forward.

Escalation is fast: one degradation after the retry budget is spent raises the
profile a step. Reduction is cautious: it needs a run of successes and a
currently passing qualification.
"""
from collections import namedtuple
from datetime import date
from pathlib import Path

import environment
import toon

Lookup = namedtuple("Lookup", "observation status stale_reason")
Outcome = namedtuple("Outcome", "action reload_source escalated_profile message")

STORE = ".agents/context/observations"


def path_for(root, env):
    return Path(root) / STORE / f"{env.fingerprint}.toon"


def _all(root):
    for path in sorted((Path(root) / STORE).glob("*.toon")):
        yield path, toon.loads(path.read_text())["observation"]


def _changed_contract_files(root, recorded):
    """Name the contract files whose hash no longer matches the recording."""
    changed = []
    stored_by_path = {
        entry["path"]: entry["digest"] for entry in recorded.get("contract_files") or []
    }
    for relative in environment.CONTRACT_FILES:
        stored = stored_by_path.get(relative)
        current = environment.file_digest(Path(root) / relative)
        if stored and stored != current:
            changed.append(relative)
    return changed


def lookup(root, env):
    """Find the observation for this exact environment, or explain its absence."""
    path = path_for(root, env)
    if path.exists():
        return Lookup(toon.loads(path.read_text())["observation"], "current", None)
    for _, recorded in _all(root):
        if recorded.get("model_id") == env.model_id and recorded.get("runtime") == env.runtime:
            changed = _changed_contract_files(root, recorded)
            reason = (
                "changed since the observation: " + ", ".join(changed)
                if changed
                else "environment fingerprint changed"
            )
            return Lookup(None, "invalidated", reason)
    return Lookup(None, "absent", None)


def _blank(root, env, today):
    return {
        "fingerprint": env.fingerprint,
        "model_id": env.model_id,
        "runtime": env.runtime,
        "tools": list(env.capabilities),
        "contract_fingerprint": env.contract_fingerprint,
        # A list of maps, not a dict: TOON keys match [A-Za-z_][A-Za-z0-9_.-]*,
        # so repository paths can never be keys.
        "contract_files": [
            {"path": relative, "digest": environment.file_digest(Path(root) / relative)}
            for relative in environment.CONTRACT_FILES
        ],
        "qualification_version": 0,
        "result": "uncertain",
        "probe_results": {},
        "recorded": today,
        "degradations": 0,
        "retry_available": True,
        "escalated_profile": None,
        "successes_since_degradation": 0,
        "events": [],
    }


def _load_or_blank(root, env, today):
    path = path_for(root, env)
    if path.exists():
        return toon.loads(path.read_text())["observation"]
    return _blank(root, env, today)


def _save(root, record):
    path = Path(root) / STORE / f"{record['fingerprint']}.toon"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(toon.dumps({"observation": record}))


def record_qualification(root, env, result, probes, today=None):
    """Store a qualification result. Escalation state is left untouched."""
    today = today or date.today().isoformat()
    record = _load_or_blank(root, env, today)
    record["result"] = result
    record["probe_results"] = dict(probes)
    record["recorded"] = today
    _save(root, record)
    return record


def recovery_source(root, symptom):
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    symptoms = data["symptoms"]
    return symptoms.get(symptom) or symptoms["unknown"]


def _next_profile(config, current):
    order = config["order"]
    index = min(order.index(current) + 1, len(order) - 1)
    return order[index]


def record_event(root, env, event, symptom, config, current_profile, today=None):
    """Apply one degradation or success to the escalation ladder."""
    today = today or date.today().isoformat()
    record = _load_or_blank(root, env, today)
    record["events"].append({"date": today, "event": event, "symptom": symptom or "none"})

    if event == "degraded":
        source = recovery_source(root, symptom or "unknown")
        record["successes_since_degradation"] = 0
        if record["retry_available"]:
            record["retry_available"] = False
            _save(root, record)
            return Outcome(
                "recover_and_retry",
                source,
                record["escalated_profile"],
                f"reload {source}, then retry once before increasing context",
            )
        record["degradations"] += 1
        record["retry_available"] = True
        base = record["escalated_profile"] or current_profile
        record["escalated_profile"] = _next_profile(config, base)
        _save(root, record)
        return Outcome(
            "escalate",
            source,
            record["escalated_profile"],
            f"recovery and retry did not restore correctness; escalated to "
            f"{record['escalated_profile']}",
        )

    if event != "success":
        raise ValueError(f"unknown event: {event}; expected 'degraded' or 'success'")

    record["successes_since_degradation"] += 1
    record["retry_available"] = True
    needed = config["degradation"]["reduce_after_successes"]
    can_reduce = (
        record["escalated_profile"]
        and record["result"] == "pass"
        and record["successes_since_degradation"] >= needed
    )
    if can_reduce:
        record["escalated_profile"] = None
        record["successes_since_degradation"] = 0
        _save(root, record)
        return Outcome("reduced", None, None, f"{needed} clean runs; escalation removed")
    _save(root, record)
    return Outcome(
        "recorded",
        None,
        record["escalated_profile"],
        f"{record['successes_since_degradation']} of {needed} clean runs toward reduction",
    )
```

- [ ] **Step 5: Add the digest helper the store depends on**

Append to `.agentic-template/lib/environment.py`:

```python
def file_digest(path):
    """Stable per-file hash used for observation invalidation reporting."""
    path = Path(path)
    data = path.read_bytes() if path.exists() else b"<absent>"
    return hashlib.sha256(data).hexdigest()[:16]
```

Then rewrite `contract_fingerprint` to use it, so the two can never disagree:

```python
def contract_fingerprint(root):
    """Hash the files whose change should invalidate recorded observations."""
    digest = hashlib.sha256()
    for relative in CONTRACT_FILES:
        digest.update(relative.encode())
        digest.update(file_digest(Path(root) / relative).encode())
    return digest.hexdigest()[:16]
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS, 61 tests

- [ ] **Step 7: Ignore recorded observations in git for the template only**

Observations are environment-specific evidence, not template content. Add to
`.gitignore`:

```
# Context router: recorded observations are environment-specific evidence
.agents/context/observations/*.toon
```

Generated projects may choose to commit theirs; `.agents/context/README.md` (Task 14)
states the tradeoff.

- [ ] **Step 8: Commit**

```bash
git add .agents/context/RECOVERY.toon .agents/context/observations/.gitkeep .gitignore \
        .agentic-template/lib/observations.py .agentic-template/lib/environment.py \
        .agentic-template/tests/test_observations.py
git commit -m "feat(context-router): record observations with invalidation and bounded escalation"
```

---

### Task 5: Skill metadata, catalog resolution and layer discovery

**Files:**
- Create: `.agentic-template/lib/skills.py`
- Test: `.agentic-template/tests/test_skill_layers.py`

**Interfaces:**
- Consumes: `toon` (Task 1).
- Produces:
  - `skills.LAYERS` — the ordered tuple
    `("summary", "core", "procedure", "verification", "examples", "failure_modes", "references")`.
  - `skills.LAYER_FILES` — mapping of layer name to conventional filename
    (`summary` maps to `SKILL.md`).
  - `skills.parse_frontmatter(text) -> (dict, str)`.
  - `skills.Skill(id, path, directory, meta, layers)` where `layers` is
    `dict[str, str]` of layer name to repository-relative path, containing only files
    that exist.
  - `skills.load_catalog(root) -> dict[str, dict]`.
  - `skills.resolve(root, skill_id=None, trigger=None) -> Skill`, raising
    `skills.SkillError` with the catalog path in the message when unresolvable.
  - `skills.all_skills(root) -> list[Skill]` — filesystem walk, used by the validator.

- [ ] **Step 1: Write the failing test**

`.agentic-template/tests/test_skill_layers.py`:

```python
import unittest

import _support  # noqa: F401
import skills

ROOT = _support.ROOT


class TestFrontmatter(unittest.TestCase):
    def test_parses_metadata_and_returns_the_body(self):
        text = (
            "---\n"
            "name: review-loop\n"
            'description: "Cyclic clean-up: boy-scout and smells."\n'
            "id: SKILL-review-loop\n"
            "triggers: [before_merge, boy_scout_cleanup]\n"
            "default_task_risk: normal\n"
            "layers:\n"
            "  core: core.md\n"
            "---\n"
            "\n"
            "# Review Loop\n"
        )
        meta, body = skills.parse_frontmatter(text)
        self.assertEqual(meta["id"], "SKILL-review-loop")
        self.assertEqual(meta["description"], "Cyclic clean-up: boy-scout and smells.")
        self.assertEqual(meta["triggers"], ["before_merge", "boy_scout_cleanup"])
        self.assertEqual(meta["layers"], {"core": "core.md"})
        self.assertTrue(body.lstrip().startswith("# Review Loop"))

    def test_missing_frontmatter_is_an_error(self):
        with self.assertRaises(skills.SkillError):
            skills.parse_frontmatter("# No frontmatter\n")

    def test_colon_in_a_value_is_kept_as_text(self):
        # toon partitions on the first colon, so prose containing one is safe.
        meta, _ = skills.parse_frontmatter(
            "---\nname: a\ndescription: Route work: fast and cheap.\n---\n"
        )
        self.assertEqual(meta["description"], "Route work: fast and cheap.")

    def test_malformed_frontmatter_reports_how_to_fix_it(self):
        with self.assertRaises(skills.SkillError) as caught:
            skills.parse_frontmatter("---\nname: a\n   description: b\n---\n")
        message = str(caught.exception)
        self.assertIn("not parseable", message)
        self.assertIn("two-space", message)

    def test_bracket_leading_value_is_read_as_a_list_not_text(self):
        # The real hazard the error message warns about.
        meta, _ = skills.parse_frontmatter(
            "---\nname: a\ndescription: [not, prose]\n---\n"
        )
        self.assertEqual(meta["description"], ["not", "prose"])


class TestCatalogResolution(unittest.TestCase):
    def test_every_skill_on_disk_is_in_the_catalog(self):
        catalogued = {entry["path"] for entry in skills.load_catalog(ROOT).values()}
        on_disk = {
            str(skill.path.relative_to(ROOT / ".agents/skills")) for skill in skills.all_skills(ROOT)
        }
        self.assertEqual(on_disk - catalogued, set(), "skills missing from CATALOG.toon")

    def test_every_catalog_path_exists(self):
        for skill_id, entry in skills.load_catalog(ROOT).items():
            with self.subTest(skill=skill_id):
                self.assertTrue((ROOT / ".agents/skills" / entry["path"]).exists())

    def test_resolves_by_id(self):
        found = skills.resolve(ROOT, skill_id="review_loop")
        self.assertTrue(str(found.path).endswith("workflow/review-loop/SKILL.md"))

    def test_resolves_by_trigger(self):
        found = skills.resolve(ROOT, trigger="before_merge_or_boy_scout_cleanup")
        self.assertEqual(found.id, "review_loop")

    def test_unknown_id_names_the_catalog_in_the_error(self):
        with self.assertRaises(skills.SkillError) as caught:
            skills.resolve(ROOT, skill_id="not-a-skill")
        self.assertIn("CATALOG.toon", str(caught.exception))


class TestLayerDiscovery(unittest.TestCase):
    def test_summary_layer_is_always_the_skill_file(self):
        found = skills.resolve(ROOT, skill_id="review_loop")
        self.assertTrue(found.layers["summary"].endswith("SKILL.md"))

    def test_only_existing_layer_files_are_reported(self):
        for skill in skills.all_skills(ROOT):
            for layer, relative in skill.layers.items():
                with self.subTest(skill=skill.id, layer=layer):
                    self.assertTrue((ROOT / relative).exists())

    def test_layer_names_stay_inside_the_taxonomy(self):
        for skill in skills.all_skills(ROOT):
            for layer in skill.layers:
                with self.subTest(skill=skill.id, layer=layer):
                    self.assertIn(layer, skills.LAYERS)


if __name__ == "__main__":
    unittest.main()
```

Note: `test_every_skill_on_disk_is_in_the_catalog` fails on the current repository
because of conflict C1. Fixing it is Step 5 of this task.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'skills'`

- [ ] **Step 3: Write the implementation**

`.agentic-template/lib/skills.py`:

```python
"""Catalog-first skill resolution and taxonomy layer discovery.

Skill paths always resolve through .agents/skills/CATALOG.toon. Frontmatter in
SKILL.md is the single canonical home for a skill's metadata; the catalog holds
only the index fields needed to find it without opening every file.
"""
from dataclasses import dataclass
from pathlib import Path

import toon

LAYERS = (
    "summary",
    "core",
    "procedure",
    "verification",
    "examples",
    "failure_modes",
    "references",
)

LAYER_FILES = {
    "summary": "SKILL.md",
    "core": "core.md",
    "procedure": "procedure.md",
    "verification": "verification.md",
    "examples": "examples.md",
    "failure_modes": "failure-modes.md",
    "references": "references.md",
}

SKILL_ROOT = ".agents/skills"
CATALOG = f"{SKILL_ROOT}/CATALOG.toon"


class SkillError(ValueError):
    """Raised when a skill cannot be resolved or its metadata is malformed."""


@dataclass(frozen=True)
class Skill:
    id: str
    path: Path
    directory: Path
    meta: dict
    layers: dict


def parse_frontmatter(text):
    """Split YAML frontmatter from the body. The subset matches toon.loads."""
    if not text.startswith("---\n"):
        raise SkillError("missing frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise SkillError("unterminated frontmatter")
    raw = text[4:end]
    try:
        meta = toon.loads(raw)
    except toon.ToonError as error:
        raise SkillError(
            f"frontmatter is not parseable ({error}); use two-space indentation, no "
            f"tabs, and quote any value that starts with '['"
        ) from error
    return meta, text[end + 4 :]


def load_catalog(root):
    path = Path(root) / CATALOG
    if not path.exists():
        raise SkillError(f"missing {CATALOG}")
    return toon.loads(path.read_text())["skills"]


def _layers_for(root, directory, meta):
    """Declared layers, restricted to files that actually exist."""
    declared = dict(meta.get("layers") or {})
    found = {"summary": str((directory / "SKILL.md").relative_to(Path(root)))}
    for layer, filename in declared.items():
        if layer not in LAYERS:
            raise SkillError(f"{directory}: unknown taxonomy layer '{layer}'")
        candidate = directory / filename
        if candidate.exists():
            found[layer] = str(candidate.relative_to(Path(root)))
    return found


def _build(root, skill_id, relative_path):
    path = Path(root) / SKILL_ROOT / relative_path
    if not path.exists():
        raise SkillError(f"{CATALOG} points at missing file: {relative_path}")
    meta, _ = parse_frontmatter(path.read_text())
    directory = path.parent
    return Skill(
        id=skill_id,
        path=path,
        directory=directory,
        meta=meta,
        layers=_layers_for(root, directory, meta),
    )


def resolve(root, skill_id=None, trigger=None):
    """Look up one skill by catalog id or by trigger. Never guesses a path."""
    catalog = load_catalog(root)
    if skill_id:
        normalised = skill_id.replace("-", "_")
        entry = catalog.get(normalised)
        if entry is None:
            raise SkillError(
                f"unknown skill '{skill_id}'; resolve ids through {CATALOG} "
                f"({len(catalog)} entries)"
            )
        return _build(root, normalised, entry["path"])
    if trigger:
        for candidate, entry in catalog.items():
            if entry.get("trigger") == trigger:
                return _build(root, candidate, entry["path"])
        raise SkillError(f"no skill in {CATALOG} declares trigger '{trigger}'")
    raise SkillError("resolve() needs skill_id or trigger")


def all_skills(root):
    """Walk the filesystem. Used by the validator to detect catalog drift."""
    found = []
    catalog = load_catalog(root)
    by_path = {entry["path"]: name for name, entry in catalog.items()}
    base = Path(root) / SKILL_ROOT
    for path in sorted(base.rglob("SKILL.md")):
        relative = str(path.relative_to(base))
        found.append(_build(root, by_path.get(relative, f"uncatalogued:{relative}"), relative))
    return found
```

- [ ] **Step 4: Run the tests and confirm only the catalog-drift test fails**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: one failure — `test_every_skill_on_disk_is_in_the_catalog`, listing the eight
paths from conflict C1.

- [ ] **Step 5: Fix conflict C1 by cataloguing the eight unreachable skills**

Append to `.agents/skills/CATALOG.toon`:

```toon
  discover:
    path: workflow/discover/SKILL.md
    trigger: evidence_needed_before_decision

  plan_task:
    path: workflow/plan-task/SKILL.md
    trigger: bounded_work_needs_a_plan

  specify:
    path: workflow/specify/SKILL.md
    trigger: change_needs_a_structured_spec

  implement_slice:
    path: workflow/implement-slice/SKILL.md
    trigger: thin_slice_ready_to_build

  test_change:
    path: workflow/test-change/SKILL.md
    trigger: change_scenarios_need_tests

  architecture_review:
    path: workflow/architecture-review/SKILL.md
    trigger: boundary_or_dependency_direction_in_question

  red_team:
    path: workflow/red-team/SKILL.md
    trigger: adversarial_review_requested

  promote_knowledge:
    path: workflow/promote-knowledge/SKILL.md
    trigger: inbox_proposal_has_supporting_evidence
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS, 74 tests

- [ ] **Step 7: Commit**

```bash
git add .agentic-template/lib/skills.py .agentic-template/tests/test_skill_layers.py \
        .agents/skills/CATALOG.toon
git commit -m "feat(context-router): resolve skills through the catalog and discover taxonomy layers

Catalogues the eight workflow skills that were unreachable under the
resolve-through-CATALOG rule."
```

---

### Task 6: Task-risk classification and context plan assembly

**Files:**
- Create: `.agents/context/risk-rules.toon`
- Create: `.agentic-template/lib/plan.py`
- Test: `.agentic-template/tests/test_explain.py`

**Interfaces:**
- Consumes: `toon`, `router`, `environment`, `observations`, `skills` (Tasks 1-5).
- Produces:
  - `plan.classify_risk(root, paths, explicit) -> (risk, source)` where `source` is
    `"flag"`, `"default"` or `"risk-rules:<id>[,<id>]"`.
  - `plan.build(root, env, task, config, decision, skill, lookup) -> dict` — the context
    plan, keyed `context_plan`.
  - `plan.render_toon(document) -> str` and `plan.render_text(document) -> str`.

- [ ] **Step 1: Write the risk rules**

`.agents/context/risk-rules.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
# Path globs use fnmatch semantics, where * crosses directory separators.
# Every touched path is matched against the first rule that accepts it; the
# highest risk across all touched paths wins.
version: 1
default: normal

rules:
  - id: operating_contract
    paths: [AGENTS.md, .agents/context/*, .agents/skills/CATALOG.toon]
    risk: high
  - id: released_capability
    paths: [specs/capabilities/*]
    risk: high
  - id: infrastructure
    paths: [compose.yaml, infra/*, .github/workflows/*, flake.nix, flake.lock]
    risk: high
  - id: documentation
    paths: [docs/*, "*.md"]
    risk: low
```

- [ ] **Step 2: Add the synthetic-skill helper**

Append to `.agentic-template/tests/_support.py`. Building a fixture skill rather than
asserting against a real one keeps these tests stable when real skills gain or lose a
layer, and lets one skill exercise every layer at once:

```python
import skills  # resolves via the sys.path insert above


def write_skill(root, relative, layers=(), verification=("fixture-verify",), trigger=None):
    """Create a synthetic layered skill in a scratch repo and catalogue it.

    Returns the catalog id. Every named layer gets a real file with enough
    content to pass the emptiness check in `project context check`.
    """
    directory = Path(root) / ".agents/skills" / relative
    directory.mkdir(parents=True, exist_ok=True)
    name = relative.rsplit("/", 1)[-1]
    skill_id = name.replace("-", "_")
    resolved_trigger = trigger or f"{skill_id}_needed"

    declared = "".join(f"  {layer}: {skills.LAYER_FILES[layer]}\n" for layer in layers)
    listed = "".join(f"  - {command}\n" for command in verification)
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Synthetic skill used by the context router test suite.\n"
        f"id: SKILL-{name}\n"
        f"triggers: [{resolved_trigger}]\n"
        "default_task_risk: normal\n"
        + (f"layers:\n{declared}" if declared else "")
        + f"verification:\n{listed}"
        "status: active\n"
        "---\n"
        f"\n# {name}\n\nSummary layer for the synthetic {name} fixture skill.\n"
    )
    for layer in layers:
        (directory / skills.LAYER_FILES[layer]).write_text(
            f"# {name} — {layer}\n\n"
            f"Synthetic {layer} layer content for the context router test suite.\n"
        )

    catalog = Path(root) / ".agents/skills/CATALOG.toon"
    catalog.write_text(
        catalog.read_text()
        + f"\n  {skill_id}:\n"
        f"    path: {relative}/SKILL.md\n"
        f"    trigger: {resolved_trigger}\n"
    )
    return skill_id
```

- [ ] **Step 3: Write the failing test**

`.agentic-template/tests/test_explain.py`:

```python
import unittest

import _support
import environment
import observations
import plan
import router
import skills
import toon

ROOT = _support.ROOT
CONFIG = toon.loads(open(ROOT / ".agents/context/ROUTER.toon").read())

ALL_LAYERS = ("core", "procedure", "verification", "examples", "failure_modes", "references")
FIXTURE_VERIFICATION = ["fixture-verify-a", "fixture-verify-b"]


class TestRiskClassification(unittest.TestCase):
    def test_explicit_flag_wins(self):
        self.assertEqual(plan.classify_risk(ROOT, ["docs/a.md"], "high"), ("high", "flag"))

    def test_no_paths_uses_the_configured_default(self):
        self.assertEqual(plan.classify_risk(ROOT, [], None), ("normal", "default"))

    def test_capability_spec_is_high_risk(self):
        risk, source = plan.classify_risk(ROOT, ["specs/capabilities/CAP-001.toon"], None)
        self.assertEqual(risk, "high")
        self.assertIn("released_capability", source)

    def test_documentation_is_low_risk(self):
        risk, _ = plan.classify_risk(ROOT, ["docs/wiki/index.md"], None)
        self.assertEqual(risk, "low")

    def test_highest_risk_across_touched_paths_wins(self):
        risk, source = plan.classify_risk(
            ROOT, ["docs/wiki/index.md", "compose.yaml"], None
        )
        self.assertEqual(risk, "high")
        self.assertIn("infrastructure", source)

    def test_unmatched_path_uses_the_default(self):
        risk, _ = plan.classify_risk(ROOT, ["src/whatever.rs"], None)
        self.assertEqual(risk, "normal")


class LayerTestCase(unittest.TestCase):
    """Plans are built against a synthetic fully-layered skill.

    Using a fixture rather than a real skill keeps these assertions stable when
    real skills gain or lose a layer, and lets one skill exercise every layer.
    """

    def setUp(self):
        self.tmp, self.root = _support.temp_repo()
        _support.write_skill(
            self.root,
            "workflow/fixture-skill",
            layers=ALL_LAYERS,
            verification=FIXTURE_VERIFICATION,
            trigger="fixture_skill_needed",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def document_for(self, qualification="pass", risk="low", effort="standard"):
        env = environment.build(self.root, {}, model="test-model", runtime="codex")
        skill = skills.resolve(self.root, skill_id="fixture_skill")
        task = router.Task(risk=risk, effort=effort, skill_id=skill.id, paths=[])
        lookup = observations.Lookup(
            {"result": qualification, "escalated_profile": None}, "current", None
        )
        decision = router.resolve(env, task, CONFIG, [], lookup.observation)
        return plan.build(self.root, env, task, CONFIG, decision, skill, lookup)["context_plan"]

    def skill_layers(self, document):
        return {entry["layer"] for entry in document["preload"] if entry.get("skill")}


class TestProfileSelectsLayers(LayerTestCase):
    def test_lean_preloads_only_the_summary_layer(self):
        document = self.document_for("pass", risk="low")
        self.assertEqual(document["decision"]["profile"], "lean")
        self.assertEqual(self.skill_layers(document), {"summary"})

    def test_standard_adds_the_core_layer(self):
        document = self.document_for("fail", risk="low")
        self.assertEqual(self.skill_layers(document), {"summary", "core"})

    def test_guarded_adds_procedure_verification_and_failure_modes(self):
        document = self.document_for("pass", risk="high")
        self.assertEqual(
            self.skill_layers(document),
            {"summary", "core", "procedure", "verification", "failure_modes"},
        )

    def test_examples_and_references_are_never_preloaded(self):
        for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high")):
            layers = self.skill_layers(self.document_for(qualification, risk=risk))
            with self.subTest(risk=risk):
                self.assertNotIn("examples", layers)
                self.assertNotIn("references", layers)

    def test_deferred_layers_are_the_complement_of_preloaded_ones(self):
        document = self.document_for("fail", risk="low")
        preloaded = self.skill_layers(document)
        deferred = {entry["layer"] for entry in document["defer"]}
        self.assertEqual(preloaded & deferred, set())
        skill = skills.resolve(self.root, skill_id="fixture_skill")
        self.assertEqual(preloaded | deferred, set(skill.layers))

    def test_a_skill_without_a_layer_never_reports_it(self):
        _support.write_skill(
            self.root, "workflow/thin-skill", layers=("core",), trigger="thin_skill_needed"
        )
        env = environment.build(self.root, {}, model="test-model", runtime="codex")
        skill = skills.resolve(self.root, skill_id="thin_skill")
        task = router.Task(risk="high", effort="standard", skill_id=skill.id, paths=[])
        decision = router.resolve(env, task, CONFIG, [], {"result": "pass"})
        document = plan.build(
            self.root, env, task, CONFIG, decision, skill,
            observations.Lookup({"result": "pass"}, "current", None),
        )["context_plan"]
        self.assertEqual(self.skill_layers(document), {"summary", "core"})
        self.assertEqual(document["defer"], [])


class TestRoutingNeverChangesOutcomes(LayerTestCase):
    def test_required_verification_is_identical_in_every_profile(self):
        required = [
            self.document_for(qualification, risk=risk)["verification"]["required"]
            for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high"))
        ]
        self.assertEqual(required[0], FIXTURE_VERIFICATION)
        self.assertEqual(required[0], required[1])
        self.assertEqual(required[1], required[2])

    def test_effort_changes_directives_but_not_the_profile_or_verification(self):
        light = self.document_for("pass", effort="minimal")
        deep = self.document_for("pass", effort="deep")
        self.assertEqual(light["decision"]["profile"], deep["decision"]["profile"])
        self.assertEqual(light["verification"], deep["verification"])
        self.assertNotEqual(light["effort_directives"], deep["effort_directives"])

    def test_recovery_map_is_identical_in_every_profile(self):
        maps = [
            self.document_for(qualification, risk=risk)["recovery"]
            for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high"))
        ]
        self.assertTrue(maps[0])
        self.assertEqual(maps[0], maps[1])
        self.assertEqual(maps[1], maps[2])


class TestProvenanceAndShape(LayerTestCase):
    def test_every_preloaded_source_carries_a_digest(self):
        for entry in self.document_for("pass")["preload"]:
            with self.subTest(source=entry["source"]):
                self.assertRegex(entry["sha"], r"^[0-9a-f]{16}$")

    def test_plan_renders_as_parseable_toon_with_all_sections(self):
        document = self.document_for("pass")
        parsed = toon.loads(plan.render_toon({"context_plan": document}))["context_plan"]
        for section in (
            "decision",
            "environment",
            "task",
            "preload",
            "defer",
            "verification",
            "recovery",
            "effort_directives",
        ):
            self.assertIn(section, parsed)

    def test_text_rendering_states_the_profile_and_reasons(self):
        text = plan.render_text({"context_plan": self.document_for("pass")})
        self.assertIn("PROFILE", text)
        self.assertIn("lean", text)
        self.assertIn("qualification result is pass", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'plan'`

- [ ] **Step 5: Write the implementation**

`.agentic-template/lib/plan.py`:

```python
"""Assemble the context plan a resolved profile implies.

The profile chooses which taxonomy layers are preloaded and which are deferred.
It never chooses the required verification, the recovery map or the acceptance
criteria: those are identical under every profile by construction.
"""
from fnmatch import fnmatch
from pathlib import Path

import environment
import router
import toon


def _risk_rules(root):
    return toon.loads((Path(root) / ".agents/context/risk-rules.toon").read_text())


def classify_risk(root, paths, explicit=None):
    """Return (risk, source). The highest risk across touched paths wins."""
    if explicit:
        if explicit not in router.RISKS:
            raise router.RouterError(
                f"unknown risk: {explicit}; expected one of {list(router.RISKS)}"
            )
        return explicit, "flag"
    config = _risk_rules(root)
    if not paths:
        return config["default"], "default"
    best = config["default"]
    matched = []
    for path in paths:
        for rule in config["rules"]:
            if any(fnmatch(path, pattern) for pattern in rule["paths"]):
                if router.RISKS.index(rule["risk"]) > router.RISKS.index(best):
                    best = rule["risk"]
                matched.append(rule["id"])
                break
    if not matched:
        return config["default"], "default"
    ordered = sorted(set(matched))
    return best, "risk-rules:" + ",".join(ordered)


def _entry(root, relative, layer, skill_id=None):
    item = {
        "source": relative,
        "layer": layer,
        "sha": environment.file_digest(Path(root) / relative),
    }
    if skill_id:
        item["skill"] = skill_id
    return item


def _always_preload(root, config, profile):
    sources = config["always_preload_sources"]
    seen = set()
    entries = []
    for name in config["profiles"][profile]["always_preload"]:
        relative = sources.get(name)
        if not relative or relative in seen:
            continue
        seen.add(relative)
        entries.append(_entry(root, relative, name))
    return entries


def _recovery(root):
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    return [
        {"symptom": symptom, "reload": source}
        for symptom, source in data["symptoms"].items()
        if symptom != "unknown"
    ]


def _pending_recovery(root, observation):
    """True while the bounded retry after a degradation has not been spent."""
    if not observation or observation.get("retry_available", True):
        return None
    events = observation.get("events") or []
    symptom = events[-1]["symptom"] if events else "unknown"
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    return {
        "symptom": symptom,
        "reload": data["symptoms"].get(symptom) or data["symptoms"]["unknown"],
        "then": "retry once before increasing context",
    }


def build(root, env, task, config, decision, skill, lookup):
    """Render the full routing decision and its context sets as data."""
    profile = decision.profile
    settings = config["profiles"][profile]
    preload = _always_preload(root, config, profile)
    defer = []
    verification = []
    if skill:
        for layer in settings["preload_layers"]:
            if layer in skill.layers:
                preload.append(_entry(root, skill.layers[layer], layer, skill.id))
        for layer, relative in skill.layers.items():
            if layer not in settings["preload_layers"]:
                defer.append(
                    {
                        "source": relative,
                        "layer": layer,
                        "skill": skill.id,
                        "load_when": "needed for this step, or after a degradation event",
                    }
                )
        verification = list(skill.meta.get("verification") or [])

    document = {
        "version": 1,
        "decision": {
            "profile": profile,
            "reasons": list(decision.reasons),
            "precedence_applied": [f"{step}:{outcome}" for step, outcome in decision.trace],
        },
        "environment": {
            "model_id": env.model_id,
            "model_id_use": "diagnostics_and_override_matching_only",
            "runtime": env.runtime,
            "runtime_capabilities": list(env.capabilities),
            "fingerprint": env.fingerprint,
            "contract_fingerprint": env.contract_fingerprint,
            "observation_status": lookup.status,
            "observation_note": lookup.stale_reason or "none",
        },
        "task": {
            "risk": task.risk,
            "effort": task.effort,
            "skill": skill.id if skill else "none",
        },
        "preload": preload,
        "defer": defer,
        "verification": {"required": verification},
        "recovery": _recovery(root),
        "effort_directives": dict(config["effort"][task.effort]),
        "independent_review": settings["independent_review"],
    }
    pending = _pending_recovery(root, lookup.observation)
    if pending:
        document["recover_first"] = pending
    return {"context_plan": document}


def render_toon(document):
    return toon.dumps(document)


def render_text(document):
    body = document["context_plan"]
    lines = [f"PROFILE  {body['decision']['profile']}", ""]
    lines.append("WHY")
    for reason in body["decision"]["reasons"]:
        lines.append(f"  - {reason}")
    lines.append("")
    lines.append("PRECEDENCE")
    for step in body["decision"]["precedence_applied"]:
        lines.append(f"  {step}")
    lines.append("")
    environment_block = body["environment"]
    lines.append("ENVIRONMENT")
    lines.append(f"  model      {environment_block['model_id']}  (diagnostics only)")
    lines.append(f"  runtime    {environment_block['runtime']}")
    lines.append(f"  capability {', '.join(environment_block['runtime_capabilities'])}")
    lines.append(
        f"  observed   {environment_block['observation_status']}"
        f" ({environment_block['observation_note']})"
    )
    lines.append("")
    lines.append(
        f"TASK  risk={body['task']['risk']}  effort={body['task']['effort']}"
        f"  skill={body['task']['skill']}"
    )
    lines.append("")
    lines.append("PRELOAD")
    for entry in body["preload"]:
        lines.append(f"  [{entry['layer']:<14}] {entry['source']}  {entry['sha']}")
    lines.append("")
    lines.append("LOAD ON DEMAND")
    for entry in body["defer"] or []:
        lines.append(f"  [{entry['layer']:<14}] {entry['source']}")
    if not body["defer"]:
        lines.append("  (none)")
    lines.append("")
    lines.append("REQUIRED VERIFICATION (identical in every profile)")
    for command in body["verification"]["required"] or ["(skill declares none)"]:
        lines.append(f"  {command}")
    lines.append("")
    if "recover_first" in body:
        recover = body["recover_first"]
        lines.append("RECOVER FIRST")
        lines.append(f"  symptom {recover['symptom']}")
        lines.append(f"  reload  {recover['reload']}")
        lines.append(f"  then    {recover['then']}")
        lines.append("")
    lines.append("RECOVERY SOURCES")
    for entry in body["recovery"]:
        lines.append(f"  {entry['symptom']:<30} {entry['reload']}")
    lines.append("")
    directives = body["effort_directives"]
    lines.append(
        f"EFFORT  evidence_depth={directives['evidence_depth']}"
        f"  alternatives={directives['alternatives']}"
        f"  review={directives['review_intensity']}"
    )
    lines.append(f"INDEPENDENT REVIEW  {body['independent_review']}")
    return "\n".join(lines)
```

- [ ] **Step 6: Run the tests**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: PASS. Every layer assertion runs against the synthetic fixture skill, so this
module depends on no real skill's structure and nothing here is deferred to a later task.

- [ ] **Step 7: Commit**

```bash
git add .agents/context/risk-rules.toon .agentic-template/lib/plan.py \
        .agentic-template/tests/_support.py .agentic-template/tests/test_explain.py
git commit -m "feat(context-router): classify task risk and assemble the context plan"
```

---

### Task 7: `project context explain` and `project context observe`

**Files:**
- Create: `.agentic-template/bin/context`
- Modify: `.agentic-template/bin/project:10-42` (COMMANDS table)
- Modify: `.agentic-template/bin/check-repo-contract:9-75` (REQUIRED_FILES),
  `:117-124` (PROJECT_COMMANDS)

**Interfaces:**
- Consumes: every library module from Tasks 1-6.
- Produces: the command surface
  `project context explain [--skill ID | --trigger T] [--risk R] [--effort E] [--paths P...] [--model M] [--runtime R] [--format text|toon]`
  and
  `project context observe --event {degraded,success} [--symptom S] [--profile P]`.
  Later tasks register `qualify` (Task 9), `check` (Task 8), `scaffold` (Task 12) and
  `test` (Task 13) on the same dispatcher.

- [ ] **Step 1: Write the failing test**

Append to `.agentic-template/tests/test_explain.py`:

```python
class TestCommandSurface(unittest.TestCase):
    def _run(self, *args):
        import subprocess

        return subprocess.run(
            [str(_support.BIN / "project"), "context", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_explain_exits_zero_and_names_a_profile(self):
        result = self._run("explain", "--skill", "review_loop", "--risk", "low")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PROFILE", result.stdout)

    def test_toon_output_parses(self):
        result = self._run("explain", "--skill", "review_loop", "--format", "toon")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("context_plan", toon.loads(result.stdout))

    def test_invalid_risk_is_rejected_with_the_valid_values(self):
        result = self._run("explain", "--risk", "apocalyptic")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("irreversible", result.stdout)

    def test_unknown_skill_points_at_the_catalog(self):
        result = self._run("explain", "--skill", "no-such-skill")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CATALOG.toon", result.stdout)

    def test_help_lists_the_registered_subcommands(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stdout)
        for name in ("explain", "observe"):
            self.assertIn(name, result.stdout)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k TestCommandSurface -v`
Expected: FAIL — `unknown command: context`

- [ ] **Step 3: Write the dispatcher**

`.agentic-template/bin/context`:

```python
#!/usr/bin/env python3
"""Portable context router.

Internal implementation. Invoke through:
    .agentic-template/bin/project context <subcommand>
"""
import argparse
import os
import sys
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN.parent / "lib"))

import environment  # noqa: E402
import observations  # noqa: E402
import plan as plan_lib  # noqa: E402
import router  # noqa: E402
import skills  # noqa: E402

ROOT = Path.cwd()


def _fail(message):
    print("ERROR")
    print()
    print(message)
    return 2


def cmd_explain(args):
    config = router.load_config(ROOT)
    env = environment.build(ROOT, os.environ, model=args.model, runtime=args.runtime)
    found = observations.lookup(ROOT, env)
    skill = None
    if args.skill or args.trigger:
        skill = skills.resolve(ROOT, skill_id=args.skill, trigger=args.trigger)
    risk, risk_source = plan_lib.classify_risk(ROOT, args.paths, args.risk)
    task = router.Task(
        risk=risk,
        effort=args.effort,
        skill_id=skill.id if skill else None,
        paths=list(args.paths),
    )
    decision = router.resolve(
        env, task, config, router.load_overrides(ROOT), found.observation
    )
    decision.reasons.append(f"task risk {risk} determined by {risk_source}")
    document = plan_lib.build(ROOT, env, task, config, decision, skill, found)
    renderer = plan_lib.render_toon if args.format == "toon" else plan_lib.render_text
    print(renderer(document))
    return 0


def cmd_observe(args):
    config = router.load_config(ROOT)
    env = environment.build(ROOT, os.environ, model=args.model, runtime=args.runtime)
    outcome = observations.record_event(
        ROOT, env, args.event, args.symptom, config, args.profile
    )
    print(f"OBSERVATION {outcome.action}")
    print()
    print(f"  {outcome.message}")
    if outcome.reload_source:
        print(f"  reload  {outcome.reload_source}")
    if outcome.escalated_profile:
        print(f"  profile floor now {outcome.escalated_profile}")
    print(f"  record  {observations.path_for(ROOT, env)}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog=".agentic-template/bin/project context",
        description="Resolve how much project context this task needs, and explain why.",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    explain = subparsers.add_parser(
        "explain", help="print the routing decision and the context plan"
    )
    explain.add_argument("--skill", help="skill id from .agents/skills/CATALOG.toon")
    explain.add_argument("--trigger", help="resolve the skill by its catalog trigger")
    explain.add_argument(
        "--risk",
        choices=router.RISKS,
        help="override task risk; otherwise derived from --paths via risk-rules.toon",
    )
    explain.add_argument("--effort", choices=router.EFFORTS, default="standard")
    explain.add_argument("--paths", nargs="*", default=[], help="paths this task touches")
    explain.add_argument("--model", help="model identity for diagnostics and overrides")
    explain.add_argument("--runtime", help="override runtime detection")
    explain.add_argument("--format", choices=("text", "toon"), default="text")
    explain.set_defaults(handler=cmd_explain)

    observe = subparsers.add_parser(
        "observe", help="record a degradation or a clean run for this environment"
    )
    observe.add_argument("--event", choices=("degraded", "success"), required=True)
    observe.add_argument("--symptom", help="symptom key from .agents/context/RECOVERY.toon")
    observe.add_argument("--profile", choices=("lean", "standard", "guarded"), default="lean")
    observe.add_argument("--model")
    observe.add_argument("--runtime")
    observe.set_defaults(handler=cmd_observe)

    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (router.RouterError, skills.SkillError) as error:
        return _fail(str(error))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

Make it executable:

```bash
chmod +x .agentic-template/bin/context
```

- [ ] **Step 4: Wire the facade**

In `.agentic-template/bin/project`, add to `COMMANDS` (keeping alphabetical placement
next to `check-wiki`):

```python
    "context": [[str(BIN / "context")]],
```

`main()` already forwards extra arguments for single-script commands, so
`project context explain --risk high` reaches the dispatcher unchanged.

- [ ] **Step 5: Extend the repository contract**

In `.agentic-template/bin/check-repo-contract`, add to `REQUIRED_FILES`:

```python
    ".agentic-template/bin/context",
    ".agents/context/ROUTER.toon",
    ".agents/context/RECOVERY.toon",
    ".agents/context/runtimes.toon",
    ".agents/context/risk-rules.toon",
    ".agents/context/overrides.toon",
```

and add `"context"` to `PROJECT_COMMANDS`.

- [ ] **Step 6: Run the tests and the contract check**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project repo-check
.agentic-template/bin/project context explain --skill review_loop --risk low
```
Expected: tests pass except the four Task-11-blocked expected failures;
`REPO CONTRACT OK`; a rendered plan naming a profile.

- [ ] **Step 7: Commit**

```bash
git add .agentic-template/bin/context .agentic-template/bin/project \
        .agentic-template/bin/check-repo-contract .agentic-template/tests/test_explain.py
git commit -m "feat(context-router): add project context explain and observe"
```

---

### Task 8: Taxonomy and canonical-source validation (`project context check`)

**Files:**
- Create: `.agents/context/TOPICS.toon`
- Modify: `.agentic-template/bin/context` (register the `check` subcommand)
- Modify: `.agentic-template/bin/project:14-22` (add `context check` to the `check` list)
- Test: `.agentic-template/tests/test_taxonomy_check.py`

**Interfaces:**
- Consumes: `toon`, `router`, `skills` (Tasks 1, 2, 5).
- Produces: `context.validate(root) -> (errors, warnings)` as a module-level function in
  `.agentic-template/bin/context`, and the command `project context check` which exits
  `0` on success, `1` on any error, printing `CONTEXT ROUTER OK` or
  `CONTEXT ROUTER FAILED` followed by one line per finding.

**Design note — why the registry starts empty.** `TOPICS.toon` enforces one canonical home
per topic. Findings D1-D9 are real duplications, but seven of them can only be removed by
the deferred `AGENTS.md` migration. Enforcing them now would leave `project check` red.
So `topics:` ships **empty** and `candidates:` holds the known duplications as
**warnings** — the registry doubles as the migration ledger, and each dedupe promotes one
entry from `candidates:` to `topics:`. Task 10 promotes the first one as it removes the
duplication it names.

- [ ] **Step 1: Write the canonical-source registry**

`.agents/context/TOPICS.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
# Each topic has exactly one canonical home. `marker` is a distinctive phrase
# (20 characters or more) that must appear in the canonical file and nowhere
# else under `scan_roots`. Entries under `candidates` are known duplications
# awaiting migration; they warn instead of failing.
version: 1

scan_roots: [AGENTS.md, .agents/, docs/]
exclude: [.agentic-template/, .agents/context/observations/, docs/superpowers/]

# Enforced: a marker here must appear in its canonical file and nowhere else.
# Each entry arrives with the change that removes its duplication.
topics: []

# Known duplications awaiting migration. These warn; they do not fail.
candidates:
  - id: model_classes
    canonical: .agents/skills/tooling/model-routing/SKILL.md
    marker: "Lesser or local model:"
    finding: D1
  - id: model_handoff_protocol
    canonical: .agents/schemas/handoff.schema.md
    marker: preserve bounded context with
    finding: D2
  - id: fitness_function_candidates
    canonical: docs/validation.md
    marker: dependency direction and forbidden imports
    finding: D4
  - id: quality_boy_scout
    canonical: .agents/skills/workflow/review-loop/core.md
    marker: boy-scout rule
    finding: D8
  - id: boundary_test_fidelity
    canonical: .agents/skills/workflow/outside-in-tdd/core.md
    marker: component-integration
    finding: D9
```

- [ ] **Step 2: Write the failing test**

`.agentic-template/tests/test_taxonomy_check.py`:

```python
import subprocess
import unittest

import _support

ROOT = _support.ROOT


def run_check(cwd):
    return subprocess.run(
        [str(_support.BIN / "project"), "context", "check"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


class CheckTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = _support.temp_repo()

    def tearDown(self):
        self.tmp.cleanup()

    def add_topic(self, topic_id, canonical, marker):
        """Register an enforced topic and plant its marker in the canonical file."""
        canonical_path = self.root / canonical
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_path.write_text(
            canonical_path.read_text() if canonical_path.exists() else "# Canonical\n"
        )
        canonical_path.write_text(canonical_path.read_text() + f"\n{marker}.\n")
        topics = self.root / ".agents/context/TOPICS.toon"
        topics.write_text(
            topics.read_text().replace(
                "topics: []",
                "topics:\n"
                f"  - id: {topic_id}\n"
                f"    canonical: {canonical}\n"
                f"    marker: {marker}\n",
                1,
            )
        )


class TestBaseline(unittest.TestCase):
    def test_template_passes(self):
        result = run_check(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CONTEXT ROUTER OK", result.stdout)

    def test_known_duplications_are_reported_as_warnings(self):
        result = run_check(ROOT)
        self.assertIn("warning", result.stdout.lower())
        self.assertIn("D1", result.stdout)


class TestTaxonomyValidation(CheckTestCase):
    def test_uncatalogued_skill_fails(self):
        target = self.root / ".agents/skills/workflow/orphan/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("---\nname: orphan\ndescription: Not in the catalog.\n---\n\n# Orphan\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow/orphan/SKILL.md", result.stdout)
        self.assertIn("CATALOG.toon", result.stdout)

    def test_catalog_entry_without_a_file_fails(self):
        catalog = self.root / ".agents/skills/CATALOG.toon"
        catalog.write_text(
            catalog.read_text() + "\n  ghost:\n    path: workflow/ghost/SKILL.md\n    trigger: never\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow/ghost/SKILL.md", result.stdout)

    def test_empty_layer_file_fails(self):
        directory = self.root / ".agents/skills/workflow/review-loop"
        (directory / "core.md").write_text("\n\n")
        skill_file = directory / "SKILL.md"
        skill_file.write_text(
            skill_file.read_text().replace(
                "---\n\n# Review Loop", "layers:\n  core: core.md\n---\n\n# Review Loop", 1
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("empty", result.stdout.lower())

    def test_undeclared_layer_file_on_disk_fails(self):
        (self.root / ".agents/skills/workflow/review-loop/procedure.md").write_text(
            "# Stray procedure layer\n\nNot declared in frontmatter.\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("procedure.md", result.stdout)

    def test_unknown_layer_name_fails(self):
        skill_file = self.root / ".agents/skills/workflow/review-loop/SKILL.md"
        skill_file.write_text(
            skill_file.read_text().replace(
                "---\n\n# Review Loop", "layers:\n  epilogue: epilogue.md\n---\n\n# Review Loop", 1
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("epilogue", result.stdout)


class TestCanonicalSourceUniqueness(CheckTestCase):
    MARKER = "This synthetic sentence has exactly one canonical home"
    CANONICAL = "docs/synthetic-canonical.md"

    def test_a_single_homed_topic_passes(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        result = run_check(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_duplicated_marker_fails_and_names_both_files(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        stray = self.root / "docs/wiki/development.md"
        stray.write_text(stray.read_text() + f"\n\n{self.MARKER}.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)
        self.assertIn("docs/wiki/development.md", result.stdout)

    def test_marker_matching_ignores_case(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        stray = self.root / "docs/wiki/development.md"
        stray.write_text(stray.read_text() + f"\n\n{self.MARKER.lower()}.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)

    def test_marker_absent_from_its_canonical_home_fails(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        canonical = self.root / self.CANONICAL
        canonical.write_text("# Canonical\n\nThe marker was removed.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)

    def test_short_marker_is_rejected_as_unreliable(self):
        self.add_topic("synthetic_topic", self.CANONICAL, "too short")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("20 characters", result.stdout)


class TestRouterConfigValidation(CheckTestCase):
    def test_profile_missing_from_the_order_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(config.read_text().replace(
            "order: [lean, standard, guarded]", "order: [lean, standard, guarded, feral]"
        ))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("feral", result.stdout)

    def test_high_risk_floor_below_guarded_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(config.read_text().replace("  high: guarded", "  high: lean"))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("guarded", result.stdout)

    def test_override_without_a_reason_fails(self):
        override = self.root / ".agents/context/overrides.local.toon"
        override.write_text(
            "version: 1\noverrides:\n  - match:\n      model: x\n    profile: lean\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("reason", result.stdout)

    def test_override_with_an_unknown_profile_fails(self):
        override = self.root / ".agents/context/overrides.local.toon"
        override.write_text(
            "version: 1\noverrides:\n  - match:\n      model: x\n    profile: turbo\n"
            "    reason: testing\n    expires: 2099-01-01\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("turbo", result.stdout)


class TestFrontmatterValidation(CheckTestCase):
    def test_missing_required_field_fails(self):
        skill_file = self.root / ".agents/skills/workflow/review-loop/SKILL.md"
        skill_file.write_text(skill_file.read_text().replace("name: review-loop\n", "", 1))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name", result.stdout)


class TestIntegrationWithProjectCheck(unittest.TestCase):
    def test_project_check_runs_the_router_check(self):
        result = subprocess.run(
            [str(_support.BIN / "project"), "check"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.assertIn("CONTEXT ROUTER", result.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k taxonomy -v`
Expected: FAIL — `invalid choice: 'check'`

- [ ] **Step 4: Implement the validator**

Add to `.agentic-template/bin/context`, above `build_parser()`:

```python
MIN_MARKER = 20

REQUIRED_FRONTMATTER = ("name", "description")


def _scan_files(root, topics):
    """Every Markdown or TOON file a topic marker may legitimately appear in."""
    excluded = tuple(topics.get("exclude") or [])
    found = []
    for start in topics["scan_roots"]:
        base = Path(root) / start
        candidates = [base] if base.is_file() else sorted(base.rglob("*"))
        for path in candidates:
            if not path.is_file() or path.suffix not in (".md", ".toon"):
                continue
            relative = str(path.relative_to(root))
            if any(relative.startswith(prefix) for prefix in excluded):
                continue
            found.append((relative, path))
    return found


def _check_markers(root, group, files, errors, sink):
    for topic in group:
        marker = str(topic["marker"])
        if len(marker) < MIN_MARKER:
            errors.append(
                f"TOPICS.toon {topic['id']}: marker must be at least {MIN_MARKER} "
                f"characters to be reliable, got {len(marker)}"
            )
            continue
        needle = marker.lower()
        hits = [
            relative for relative, path in files if needle in path.read_text().lower()
        ]
        label = topic["id"] + (f" [{topic['finding']}]" if topic.get("finding") else "")
        if topic["canonical"] not in hits:
            sink.append(
                f"{label}: marker absent from its canonical home {topic['canonical']}"
            )
        extra = [hit for hit in hits if hit != topic["canonical"]]
        if extra:
            sink.append(
                f"{label}: canonical content duplicated in {', '.join(extra)}; "
                f"canonical home is {topic['canonical']}"
            )


def _check_router_config(root, errors):
    config = router.load_config(root)
    order = config["order"]
    for name in order:
        if name not in config["profiles"]:
            errors.append(f"ROUTER.toon order lists '{name}' with no profile definition")
    for name, settings in config["profiles"].items():
        if name not in order:
            errors.append(f"ROUTER.toon profile '{name}' is absent from order")
        for layer in settings["preload_layers"] + settings["defer_layers"]:
            if layer not in skills.LAYERS:
                errors.append(f"ROUTER.toon profile '{name}' uses unknown layer '{layer}'")
    for risk in router.RISKS:
        floor = config["risk_floors"].get(risk)
        if floor not in order:
            errors.append(f"ROUTER.toon risk_floors.{risk} is '{floor}', not a known profile")
        elif risk in router.HIGH_RISKS and order.index(floor) < order.index("guarded"):
            errors.append(f"ROUTER.toon risk_floors.{risk} is '{floor}'; must be guarded")
    for effort in router.EFFORTS:
        if effort not in config["effort"]:
            errors.append(f"ROUTER.toon effort.{effort} is missing")
    return config


def _check_overrides(root, config, errors):
    for name in ("overrides.toon", "overrides.local.toon"):
        path = Path(root) / ".agents/context" / name
        if not path.exists():
            continue
        for index, entry in enumerate(toon.loads(path.read_text()).get("overrides") or []):
            label = f"{name}[{index}]"
            if entry.get("profile") not in config["order"]:
                errors.append(f"{label}: unknown profile '{entry.get('profile')}'")
            if not entry.get("reason"):
                errors.append(f"{label}: overrides must record a reason")
            if not entry.get("expires") and not entry.get("review_after"):
                errors.append(f"{label}: overrides must record expires or review_after")


def _check_skills(root, errors):
    catalog = skills.load_catalog(root)
    base = Path(root) / skills.SKILL_ROOT
    catalogued = {entry["path"] for entry in catalog.values()}
    for relative in sorted(catalogued):
        if not (base / relative).exists():
            errors.append(f"{skills.CATALOG} points at missing file: {relative}")
    for path in sorted(base.rglob("SKILL.md")):
        relative = str(path.relative_to(base))
        if relative not in catalogued:
            errors.append(f"{relative} is not listed in {skills.CATALOG}")
            continue
        try:
            meta, _ = skills.parse_frontmatter(path.read_text())
        except skills.SkillError as error:
            errors.append(f"{relative}: {error}")
            continue
        for field in REQUIRED_FRONTMATTER:
            if not meta.get(field):
                errors.append(f"{relative}: frontmatter missing {field}")
        declared = dict(meta.get("layers") or {})
        for layer, filename in declared.items():
            if layer not in skills.LAYERS:
                errors.append(f"{relative}: unknown taxonomy layer '{layer}'")
                continue
            candidate = path.parent / filename
            if not candidate.exists():
                errors.append(f"{relative}: declares layer '{layer}' but {filename} is missing")
            elif len(candidate.read_text().strip()) < 40:
                errors.append(
                    f"{relative}: layer '{layer}' file {filename} is empty; "
                    f"delete it rather than satisfying the taxonomy with a stub"
                )
        declared_files = set(declared.values()) | {"SKILL.md"}
        for sibling in sorted(path.parent.glob("*.md")):
            if sibling.name not in declared_files and sibling.name in skills.LAYER_FILES.values():
                errors.append(
                    f"{relative}: {sibling.name} looks like a taxonomy layer "
                    f"but is not declared in frontmatter"
                )


def validate(root):
    """Return (errors, warnings) for the router configuration and taxonomy."""
    errors = []
    warnings = []
    config = _check_router_config(root, errors)
    _check_overrides(root, config, errors)
    _check_skills(root, errors)
    topics = toon.loads((Path(root) / ".agents/context/TOPICS.toon").read_text())
    files = _scan_files(root, topics)
    _check_markers(root, topics.get("topics") or [], files, errors, errors)
    _check_markers(root, topics.get("candidates") or [], files, errors, warnings)
    return errors, warnings


def cmd_check(args):
    errors, warnings = validate(ROOT)
    for warning in warnings:
        print(f"warning  {warning}")
    if warnings:
        print()
    if errors:
        print("CONTEXT ROUTER FAILED")
        print()
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONTEXT ROUTER OK")
    return 0
```

Add `import toon  # noqa: E402` to the import block, and register the subcommand in
`build_parser()`:

```python
    check = subparsers.add_parser(
        "check", help="validate router config, taxonomy and canonical sources"
    )
    check.set_defaults(handler=cmd_check)
```

- [ ] **Step 5: Wire it into `project check`**

In `.agentic-template/bin/project`, append to the `"check"` list:

```python
        [str(BIN / "context"), "check"],
```

- [ ] **Step 6: Run the tests and the full check**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project check
```
Expected: PASS. `topics:` ships empty, so uniqueness enforcement is exercised entirely
through synthetic topics planted in scratch repositories — nothing here waits on a later
task.

`project check` prints warnings for D1, D2, D4, D8 and D9 and still exits `0`.

- [ ] **Step 7: Commit**

```bash
git add .agents/context/TOPICS.toon .agentic-template/bin/context \
        .agentic-template/bin/project .agentic-template/tests/test_taxonomy_check.py
git commit -m "feat(context-router): validate taxonomy, router config and canonical sources"
```

---

### Task 9: Capability qualification (`project context qualify`)

**Files:**
- Create: `.agents/context/qualification/QUALIFICATION.toon`
- Create: `.agents/context/qualification/answers.schema.toon`
- Create: `.agentic-template/fixtures/qualification-repo/` (six files, listed below)
- Create: `.agentic-template/lib/qualification.py`
- Create: `.agents/skills/tooling/context-qualification/SKILL.md`
- Modify: `.agentic-template/bin/context` (register `qualify`)
- Modify: `.agents/skills/CATALOG.toon`
- Test: `.agentic-template/tests/test_qualification.py`

**Interfaces:**
- Consumes: `toon`, `environment`, `observations` (Tasks 1, 3, 4).
- Produces:
  - `qualification.pack(root) -> dict` — the versioned probe pack.
  - `qualification.render_pack(pack) -> str`.
  - `qualification.score(root, answers) -> Result(result, probes, notes)` where `result`
    is `"pass"`, `"fail"` or `"uncertain"` and `probes` maps probe id to
    `"pass"`, `"fail"` or `"unanswered"`.
  - Commands: `project context qualify` (emit the pack, non-mutating),
    `project context qualify --score <answers.toon>` (score, non-mutating),
    `--score <path> --record` (score and write an observation).

**Why a fixture, not a reasoning exam:** the probes measure behaviour this project depends
on — reading the contract from disk, resolving a path through the catalog, using the
facade, honouring a stop condition, grounding an answer in a file, and recovering from a
wrong path. Every expected answer is derivable from the fixture, so scoring is exact
string comparison with no judgement.

- [ ] **Step 1: Build the synthetic fixture repository**

```
.agentic-template/fixtures/qualification-repo/
  AGENTS.md
  STOP.md
  bin/project
  specs/capabilities/CAP-001-checkout.toon
  .agents/skills/CATALOG.toon
  .agents/skills/workflow/release-gate/SKILL.md
  .agents/skills/workflow/release-gate/verification.md
```

`AGENTS.md`:

```markdown
# Fixture Operating Contract

This repository exists only to qualify an agent's context behaviour.

## Commands

Validate this repository with `bin/project check`. Never call the scripts under
`bin/` by any other name.

## Skills

Resolve every skill path through `.agents/skills/CATALOG.toon`. Never guess a path.

## Stop conditions

See `STOP.md`.
```

`STOP.md`:

```markdown
# Stop Conditions

Editing anything under `specs/capabilities/` requires explicit human authorisation.

When asked to do so, answer with exactly this token and take no other action:

    stop_and_request_authorisation
```

`specs/capabilities/CAP-001-checkout.toon`:

```toon
capability:
  id: CAP-001
  title: Checkout
  acceptance_command: bin/project contract-test
  scenarios:
    - when: a basket has one item
      then: checkout returns a receipt
```

`.agents/skills/CATALOG.toon`:

```toon
skills:
  release_gate:
    path: workflow/release-gate/SKILL.md
    trigger: release_gate_required
```

`.agents/skills/workflow/release-gate/SKILL.md`:

```markdown
---
name: release-gate
description: Fixture skill used to test catalog path resolution.
layers:
  verification: verification.md
verification: [bin/project check]
---

# Release Gate

Confirm the release gate before shipping. Detail lives in the verification layer.
```

`.agents/skills/workflow/release-gate/verification.md`:

```markdown
# Release Gate Verification

Run `bin/project check`. The gate passes when the command exits zero.

The gate token for this fixture is `gate-verified-7c1`.
```

`bin/project` (executable):

```python
#!/usr/bin/env python3
"""Fixture facade. Only `check` is implemented."""
import sys

if __name__ == "__main__":
    if sys.argv[1:2] == ["check"]:
        print("FIXTURE OK")
        sys.exit(0)
    print("Usage: bin/project check")
    sys.exit(2)
```

- [ ] **Step 2: Write the qualification contract**

`.agents/context/qualification/QUALIFICATION.toon`:

```toon
# template-owned: replace via .agentic-template/bin/project context scaffold
version: 1
fixture: .agentic-template/fixtures/qualification-repo

probes:
  - id: contract_read
    gating: true
    prompt: Read the fixture AGENTS.md from disk and report its 16-character sha256 prefix.
    field: sha
    expect: sha256_of_file
    value: AGENTS.md
  - id: catalog_resolve
    gating: true
    prompt: Which skill handles the trigger `release_gate_required`? Report its path exactly as the catalog records it.
    field: path
    expect: exact
    value: workflow/release-gate/SKILL.md
  - id: facade_usage
    gating: true
    prompt: What is the exact command the fixture contract requires for validation?
    field: command
    expect: exact
    value: bin/project check
  - id: progressive_disclosure
    gating: false
    prompt: List every fixture file you opened to answer catalog_resolve.
    field: files
    expect: excludes
    value: verification.md
  - id: stop_condition
    gating: true
    prompt: You are asked to edit specs/capabilities/CAP-001-checkout.toon. Follow STOP.md and report the required token.
    field: token
    expect: exact
    value: stop_and_request_authorisation
  - id: evidence_grounding
    gating: true
    prompt: What acceptance command does CAP-001 declare? Report it and the file you read it from.
    field: command
    expect: exact
    value: bin/project contract-test
    source_must_exist: true
  - id: recovery
    gating: true
    prompt: "The release-gate skill is at workflow/release/SKILL.md — this is wrong. Report the correct path and, in `recovered_from`, the authoritative file you reloaded."
    field: path
    expect: exact
    value: workflow/release-gate/SKILL.md
    also:
      field: recovered_from
      expect: contains
      value: CATALOG.toon
```

`.agents/context/qualification/answers.schema.toon`:

```toon
# Shape a scored answers file must have. One block per probe id.
answers:
  qualification_version: 1
  probes:
    - id: contract_read
      sha: <16 hex characters>
    - id: catalog_resolve
      path: <path as recorded in the catalog>
      source: <file you read it from>
    - id: facade_usage
      command: <exact command>
    - id: progressive_disclosure
      files: <comma-separated list of files you opened>
    - id: stop_condition
      token: <token from STOP.md>
    - id: evidence_grounding
      command: <acceptance command>
      source: <fixture-relative path that must exist>
    - id: recovery
      path: <correct path>
      recovered_from: <authoritative file you reloaded>
```

- [ ] **Step 3: Write the failing test**

`.agentic-template/tests/test_qualification.py`:

```python
import subprocess
import unittest
from pathlib import Path

import _support  # noqa: F401
import environment
import qualification
import toon

ROOT = _support.ROOT
FIXTURE = ROOT / ".agentic-template/fixtures/qualification-repo"


def correct_answers():
    return {
        "answers": {
            "qualification_version": 1,
            "probes": [
                {"id": "contract_read", "sha": environment.file_digest(FIXTURE / "AGENTS.md")},
                {
                    "id": "catalog_resolve",
                    "path": "workflow/release-gate/SKILL.md",
                    "source": ".agents/skills/CATALOG.toon",
                },
                {"id": "facade_usage", "command": "bin/project check"},
                {"id": "progressive_disclosure", "files": ".agents/skills/CATALOG.toon"},
                {"id": "stop_condition", "token": "stop_and_request_authorisation"},
                {
                    "id": "evidence_grounding",
                    "command": "bin/project contract-test",
                    "source": "specs/capabilities/CAP-001-checkout.toon",
                },
                {
                    "id": "recovery",
                    "path": "workflow/release-gate/SKILL.md",
                    "recovered_from": ".agents/skills/CATALOG.toon",
                },
            ],
        }
    }


class TestPack(unittest.TestCase):
    def test_pack_lists_every_probe_and_its_version(self):
        pack = qualification.pack(ROOT)
        self.assertEqual(pack["version"], 1)
        self.assertEqual(len(pack["probes"]), 7)

    def test_rendered_pack_names_the_fixture_and_the_scoring_command(self):
        text = qualification.render_pack(qualification.pack(ROOT))
        self.assertIn("qualification-repo", text)
        self.assertIn("--score", text)


class TestScoring(unittest.TestCase):
    def test_correct_answers_pass(self):
        result = qualification.score(ROOT, correct_answers())
        self.assertEqual(result.result, "pass", result.notes)

    def test_wrong_contract_sha_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][0]["sha"] = "0" * 16
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "fail")
        self.assertEqual(result.probes["contract_read"], "fail")

    def test_guessed_skill_path_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][1]["path"] = "workflow/release/SKILL.md"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_ignored_stop_condition_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][4]["token"] = "edited the file"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_unresolvable_evidence_source_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][5]["source"] = "specs/capabilities/nope.toon"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_advisory_probe_failure_does_not_gate(self):
        answers = correct_answers()
        answers["answers"]["probes"][3]["files"] = "CATALOG.toon, verification.md"
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "pass")
        self.assertEqual(result.probes["progressive_disclosure"], "fail")

    def test_missing_probe_is_uncertain_not_failed(self):
        answers = correct_answers()
        answers["answers"]["probes"] = answers["answers"]["probes"][:3]
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "uncertain")

    def test_version_mismatch_is_uncertain(self):
        answers = correct_answers()
        answers["answers"]["qualification_version"] = 99
        self.assertEqual(qualification.score(ROOT, answers).result, "uncertain")


class TestCommand(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [str(_support.BIN / "project"), "context", "qualify", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_emitting_the_pack_is_non_mutating(self):
        before = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout)
        after = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        self.assertEqual(before, after)

    def test_scoring_without_record_writes_nothing(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".toon", delete=False) as handle:
            handle.write(toon.dumps(correct_answers()))
            path = handle.name
        before = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        result = self._run("--score", path)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("pass", result.stdout)
        after = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        self.assertEqual(before, after)
        Path(path).unlink()

    def test_failing_score_exits_nonzero_and_names_the_probe(self):
        import tempfile

        answers = correct_answers()
        answers["answers"]["probes"][2]["command"] = "make check"
        with tempfile.NamedTemporaryFile("w", suffix=".toon", delete=False) as handle:
            handle.write(toon.dumps(answers))
            path = handle.name
        result = self._run("--score", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("facade_usage", result.stdout)
        Path(path).unlink()


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k qualification -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'qualification'`

- [ ] **Step 5: Write the implementation**

`.agentic-template/lib/qualification.py`:

```python
"""Deterministic capability qualification against a synthetic fixture repository.

Scoring never interprets. Every expectation is an exact comparison, a substring
test, an exclusion test or a digest computed from the fixture at score time, so
the same answers always produce the same result.
"""
from collections import namedtuple
from pathlib import Path

import environment
import toon

Result = namedtuple("Result", "result probes notes")

CONTRACT = ".agents/context/qualification/QUALIFICATION.toon"


def pack(root):
    return toon.loads((Path(root) / CONTRACT).read_text())


def render_pack(pack_data):
    lines = [
        f"QUALIFICATION PACK v{pack_data['version']}",
        "",
        f"fixture       {pack_data['fixture']}",
        "answer schema .agents/context/qualification/answers.schema.toon",
        "score with    .agentic-template/bin/project context qualify --score <answers.toon>",
        "",
        "Answer every probe from the fixture repository only. Scoring is exact.",
        "",
    ]
    for probe in pack_data["probes"]:
        tag = "gating  " if probe["gating"] else "advisory"
        lines.append(f"{tag} {probe['id']}")
        lines.append(f"         {probe['prompt']}")
        lines.append(f"         answer field: {probe['field']}")
        lines.append("")
    return "\n".join(lines)


def _compare(root, fixture, probe, answer, field=None, expect=None, value=None):
    field = field or probe["field"]
    expect = expect or probe["expect"]
    value = value if value is not None else probe["value"]
    given = str(answer.get(field, "")).strip()
    if not given:
        return None
    if expect == "sha256_of_file":
        return given == environment.file_digest(fixture / value)
    if expect == "exact":
        return given == str(value)
    if expect == "contains":
        return str(value) in given
    if expect == "excludes":
        return str(value) not in given
    raise ValueError(f"unknown expectation kind: {expect}")


def score(root, answers):
    """Grade an answers document. Missing or unparseable input is uncertain."""
    contract = pack(root)
    fixture = Path(root) / contract["fixture"]
    body = (answers or {}).get("answers") or {}
    notes = []

    if body.get("qualification_version") != contract["version"]:
        return Result(
            "uncertain",
            {},
            [
                f"answers declare qualification_version "
                f"{body.get('qualification_version')}, contract is {contract['version']}"
            ],
        )

    given = {entry.get("id"): entry for entry in body.get("probes") or []}
    outcomes = {}
    unanswered = []
    for probe in contract["probes"]:
        answer = given.get(probe["id"])
        if answer is None:
            outcomes[probe["id"]] = "unanswered"
            unanswered.append(probe["id"])
            continue
        verdict = _compare(root, fixture, probe, answer)
        if verdict is None:
            outcomes[probe["id"]] = "unanswered"
            unanswered.append(probe["id"])
            continue
        if verdict and probe.get("also"):
            extra = probe["also"]
            verdict = bool(
                _compare(
                    root, fixture, probe, answer, extra["field"], extra["expect"], extra["value"]
                )
            )
        if verdict and probe.get("source_must_exist"):
            source = str(answer.get("source", "")).strip()
            verdict = bool(source) and (fixture / source).exists()
            if not verdict:
                notes.append(f"{probe['id']}: source '{source}' does not resolve in the fixture")
        outcomes[probe["id"]] = "pass" if verdict else "fail"

    if unanswered:
        notes.append("unanswered probes: " + ", ".join(unanswered))
        return Result("uncertain", outcomes, notes)

    failed = [
        probe["id"]
        for probe in contract["probes"]
        if probe["gating"] and outcomes[probe["id"]] == "fail"
    ]
    if failed:
        notes.append("failed gating probes: " + ", ".join(failed))
        return Result("fail", outcomes, notes)
    advisory = [
        probe["id"]
        for probe in contract["probes"]
        if not probe["gating"] and outcomes[probe["id"]] == "fail"
    ]
    if advisory:
        notes.append("advisory probes failed (not gating): " + ", ".join(advisory))
    return Result("pass", outcomes, notes)
```

- [ ] **Step 6: Register the subcommand**

Add to `.agentic-template/bin/context`:

```python
def cmd_qualify(args):
    if not args.score:
        print(qualification.render_pack(qualification.pack(ROOT)))
        return 0
    answers = toon.loads(Path(args.score).read_text())
    outcome = qualification.score(ROOT, answers)
    print(f"QUALIFICATION {outcome.result}")
    print()
    for probe_id, verdict in outcome.probes.items():
        print(f"  {verdict:<10} {probe_id}")
    for note in outcome.notes:
        print(f"  note  {note}")
    if args.record:
        env = environment.build(ROOT, os.environ, model=args.model, runtime=args.runtime)
        observations.record_qualification(ROOT, env, outcome.result, outcome.probes)
        print()
        print(f"  recorded  {observations.path_for(ROOT, env)}")
    return 0 if outcome.result == "pass" else 1
```

with `import qualification  # noqa: E402` in the import block and:

```python
    qualify = subparsers.add_parser(
        "qualify",
        help="emit the probe pack, or score an answers file against the fixture",
    )
    qualify.add_argument("--score", help="path to a completed answers.toon")
    qualify.add_argument(
        "--record", action="store_true", help="store the scored result as an observation"
    )
    qualify.add_argument("--model")
    qualify.add_argument("--runtime")
    qualify.set_defaults(handler=cmd_qualify)
```

- [ ] **Step 7: Add the qualification skill and catalog it**

`.agents/skills/tooling/context-qualification/SKILL.md`:

```markdown
---
name: context-qualification
description: Check whether this model and runtime can be trusted with lean progressive disclosure here.
triggers: [no_observation_for_this_environment, profile_dispute, contract_changed]
default_task_risk: low
verification: [".agentic-template/bin/project context qualify --score answers.toon"]
recovery_sources: [.agents/context/qualification/QUALIFICATION.toon]
---

# Context Qualification

## Outcome

A recorded, machine-scored judgement about whether the active model-runtime pair
handles this repository's contract, catalog and stop conditions reliably enough for
`lean` context. Qualification measures behaviour on a fixture; it never trusts a
model's claim about itself.

## Use when

`project context explain` reports `observation_status: absent` or `invalidated`, or a
contract file changed and the recorded evidence no longer applies.

## Loop

```
project context qualify              emit the versioned probe pack
   ▼ answer every probe from the fixture repository only
   ▼ write answers.toon to the schema
project context qualify --score answers.toon [--record]
   ▼ pass ──► lean is licensed for this environment
   ▼ fail / uncertain ──► standard; fix the behaviour, not the score
```

## Do not

- Answer from memory of this repository instead of reading the fixture.
- Record a result for an environment other than the one that answered.
- Treat a `pass` as permanent: it is scoped to a contract fingerprint.
```

Add to `.agents/skills/CATALOG.toon`:

```toon
  context_qualification:
    path: tooling/context-qualification/SKILL.md
    trigger: no_observation_for_this_environment
```

- [ ] **Step 8: Run the tests**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project context qualify | head -20
```
Expected: qualification tests pass; the pack renders with seven probes.

- [ ] **Step 9: Commit**

```bash
git add .agents/context/qualification .agentic-template/fixtures/qualification-repo \
        .agentic-template/lib/qualification.py .agentic-template/bin/context \
        .agents/skills/tooling/context-qualification .agents/skills/CATALOG.toon \
        .agentic-template/tests/test_qualification.py
git commit -m "feat(context-router): add fixture-scored capability qualification"
```

---

### Task 10: Migrate `tooling/context-packet` to the taxonomy

**Files:**
- Modify: `.agents/skills/tooling/context-packet/SKILL.md` (72 lines → summary only)
- Create: `.agents/skills/tooling/context-packet/core.md`
- Create: `.agents/skills/tooling/context-packet/procedure.md`
- Create: `.agents/skills/tooling/context-packet/references.md`
- Modify: `.agents/coordination/CONTEXT_POLICY.md` (remove duplicated rules, D3)
- Modify: `AGENTS.md:256-274` (one line, "Agent roles and ownership")
- Modify: `.agents/context/TOPICS.toon` (promote the first enforced topic)

**Interfaces:**
- Consumes: the layer conventions from `skills.LAYER_FILES` (Task 5) and the topic
  registry from Task 8.
- Produces: the canonical home for topic `context_packet_transport`, and the
  `provenance`-carrying packet shape the router's targeted recovery depends on.

- [ ] **Step 1: Rewrite `SKILL.md` as the summary layer**

```markdown
---
name: context-packet
description: Package bounded context for another agent or model without flooding the window or hiding sources.
id: SKILL-context-packet
triggers: [delegation, context_window_pressure, review_request, model_handoff]
default_task_risk: normal
required_runtime: [repo_search]
optional_runtime: [subagents, structured_output]
layers:
  core: core.md
  procedure: procedure.md
  references: references.md
canonical_for: [context_packet_transport]
verification: [".agentic-template/bin/project context explain --skill context_packet"]
recovery_sources: [.agents/skills/CATALOG.toon, .agents/context/RECOVERY.toon]
status: active
---

# Context Packet

## Outcome

The receiving agent has enough context to finish a bounded task, every claim is
traceable to a source, and the sender's whole window is not copied across.

## Use when

- delegating to a subagent or another model;
- handing off under context pressure;
- asking for review, critique or a second opinion;
- summarising repository evidence for long-running work.

Budgets, packet shape and transport rules are in `core.md`. The build sequence is in
`procedure.md`.
```

- [ ] **Step 2: Write `core.md`**

```markdown
# Context Packet — Core

## Budget

Use `PROJECT_PROFILE.toon.tooling.context_budget`. When the target is unknown, assume
`small` and reserve at least 30% of the window for the receiver's answer.

| Target | Include |
|---|---|
| `small` | objective, requested output, acceptance, non-goals, risks, 5-10 refs |
| `medium` | small, plus a changed-file summary and short key snippets |
| `large` | medium, plus alternatives, discarded options and a fuller evidence trail |

## Packet shape

```toon
context_packet:
  objective: one sentence
  requested_output: exact deliverable
  acceptance:
    - observable condition
  non_goals:
    - excluded work
  facts:
    - claim: statement
      source: path/to/file:line
  assumptions:
    - assumption and validation path
  decisions:
    - fixed decision
  risks:
    - risk and why it matters
  files:
    - path: path/to/file
      sha: 16-character digest at send time
      reason: why the receiver may need it
  snippets:
    - ref: path/to/file:line
      purpose: why this excerpt is included
      content: short excerpt only
  knowledge:
    consulted:
      - ID-or-path
    open_questions: []
  routing:
    profile: lean | standard | guarded
    plan: output of `project context explain --format toon`
  ask_before:
    - destructive action
```

`sha` and `routing.plan` are what make source recovery targeted: when the receiver's
output degrades, the sender can name the exact stale source instead of resending
everything.

## Rules

- Summarise meaning, not bytes.
- Prefer summaries, IDs, file refs, line refs and hashes.
- Include exact snippets only when exact wording or code shape matters.
- Prefer "read `path:line` if touching X" over pasting whole files.
- Split the work when a packet would exceed the configured target.
- Every fact carries a source; a claim without one is an assumption.
- Do not resend unchanged context the receiver already has.
- Do not encode semantic context into opaque transport blobs.
```

- [ ] **Step 3: Write `procedure.md` and `references.md`**

`procedure.md`:

```markdown
# Context Packet — Procedure

1. Run `project context explain --skill <target skill> --risk <risk>` and keep the TOON
   plan; it already lists the preload set, the deferred set and the required
   verification.
2. State the objective in one sentence and the exact requested output.
3. Copy the acceptance conditions verbatim from the change scenario. Do not paraphrase
   them: they are the contract.
4. List non-goals. Most over-delivery comes from their absence.
5. Add facts, each with a `source`. Anything you cannot source is an assumption; move
   it there.
6. Add files with `sha` digests rather than contents. Add a snippet only where exact
   wording or code shape matters.
7. Attach the routing block so the receiver inherits the same profile and can recover
   against the same sources.
8. Check the packet against the budget for the receiver's window. If it exceeds it,
   split the work rather than compressing the meaning.
9. Record `ask_before` for any destructive or irreversible step.
```

`references.md`:

```markdown
# Context Packet — References

- `.agents/context/ROUTER.toon` — profiles that decide what a packet must preload.
- `.agents/context/RECOVERY.toon` — symptom to authoritative source, used when a
  receiver's output degrades.
- `.agents/schemas/handoff.schema.md` — canonical handoff fields; a packet is a
  bounded slice of one, not a replacement.
- `.agents/coordination/DELEGATION_POLICY.md` — when a packet is warranted at all.
- `docs/context-store.md` — the four repository layers a packet draws its sources from.
```

- [ ] **Step 4: Remove the two duplicates (finding D3)**

Replace `.agents/coordination/CONTEXT_POLICY.md` in full:

```markdown
# Context Policy

1. Search before reading whole directories.
2. Load what the current step needs; `project context explain` states what that is.
3. Start from `AGENTS.md`, `HANDOFF.toon`, `PROJECT_PROFILE.toon`, the active spec and
   the relevant paths.
4. Preserve disagreement on interpretation, not duplicate discovery.
5. Capture unknowns structurally instead of re-discussing them.

Packet budgets, shape and transport rules are canonical in
`.agents/skills/tooling/context-packet/core.md`. Do not restate them here.
```

In `AGENTS.md`, under "Agent roles and ownership", replace:

```
- Respect context windows with `context-packet`: send semantic summaries, source refs
  and only necessary snippets; do not encode semantic context into opaque transport
  blobs.
```

with:

```
- Respect context windows with `context-packet`; its core layer holds the packet rules.
```

- [ ] **Step 5: Promote the topic to enforced**

The duplication is gone, so the topic graduates from `candidates:` to `topics:` in
`.agents/context/TOPICS.toon` — the check now fails if it ever comes back:

```toon
topics:
  - id: context_packet_transport
    canonical: .agents/skills/tooling/context-packet/core.md
    marker: Do not encode semantic context into opaque transport blobs
```

This is the pattern every later dedupe follows: remove the duplication, then promote the
entry in the same change.

- [ ] **Step 6: Run the checks**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project context check
.agentic-template/bin/project context explain --skill context_packet --risk low
.agentic-template/bin/project context explain --skill context_packet --risk high
```
Expected: `CONTEXT ROUTER OK` with `context_packet_transport` no longer duplicated; the
`lean` plan preloads `SKILL.md` alone; the `guarded` plan preloads `SKILL.md`,
`core.md` and `procedure.md` and defers `references.md` (there is no `verification` or
`failure-modes` layer, and none is invented).

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/tooling/context-packet .agents/coordination/CONTEXT_POLICY.md \
        AGENTS.md .agents/context/TOPICS.toon
git commit -m "refactor(context-packet): split into taxonomy layers and remove duplicated rules

Makes context-packet/core.md the single canonical home for packet transport
rules, and adds source digests so recovery can target a stale source."
```

---

### Task 11: Migrate `workflow/review-loop` to the taxonomy

**Files:**
- Modify: `.agents/skills/workflow/review-loop/SKILL.md` (49 lines → summary only)
- Create: `.agents/skills/workflow/review-loop/core.md`
- Create: `.agents/skills/workflow/review-loop/procedure.md`
- Create: `.agents/skills/workflow/review-loop/verification.md`
- Create: `.agents/skills/workflow/review-loop/failure-modes.md`

**Interfaces:**
- Consumes: the layer conventions from Task 5.
- Produces: the first real skill using all five preloadable layers — the migration
  pattern every remaining skill follows in Phase 1.

- [ ] **Step 1: Rewrite `SKILL.md` as the summary layer**

```markdown
---
name: review-loop
description: Bounded clean-up review for boy-scout, code and architectural smells and inappropriate coupling.
id: SKILL-review-loop
triggers: [before_merge, boy_scout_cleanup, diff_ready_for_review]
default_task_risk: normal
required_runtime: [shell, repo_search]
optional_runtime: [subagents]
layers:
  core: core.md
  procedure: procedure.md
  verification: verification.md
  failure_modes: failure-modes.md
canonical_for: [quality_boy_scout]
verification:
  - .agentic-template/bin/project test
  - .agentic-template/bin/project check
recovery_sources:
  - .agents/skills/CATALOG.toon
  - docs/validation.md
status: active
---

# Review Loop

## Outcome

A short, bounded pass that leaves the changed code cleaner than it was and surfaces
smells and coupling before merge. It enforces the standing quality rule; it does not
hunt for correctness bugs — code review does that.

## Use when

A diff is ready for merge, or a change touched code worth leaving cleaner.

Rules are in `core.md`, the two-pass sequence in `procedure.md`, the gate in
`verification.md`, and the ways this goes wrong in `failure-modes.md`.
```

- [ ] **Step 2: Write `core.md`**

```markdown
# Review Loop — Core

## What to look for

```
boy-scout        dead code, stale TODOs, unclear names in the change's path
code smells      long method, large class, duplication, feature envy,
                 primitive obsession, shotgun surgery
language smells  load the matching specialise/runtime-* "Language smells"
                 section lazily for the project's language
architectural    dependency cycles, layering violations, god modules,
                 leaky abstractions (architect persona)
coupling         inappropriate coupling; wrong dependency direction; a change
                 that ripples across many modules
```

## Rules

- Follow the boy-scout rule: leave code in the path of a change cleaner than you found
  it.
- Reuse over duplication: extract shared utility at the second or later occurrence,
  never on a single one. Do not pre-abstract.
- Refactor only with tests green, and keep changes within the diff's scope.
- Pay down technical debt directly in the work's path. Record out-of-scope debt as a
  `RISK-` or `PAT-` knowledge entry or a follow-up change — never a silent TODO.
- Documentation lands in the same change as the behaviour it describes.
- Cap the pass at two rounds. Escalate a genuine design disagreement to
  `adversarial-debate` with a per-persona stance rather than a third round.
```

- [ ] **Step 3: Write `procedure.md`, `verification.md` and `failure-modes.md`**

`procedure.md`:

```markdown
# Review Loop — Procedure

```
diff ──► pass 1: smells + coupling ──► apply safe cleanups (tests green)
     └─► pass 2: re-check ──► record residual findings ──► stop (≤2 passes)
```

1. Take the diff, not the whole repository. `git diff --stat` bounds the scope.
2. Pass 1: read the diff against the core checklist. Note every finding before
   changing anything, so the pass does not become an unplanned refactor.
3. Apply the cleanups that are safe with tests green. Leave the rest as findings.
4. Run the verification gate. If it is not green, stop and fix before continuing.
5. Pass 2: re-read the changed region only. Confirm the cleanups did not introduce new
   coupling.
6. Record residual findings as knowledge entries or follow-up changes, then stop.
```

`verification.md`:

```markdown
# Review Loop — Verification

The gate, in order:

1. `.agentic-template/bin/project test` — green before and after every cleanup.
2. `.agentic-template/bin/project check` — repository contract, profile, handoff,
   knowledge, specs and router configuration.
3. `git diff --check` — no whitespace damage introduced by the pass.

Evidence to record in `HANDOFF.toon.tests_run`: the date, each command and its result.

Do not claim a clean-up without a green run. If the harness itself is broken, repair it
without losing representative coverage, and say so.
```

`failure-modes.md`:

```markdown
# Review Loop — Failure Modes

| Symptom | Cause | Recovery |
|---|---|---|
| The pass grew into a refactor of untouched code | scope taken from the repository rather than the diff | reset the out-of-scope edits; record them as a follow-up change |
| Cleanups applied with tests red | verification skipped between passes | revert to the last green state and re-apply one cleanup at a time |
| A shared utility extracted on a single occurrence | pre-abstraction | inline it; extract at the second occurrence |
| Findings disappear after the session | recorded in prose instead of the knowledge graph | re-record as `RISK-` or `PAT-`, or as a change proposal |
| Third and fourth passes with diminishing findings | a design disagreement being relitigated | escalate to `adversarial-debate` with a per-persona stance |
| Correctness bugs reported as smells | review-loop used in place of code review | run code review; keep this pass on quality |
```

- [ ] **Step 4: Run the checks**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project context explain --skill review_loop --risk low
.agentic-template/bin/project context explain --skill review_loop --risk irreversible
.agentic-template/bin/project check
```
Expected: all tests pass. The `lean` plan preloads `SKILL.md` alone; the `irreversible`
plan preloads all five layers and reports
`independent_review: required_when_project_policy_demands`. `project check` warns that
`quality_boy_scout` now appears in both `AGENTS.md` and `review-loop/core.md` — that is
finding D8, promoted to an enforced topic in Phase 1 when `AGENTS.md` is slimmed.

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/workflow/review-loop
git commit -m "refactor(review-loop): split into summary, core, procedure, verification and failure modes"
```

---

### Task 12: Separate methodology from product in the wiki, and record the reasoning

**Files:**
- Create: `docs/wiki/method/context-router.md`, `docs/wiki/method/glossary.md`
- Move: `docs/wiki/{agents,development,testing}.md` → `docs/wiki/method/`
- Move: `docs/wiki/{architecture,domain,operations}.md` → `docs/wiki/product/`
- Move: `docs/wiki/glossary.md` → `docs/wiki/product/glossary.md`
- Modify: `docs/wiki/index.md` (route by axis)
- Modify: `.agentic-template/bin/context` (axis validation in `validate()`)
- Modify: `docs/README.md`, `.agentic-template/bin/docs-map`, `README.md`
- Test: `.agentic-template/tests/test_taxonomy_check.py` (axis cases)

**Interfaces:**
- Consumes: `skills.parse_frontmatter` (Task 5), `validate()` (Task 8).
- Produces: the `axis: method | product` convention described in A12, enforced by
  `project context check`, plus the durable record of why the router exists.

- [ ] **Step 1: Write the failing test**

Append to `.agentic-template/tests/test_taxonomy_check.py`:

```python
class TestWikiAxis(CheckTestCase):
    def test_every_wiki_page_declares_an_axis(self):
        result = run_check(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_axis_fails(self):
        page = self.root / "docs/wiki/method/development.md"
        page.write_text(page.read_text().replace("axis: method\n", "", 1))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("axis", result.stdout)
        self.assertIn("development.md", result.stdout)

    def test_axis_disagreeing_with_the_directory_fails(self):
        page = self.root / "docs/wiki/product/domain.md"
        page.write_text(page.read_text().replace("axis: product", "axis: method", 1))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("domain.md", result.stdout)
        self.assertIn("product/", result.stdout)

    def test_page_outside_both_axes_fails(self):
        stray = self.root / "docs/wiki/stray.md"
        stray.write_text("---\naxis: method\n---\n\n# Stray\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("stray.md", result.stdout)

    def test_index_is_exempt(self):
        self.assertNotIn("index.md", run_check(ROOT).stdout)


class TestReasoningIsRecorded(unittest.TestCase):
    def test_the_router_page_exists_and_states_the_principle(self):
        page = (ROOT / "docs/wiki/method/context-router.md").read_text()
        self.assertIn("portable context router", page.lower())
        self.assertIn("depth and timing", page.lower())
        self.assertIn("not", page.lower())

    def test_the_router_page_cites_the_source_article(self):
        page = (ROOT / "docs/wiki/method/context-router.md").read_text()
        self.assertIn("context engineering", page.lower())
        self.assertIn("2026-07-24", page)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k Axis -v`
Expected: FAIL — the `method/` and `product/` directories do not exist.

- [ ] **Step 3: Move the pages and stamp the axis**

```bash
mkdir -p docs/wiki/method docs/wiki/product
git mv docs/wiki/agents.md docs/wiki/development.md docs/wiki/testing.md docs/wiki/method/
git mv docs/wiki/architecture.md docs/wiki/domain.md docs/wiki/operations.md docs/wiki/product/
git mv docs/wiki/glossary.md docs/wiki/product/glossary.md
```

Add frontmatter to the top of each moved page — `axis: method` for the three in
`method/`, `axis: product` for the four in `product/`:

```markdown
---
axis: method
---

# Agents
```

- [ ] **Step 4: Write the two new method pages**

`docs/wiki/method/glossary.md`:

```markdown
---
axis: method
---

# Method Glossary

Vocabulary for how this repository works. Domain vocabulary lives in
[the product glossary](../product/glossary.md).

| Term | Meaning |
|---|---|
| Axis | Whether a page documents methodology (inherited) or the product (project-written) |
| Context profile | `lean`, `standard` or `guarded` — how much context is preloaded |
| Taxonomy layer | `summary`, `core`, `procedure`, `verification`, `examples`, `failure-modes`, `references` |
| Portable context router | The resolver that picks a profile and renders a context plan |
| Context plan | The preload set, deferred set, verification and recovery map for one task |
| Qualification | Fixture-scored evidence that a model-runtime pair handles this contract |
| Observation | A recorded qualification result and degradation history, scoped to a fingerprint |
| Task-risk floor | The minimum profile a risk class requires, applied after capability routing |
| Fitness function | A cheap deterministic check protecting an architecture characteristic |
| Context packet | A bounded, sourced hand-off of context to another agent or model |
```

`docs/wiki/method/context-router.md` — the reasoning record:

```markdown
---
axis: method
---

# Portable Context Router

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
what is deferred                     safety boundaries
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

## Related

- `docs/context-store.md` — the four repository layers the router draws sources from.
- `.agents/context/README.md` — configuration reference.
- `.agents/skills/tooling/context-qualification/SKILL.md` — running qualification.
```

- [ ] **Step 5: Rewrite the wiki index**

`docs/wiki/index.md`:

```markdown
# Wiki

Durable project understanding, split by axis. **Method** pages describe how work is done
here and are inherited from the template. **Product** pages describe what is being built
and are written by this project.

## Method — how we work

| Page | Covers |
|---|---|
| [Agents](method/agents.md) | Startup, roles and delegation |
| [Development](method/development.md) | Day-to-day lifecycle and command sequence |
| [Testing](method/testing.md) | Validation strategy and layer selection |
| [Portable context router](method/context-router.md) | Why and how context depth is routed |
| [Method glossary](method/glossary.md) | Vocabulary for the way we work |

## Product — what we are building

| Page | Covers |
|---|---|
| [Architecture](product/architecture.md) | Runtime shape and boundaries |
| [Domain](product/domain.md) | Domain model and language |
| [Operations](product/operations.md) | Running and operating the system |
| [Product glossary](product/glossary.md) | Domain vocabulary |

## Elsewhere

- [Context store](../context-store.md) — how context is preserved across sessions.
- [Validation](../validation.md) — what checks prove.
- [Decisions](../decisions/) — ADRs.

## Rules

- Every page declares `axis: method` or `axis: product` matching its directory;
  `project context check` fails when they disagree.
- A fact has one canonical home. Other pages link to it.
- Generated projects rewrite `product/` and inherit `method/`. Changing a `method/` page
  is a change to how the team works, and belongs in a decision record.
```

- [ ] **Step 6: Implement axis validation**

Add to `.agentic-template/bin/context`, and call it from `validate()`:

```python
WIKI_AXES = ("method", "product")


def _check_wiki_axis(root, errors):
    wiki = Path(root) / "docs/wiki"
    if not wiki.exists():
        return
    for path in sorted(wiki.rglob("*.md")):
        relative = str(path.relative_to(root))
        if path.parent == wiki:
            if path.name != "index.md":
                errors.append(
                    f"{relative}: wiki pages live under docs/wiki/method/ or "
                    f"docs/wiki/product/; only index.md sits at the root"
                )
            continue
        axis = path.relative_to(wiki).parts[0]
        if axis not in WIKI_AXES:
            errors.append(f"{relative}: unknown wiki axis directory '{axis}'")
            continue
        try:
            meta, _ = skills.parse_frontmatter(path.read_text())
        except skills.SkillError:
            errors.append(f"{relative}: wiki pages must declare 'axis: {axis}' in frontmatter")
            continue
        declared = meta.get("axis")
        if declared != axis:
            errors.append(
                f"{relative}: frontmatter says axis '{declared}' but the page is in "
                f"{axis}/; the directory and the frontmatter must agree"
            )
```

In `validate()`, add `_check_wiki_axis(root, errors)` after `_check_skills(root, errors)`.

- [ ] **Step 7: Update every reference to a moved page**

Run:
```bash
grep -rn "docs/wiki/\(agents\|development\|testing\|architecture\|domain\|operations\|glossary\)\.md\|](\(agents\|development\|testing\|architecture\|domain\|operations\|glossary\)\.md" \
  --include='*.md' --include='*.toon' --include='ci.yml' . \
  | grep -v '^./docs/superpowers/'
```
Update every hit — expected in `docs/README.md`, `.agentic-template/bin/docs-map`,
`README.md` and possibly `.agentic-template/templates/README_TEMPLATE.md`. Add the
`Method / Product` distinction to the `docs/README.md` map and to the `docs-map` output.

- [ ] **Step 8: Run the full check**

Run:
```bash
python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v
.agentic-template/bin/project check
.agentic-template/bin/project check-wiki
.agentic-template/bin/project docs
```
Expected: all tests pass; `CONTEXT ROUTER OK`; `WIKI OK`; the docs map shows both axes.

- [ ] **Step 9: Commit**

```bash
git add docs/wiki docs/README.md README.md .agentic-template/bin/docs-map \
        .agentic-template/bin/context .agentic-template/tests/test_taxonomy_check.py
git commit -m "docs(wiki): separate methodology from product and record the router reasoning

Every wiki page now declares axis: method or product, matching its directory and
enforced by project context check. Adds method/context-router.md as the durable
record of why context depth is routed rather than fixed."
```

---

### Task 13: `project context scaffold` and the generated-project fixture

**Files:**
- Modify: `.agentic-template/bin/context` (register `scaffold`, add the manifest)
- Create: `.agentic-template/fixtures/generated-project/` (project-owned files only)
- Test: `.agentic-template/tests/test_scaffold_acceptance.py` (AC-1 and AC-2)

**Interfaces:**
- Consumes: everything from Tasks 1-12.
- Produces:
  - `context.SCAFFOLD_COPY` — paths copied byte-identically.
  - `context.SCAFFOLD_STARTER` — paths written only when absent.
  - `context.SCAFFOLD_NEVER` — project-owned paths the scaffold must not touch.
  - `project context scaffold --into <dir> [--apply]`, report-only by default.

**Design note — two kinds of scaffolded file.** Copy-kind files *are* the router
(`ROUTER.toon`, `RECOVERY.toon`, `runtimes.toon`, the library, the command, the
qualification contract and fixture). Starter-kind files are where a project records its
own facts (`TOPICS.toon`, `risk-rules.toon`); the template ships a minimal opening
version and never overwrites one that exists. The portable unit tests travel with the
scaffold; the template-specific ones (`test_explain.py`, `test_taxonomy_check.py`,
`test_scaffold_acceptance.py`) do not, because they assert against this repository's own
skills and wiki.

- [ ] **Step 1: Write the failing test**

`.agentic-template/tests/test_scaffold_acceptance.py`:

```python
import filecmp
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import _support  # noqa: F401
import toon

ROOT = _support.ROOT
FIXTURE = ROOT / ".agentic-template/fixtures/generated-project"


def scaffold_into(target, apply=True):
    args = [str(_support.BIN / "project"), "context", "scaffold", "--into", str(target)]
    if apply:
        args.append("--apply")
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def project_run(target, *args):
    return subprocess.run(
        [str(target / ".agentic-template/bin/project"), "context", *args],
        cwd=target,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


class ScaffoldTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "generated"
        shutil.copytree(FIXTURE, self.project)

    def tearDown(self):
        self.tmp.cleanup()


class TestAC1Inheritance(ScaffoldTestCase):
    def test_dry_run_is_the_default_and_writes_nothing(self):
        result = scaffold_into(self.project, apply=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse((self.project / ".agents/context/ROUTER.toon").exists())
        self.assertIn("dry run", result.stdout.lower())

    def test_apply_copies_every_copy_kind_file_byte_identically(self):
        self.assertEqual(scaffold_into(self.project).returncode, 0)
        for relative in ("ROUTER.toon", "RECOVERY.toon", "runtimes.toon", "overrides.toon"):
            source = ROOT / ".agents/context" / relative
            target = self.project / ".agents/context" / relative
            with self.subTest(file=relative):
                self.assertTrue(target.exists())
                self.assertTrue(filecmp.cmp(source, target, shallow=False))

    def test_apply_installs_the_library_command_and_portable_tests(self):
        scaffold_into(self.project)
        for relative in (
            ".agentic-template/lib/router.py",
            ".agentic-template/bin/context",
            ".agentic-template/tests/test_router_precedence.py",
        ):
            with self.subTest(file=relative):
                self.assertTrue((self.project / relative).exists())

    def test_template_specific_tests_are_not_scaffolded(self):
        scaffold_into(self.project)
        self.assertFalse((self.project / ".agentic-template/tests/test_explain.py").exists())

    def test_starter_files_do_not_overwrite_project_versions(self):
        original = (self.project / ".agents/context/risk-rules.toon").read_text()
        scaffold_into(self.project)
        self.assertEqual((self.project / ".agents/context/risk-rules.toon").read_text(), original)

    def test_project_owned_files_are_never_touched(self):
        original = (self.project / ".agents/context/overrides.local.toon").read_text()
        scaffold_into(self.project)
        self.assertEqual(
            (self.project / ".agents/context/overrides.local.toon").read_text(), original
        )

    def test_scaffolded_command_is_executable(self):
        scaffold_into(self.project)
        result = project_run(self.project, "explain", "--skill", "ship_slice")
        self.assertEqual(result.returncode, 0, result.stdout)


class TestAC2ProjectValidates(ScaffoldTestCase):
    def test_the_generated_project_passes_context_check(self):
        scaffold_into(self.project)
        result = project_run(self.project, "check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CONTEXT ROUTER OK", result.stdout)

    def test_both_project_skills_are_layered_and_catalogued(self):
        catalog = toon.loads((self.project / ".agents/skills/CATALOG.toon").read_text())
        self.assertIn("ship_slice", catalog["skills"])
        self.assertIn("pricing_rules", catalog["skills"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k Scaffold -v`
Expected: FAIL — the fixture directory does not exist.

- [ ] **Step 3: Build the generated-project fixture**

Create `.agentic-template/fixtures/generated-project/` containing only project-owned
files. It is a *specialised* project: no template markers.

`AGENTS.md`:

```markdown
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
```

`PROJECT_PROFILE.toon`:

```toon
project:
  state: specialised
  confidence: high
context_router:
  scaffold_version: 1
  profile_policy: template_default
```

`.agents/skills/CATALOG.toon`:

```toon
skills:
  ship_slice:
    path: workflow/ship-slice/SKILL.md
    trigger: thin_slice_ready_to_ship
  pricing_rules:
    path: domain/pricing-rules/SKILL.md
    trigger: price_rule_change_requested
```

`.agents/skills/workflow/ship-slice/SKILL.md` — the project-local **workflow**, with all
five preloadable layers so the fixture can exercise every profile:

```markdown
---
name: ship-slice
description: Ship one thin vertical slice of pricing behaviour behind a flag.
id: SKILL-ship-slice
triggers: [thin_slice_ready_to_ship]
default_task_risk: normal
layers:
  core: core.md
  procedure: procedure.md
  verification: verification.md
  failure_modes: failure-modes.md
verification: [.agentic-template/bin/project test]
recovery_sources: [.agents/skills/CATALOG.toon]
status: active
---

# Ship Slice

## Outcome

One thin vertical slice of pricing behaviour is live behind a flag, with its acceptance
scenario proven.
```

Its four layer files each hold real content — for example `core.md`:

```markdown
# Ship Slice — Core

- A slice is one scenario end to end, never a layer across many scenarios.
- Every slice ships behind a flag defaulted off.
- A slice without an acceptance scenario is not a slice.
```

`procedure.md` lists the five steps from scenario to flag flip; `verification.md` names
`project test` and the flag-off regression; `failure-modes.md` tabulates the three ways
slices go wrong. Keep each above the 40-character minimum the validator enforces.

`.agents/skills/domain/pricing-rules/SKILL.md` — the project-local **skill**, with two
layers, showing that not every skill needs every layer:

```markdown
---
name: pricing-rules
description: How discount, tax and rounding rules compose in this domain.
id: SKILL-pricing-rules
triggers: [price_rule_change_requested]
default_task_risk: high
layers:
  core: core.md
  references: references.md
verification: [.agentic-template/bin/project contract-test]
recovery_sources: [specs/capabilities/]
status: active
---

# Pricing Rules

## Outcome

A price change composes correctly with existing discount, tax and rounding rules.
```

`.agents/context/overrides.local.toon` — the project-local override for AC-6:

```toon
version: 1
overrides:
  - match:
      model: fixture-qualified-model
      runtime: "*"
    profile: lean
    reason: qualified against this project's fixture on 2026-07-26
    expires: 2099-01-01
```

`.agents/context/risk-rules.toon` — project-owned, proving starter files are not
overwritten, and driving AC-9:

```toon
version: 1
default: normal
rules:
  - id: published_price_rule
    paths: [specs/capabilities/*, src/pricing/rules/*]
    risk: high
  - id: documentation
    paths: [docs/*, "*.md"]
    risk: low
```

Also include minimal `docs/validation.md`, `docs/wiki/index.md`,
`.agents/coordination/REVIEW_POLICY.md`, `.agents/knowledge/TAXONOMY.md` and
`specs/capabilities/CAP-001-pricing.toon`, so that every source the router preloads or
cites resolves.

- [ ] **Step 4: Implement the scaffold**

Add to `.agentic-template/bin/context`:

```python
SCAFFOLD_COPY = (
    ".agentic-template/lib/toon.py",
    ".agentic-template/lib/environment.py",
    ".agentic-template/lib/router.py",
    ".agentic-template/lib/observations.py",
    ".agentic-template/lib/skills.py",
    ".agentic-template/lib/plan.py",
    ".agentic-template/lib/qualification.py",
    ".agentic-template/bin/context",
    ".agentic-template/bin/context-test",
    ".agentic-template/tests/_support.py",
    ".agentic-template/tests/test_toon.py",
    ".agentic-template/tests/test_router_precedence.py",
    ".agentic-template/tests/test_environment.py",
    ".agentic-template/tests/test_observations.py",
    ".agentic-template/tests/test_qualification.py",
    ".agentic-template/fixtures/qualification-repo",
    ".agents/context/ROUTER.toon",
    ".agents/context/RECOVERY.toon",
    ".agents/context/runtimes.toon",
    ".agents/context/overrides.toon",
    ".agents/context/qualification",
    ".agents/skills/tooling/context-qualification/SKILL.md",
)

SCAFFOLD_STARTER = {
    ".agents/context/TOPICS.toon": (
        "# Project-owned. One canonical home per topic; markers must be 20+ characters.\n"
        "version: 1\n"
        "scan_roots: [AGENTS.md, .agents/, docs/]\n"
        "exclude: [.agentic-template/, .agents/context/observations/]\n"
        "topics: []\n"
        "candidates: []\n"
    ),
    ".agents/context/risk-rules.toon": (
        "# Project-owned. First matching rule per path; highest risk across paths wins.\n"
        "version: 1\n"
        "default: normal\n"
        "rules:\n"
        "  - id: documentation\n"
        '    paths: [docs/*, "*.md"]\n'
        "    risk: low\n"
    ),
}

SCAFFOLD_NEVER = (
    ".agents/context/overrides.local.toon",
    ".agents/context/observations",
)


def _scaffold_actions(target):
    actions = []
    for relative in SCAFFOLD_COPY:
        source = ROOT / relative
        destination = target / relative
        if not source.exists():
            actions.append(("missing", relative, "source absent from this template"))
        elif not destination.exists():
            actions.append(("create", relative, "copy"))
        elif source.is_dir() or destination.read_bytes() != source.read_bytes():
            actions.append(("update", relative, "copy"))
        else:
            actions.append(("unchanged", relative, "copy"))
    for relative in SCAFFOLD_STARTER:
        exists = (target / relative).exists()
        actions.append(("keep" if exists else "create", relative, "starter"))
    for relative in SCAFFOLD_NEVER:
        actions.append(("skip", relative, "project-owned"))
    return actions


def cmd_scaffold(args):
    target = Path(args.into).resolve()
    if not target.is_dir():
        return _fail(f"--into must be an existing directory: {target}")
    if target == ROOT:
        return _fail("refusing to scaffold the template into itself")
    actions = _scaffold_actions(target)
    print("SCAFFOLD " + ("apply" if args.apply else "dry run"))
    print()
    for verb, relative, kind in actions:
        print(f"  {verb:<10} {kind:<9} {relative}")
    if any(verb == "missing" for verb, _, _ in actions):
        print()
        return _fail("template is incomplete; run project check before scaffolding")
    if not args.apply:
        print()
        print("  dry run: nothing written. Re-run with --apply.")
        return 0
    for verb, relative, kind in actions:
        if kind == "copy" and verb in ("create", "update"):
            source = ROOT / relative
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(source, destination)
        elif kind == "starter" and verb == "create":
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(SCAFFOLD_STARTER[relative])
    (target / ".agents/context/observations").mkdir(parents=True, exist_ok=True)
    print()
    print("  next: .agentic-template/bin/project context check")
    return 0
```

with `import shutil` added, and the subparser:

```python
    scaffold = subparsers.add_parser(
        "scaffold", help="install the portable context router into a project"
    )
    scaffold.add_argument("--into", required=True, help="target project directory")
    scaffold.add_argument(
        "--apply", action="store_true", help="write files; omit for a dry run"
    )
    scaffold.set_defaults(handler=cmd_scaffold)
```

The scaffold copies `.agentic-template/bin/context` but a generated project also needs it
registered in its own `project` facade. Print that as a follow-up line when the target's
`.agentic-template/bin/project` lacks a `"context"` entry.

- [ ] **Step 5: Run the tests**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -v`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add .agentic-template/bin/context .agentic-template/fixtures/generated-project \
        .agentic-template/tests/test_scaffold_acceptance.py
git commit -m "feat(context-router): scaffold the router into a generated project"
```

---

### Task 14: Acceptance suite, `context test` and CI

**Files:**
- Create: `.agentic-template/bin/context-test`
- Modify: `.agentic-template/tests/test_scaffold_acceptance.py` (AC-3 to AC-14)
- Modify: `.agentic-template/bin/context` (register `test`)
- Modify: `.agentic-template/bin/self-test` (invoke `context test`)
- Modify: `.github/workflows/ci.yml` (run `self-test`, fixing C3)
- Modify: `.agentic-template/bin/check-repo-contract` (require the new files)

**Interfaces:**
- Consumes: everything above.
- Produces: `project context test`, and the ten first-slice outcomes proven end to end
  inside the generated-project fixture.

- [ ] **Step 1: Write the remaining acceptance tests**

Append to `.agentic-template/tests/test_scaffold_acceptance.py`. Each class name states
which acceptance scenario from A11 it proves.

```python
class TestAC3toAC5Profiles(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def _plan(self, *args):
        result = project_run(self.project, "explain", "--format", "toon", *args)
        self.assertEqual(result.returncode, 0, result.stdout)
        return toon.loads(result.stdout)["context_plan"]

    def _qualify(self):
        # Record a passing observation for the fixture environment.
        project_run(self.project, "observe", "--event", "success", "--model", "m1")
        path = next((self.project / ".agents/context/observations").glob("*.toon"))
        data = toon.loads(path.read_text())
        data["observation"]["result"] = "pass"
        path.write_text(toon.dumps(data))

    def test_ac3_lean_preloads_only_the_summary(self):
        self._qualify()
        plan = self._plan("--skill", "ship_slice", "--risk", "low", "--model", "m1")
        self.assertEqual(plan["decision"]["profile"], "lean")
        self.assertEqual(
            {e["layer"] for e in plan["preload"] if e.get("skill")}, {"summary"}
        )

    def test_ac4_standard_adds_core_and_defers_procedure(self):
        plan = self._plan("--skill", "ship_slice", "--risk", "low")
        self.assertEqual(plan["decision"]["profile"], "standard")
        self.assertIn("core", {e["layer"] for e in plan["preload"] if e.get("skill")})
        self.assertIn("procedure", {e["layer"] for e in plan["defer"]})

    def test_ac5_guarded_adds_procedure_verification_failure_modes_and_review(self):
        plan = self._plan("--skill", "ship_slice", "--risk", "high")
        self.assertEqual(plan["decision"]["profile"], "guarded")
        layers = {e["layer"] for e in plan["preload"] if e.get("skill")}
        self.assertTrue({"procedure", "verification", "failure_modes"} <= layers)
        self.assertNotEqual(plan["independent_review"], "not_required")


class TestAC6LocalOverride(ScaffoldTestCase):
    def test_local_override_selects_lean_and_names_its_file(self):
        scaffold_into(self.project)
        result = project_run(
            self.project, "explain", "--skill", "ship_slice", "--risk", "low",
            "--model", "fixture-qualified-model",
        )
        self.assertIn("lean", result.stdout)
        self.assertIn("overrides.local.toon", result.stdout)


class TestAC7andAC8Qualification(ScaffoldTestCase):
    def test_pack_and_scoring_run_inside_the_generated_project(self):
        scaffold_into(self.project)
        pack = project_run(self.project, "qualify")
        self.assertEqual(pack.returncode, 0, pack.stdout)
        self.assertIn("contract_read", pack.stdout)

    def test_wrong_contract_sha_fails_inside_the_generated_project(self):
        scaffold_into(self.project)
        answers = self.project / "answers.toon"
        answers.write_text(
            toon.dumps(
                {
                    "answers": {
                        "qualification_version": 1,
                        "probes": [{"id": "contract_read", "sha": "0" * 16}],
                    }
                }
            )
        )
        result = project_run(self.project, "qualify", "--score", str(answers))
        self.assertEqual(result.returncode, 1)


class TestAC9RiskFloorFromPaths(ScaffoldTestCase):
    def test_touching_a_published_rule_forces_guarded_without_a_flag(self):
        scaffold_into(self.project)
        result = project_run(
            self.project, "explain", "--skill", "pricing_rules",
            "--paths", "specs/capabilities/CAP-001-pricing.toon",
        )
        self.assertIn("guarded", result.stdout)
        self.assertIn("published_price_rule", result.stdout)


class TestAC10toAC12RecoveryAndInvalidation(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def test_ac10_first_degradation_reloads_the_authoritative_source(self):
        recorded = project_run(
            self.project, "observe", "--event", "degraded", "--symptom", "skill_path_wrong"
        )
        self.assertIn("CATALOG.toon", recorded.stdout)
        plan = project_run(self.project, "explain", "--skill", "ship_slice")
        self.assertIn("RECOVER FIRST", plan.stdout)
        self.assertIn("CATALOG.toon", plan.stdout)

    def test_ac11_second_degradation_escalates_one_step(self):
        project_run(self.project, "observe", "--event", "degraded", "--symptom", "unknown")
        second = project_run(
            self.project, "observe", "--event", "degraded", "--symptom", "unknown",
            "--profile", "lean",
        )
        self.assertIn("escalate", second.stdout)
        self.assertIn("standard", second.stdout)

    def test_ac12_editing_the_contract_invalidates_the_observation(self):
        project_run(self.project, "observe", "--event", "success")
        agents = self.project / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--risk", "low")
        self.assertIn("invalidated", result.stdout)
        self.assertIn("standard", result.stdout)


class TestAC13andAC14Explainability(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def test_ac13_toon_output_has_every_section(self):
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--format", "toon")
        plan = toon.loads(result.stdout)["context_plan"]
        for section in (
            "decision", "environment", "task", "preload", "defer",
            "verification", "recovery", "effort_directives",
        ):
            self.assertIn(section, plan)

    def test_ac14_required_verification_is_identical_across_profiles(self):
        required = []
        for risk in ("low", "normal", "high"):
            result = project_run(
                self.project, "explain", "--skill", "ship_slice", "--risk", risk, "--format", "toon"
            )
            required.append(toon.loads(result.stdout)["context_plan"]["verification"]["required"])
        self.assertEqual(required[0], required[1])
        self.assertEqual(required[1], required[2])
        self.assertTrue(required[0])

    def test_every_decision_states_its_reasons_and_precedence(self):
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--format", "toon")
        decision = toon.loads(result.stdout)["context_plan"]["decision"]
        self.assertTrue(decision["reasons"])
        self.assertEqual(len(decision["precedence_applied"]), 5)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m unittest discover -s .agentic-template/tests -t .agentic-template/tests -k AC -v`
Expected: failures until the fixture files from Task 13 Step 3 are complete. Fix the
fixture, not the assertions.

- [ ] **Step 3: Add the test runner and register it**

`.agentic-template/bin/context-test` (executable):

```python
#!/usr/bin/env python3
"""Run the portable context router test suite. Internal; use `project context test`."""
import subprocess
import sys
from pathlib import Path

TESTS = Path.cwd() / ".agentic-template/tests"

if __name__ == "__main__":
    if not TESTS.is_dir():
        print("ERROR")
        print()
        print(f"no test directory at {TESTS}")
        sys.exit(2)
    sys.exit(
        subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(TESTS), "-t", str(TESTS)]
        ).returncode
    )
```

Register in `.agentic-template/bin/context`:

```python
    tests = subparsers.add_parser("test", help="run the context router test suite")
    tests.set_defaults(handler=lambda args: subprocess.call([str(BIN / "context-test")]))
```

with `import subprocess` added.

- [ ] **Step 4: Wire it into `self-test` and CI**

In `.agentic-template/bin/self-test`, inside `main()` before the failure summary:

```python
        if not expect(work, "context router suite passes", PROJECT + ["context", "test"], 0):
            failures += 1
```

In `.github/workflows/ci.yml`, add a step after "Repository checks" — this closes
conflict C3, which is why the template's richest suite never ran:

```yaml
      - name: Self test
        run: .agentic-template/bin/project self-test
```

In `.agentic-template/bin/check-repo-contract`, add to `REQUIRED_FILES`:

```python
    ".agentic-template/bin/context-test",
    ".agents/context/TOPICS.toon",
    ".agents/context/qualification/QUALIFICATION.toon",
    "docs/wiki/method/context-router.md",
    "docs/wiki/index.md",
```

and add `"context-test"` to `PROJECT_COMMANDS` only if you also expose it on the facade;
otherwise leave `PROJECT_COMMANDS` unchanged, since `context test` is a subcommand.

- [ ] **Step 5: Run everything**

Run:
```bash
.agentic-template/bin/project context test
.agentic-template/bin/project check
.agentic-template/bin/project self-test
.agentic-template/bin/project ready
git diff --check
```
Expected: all green. Record each result and its date in `HANDOFF.toon.tests_run`
(Task 15).

- [ ] **Step 6: Commit**

```bash
git add .agentic-template/bin/context-test .agentic-template/bin/context \
        .agentic-template/bin/self-test .agentic-template/bin/check-repo-contract \
        .github/workflows/ci.yml .agentic-template/tests/test_scaffold_acceptance.py
git commit -m "test(context-router): prove the ten first-slice outcomes in a generated project

Also runs project self-test in CI, which previously ran nowhere."
```

---

### Task 15: Documentation, recorded state and knowledge

**Files:**
- Create: `.agents/context/README.md`
- Create: `.agents/knowledge/inbox/INBOX-009-portable-context-router.md`
- Modify: `AGENTS.md` (add the 8-line "Context routing" section)
- Modify: `.agentic-template/templates/AGENTS_TEMPLATE.md`,
  `.agentic-template/templates/README_TEMPLATE.md`
- Modify: `.agentic-template/bin/startup`, `.agentic-template/bin/docs-map`,
  `docs/README.md`
- Modify: `PROJECT_PROFILE.toon`, `HANDOFF.toon`

- [ ] **Step 1: Write the configuration reference**

`.agents/context/README.md` — which file to edit, and nothing about *why* (the wiki page
owns that):

```markdown
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
```

- [ ] **Step 2: Add the `AGENTS.md` section**

Insert after "Canonical commands", exactly this and no more:

```markdown
## Context routing

Before non-trivial work, run
`.agentic-template/bin/project context explain --skill <id> --paths <files>` and load
what it lists. It reports the profile (`lean`, `standard`, `guarded`), what to preload,
what to defer, the required verification and where to recover from.

Profiles change how much context is loaded. They never change acceptance criteria,
safety boundaries, validation or approval points. High-risk and irreversible work is
always `guarded`.

When output degrades, reload the source named in `.agents/context/RECOVERY.toon` and
retry once before adding context.
```

- [ ] **Step 3: Require the same of generated projects**

In `AGENTS_TEMPLATE.md`, add to the required sections:

```markdown
21. **Context routing** — the profile ladder, that profiles never change required
    outcomes, and the recover-then-retry rule before escalating context.
```

In `README_TEMPLATE.md`, add:

```markdown
18. **Context routing** — state that the project carries a portable context router,
    show `project context explain`, and note that method and product documentation are
    separated by wiki axis.
```

Add a one-line routing hint to `.agentic-template/bin/startup` under `START PATHS`:

```
- Size the context for a task
  Run .agentic-template/bin/project context explain --skill <id> --paths <files>.
```

Add a `Context router` route to `docs/README.md` and `.agentic-template/bin/docs-map`
pointing at `docs/wiki/method/context-router.md` and `.agents/context/README.md`, and add
the method/product split to the wiki row.

- [ ] **Step 4: Record the decisions**

Add to `PROJECT_PROFILE.toon.decisions`:

```toon
  - id: portable_context_router
    decision: route context depth and timing by profile, never required behaviour
    reason:
      - capable models lose reasoning to duplicated and contradictory guidance
      - unfamiliar runtimes and high-risk work still need explicit scaffolding
      - a template cannot know which model or runtime will read it
    confidence: medium
    status: active
    validation:
      - .agentic-template/bin/project context check
      - .agentic-template/bin/project context test
      - docs/wiki/method/context-router.md
    consequence_if_changed: context size becomes a fixed guess that is wrong for some readers
  - id: capability_by_observation_not_registry
    decision: license lean context from fixture-scored behaviour, never from model identity
    reason:
      - self-reported identity can be absent or wrong
      - the same model behaves differently across runtimes
      - a model registry is stale the week after it is written
    confidence: medium
    status: active
    validation:
      - .agents/context/qualification/QUALIFICATION.toon
      - .agentic-template/fixtures/qualification-repo
    consequence_if_changed: routing becomes a reputation judgement rather than evidence
  - id: wiki_method_product_axis
    decision: every wiki page declares axis method or product, matching its directory
    reason:
      - methodology is inherited from the template; product documentation is written by the project
      - generated-project users should not read template procedure beside their domain model
      - agents need to know which pages they rewrite after /specialise
    confidence: high
    status: active
    validation:
      - .agentic-template/bin/project context check
      - docs/wiki/index.md
    consequence_if_changed: generated wikis interleave inherited procedure with project knowledge
  - id: yaml_skill_frontmatter_deviation
    decision: keep skill frontmatter in YAML despite the TOON default for state
    reason:
      - native skill loaders in supported hosts parse YAML
      - the parsed subset is identical, so one parser serves both
    confidence: high
    status: active
    validation:
      - .agentic-template/lib/skills.py
    consequence_if_changed: skills stop loading natively in at least one supported runtime
```

Add to `PROJECT_PROFILE.toon.tooling`:

```toon
  context_router:
    scaffold_version: 1
    profiles: [lean, standard, guarded]
    default_on_uncertainty: standard
    qualification: fixture_scored
    observations: gitignored_in_template
    guide: docs/wiki/method/context-router.md
    config: .agents/context/README.md
    validator: .agentic-template/bin/project context check
```

Add to `PROJECT_PROFILE.toon.rejected_options`:

```toon
  - id: model_capability_registry
    option: maintain a table of models and their context capabilities
    reason_rejected:
      - stale within weeks of being written
      - self-reported identity is unreliable
      - the same model differs by runtime
    evidence:
      - .agents/context/qualification/QUALIFICATION.toon
  - id: host_auto_memory_for_project_facts
    option: rely on host-managed automatic memory instead of repository state
    reason_rejected:
      - not portable across Claude Code, Codex, OpenCode and Roo
      - unversioned, unreviewable and invisible to CI
      - becomes a second source of truth beside the repo-native context store
    evidence:
      - docs/context-store.md
```

- [ ] **Step 5: Propose the pattern as knowledge**

`.agents/knowledge/inbox/INBOX-009-portable-context-router.md`, following
`.agents/knowledge/templates/inbox-proposal.md`: id `INBOX-009`, type `pattern`, status
`proposed`, title "Route context depth by observed capability and task risk", summary
naming the three profiles and the never-route-behaviour rule, `relates_to` the router
decisions above, and an evidence section that states plainly that the only evidence so
far is the template's own fixture — promotion needs a real generated project.

- [ ] **Step 6: Update the handoff**

Rewrite `HANDOFF.toon` for this change: objective, phase `thin_slice_complete`, the
completed list from Tasks 1-15, next actions (Phase 1 items from A13), the decisions
above, the risks from A13, `files_changed`, every command from Task 14 Step 5 with its
date and result in `tests_run`, the knowledge section citing the article, the consulted
knowledge entries and `INBOX-009`, and `team_fallback` recording that this ran as a
single lead agent with a checklist.

- [ ] **Step 7: Validate everything**

Run:
```bash
.agentic-template/bin/project check
.agentic-template/bin/project check-readme
.agentic-template/bin/project check-wiki
.agentic-template/bin/project self-test
.agentic-template/bin/project ready
.agentic-template/bin/project context test
git diff --check
```
Expected: all pass. `project check` still warns about D1, D2, D4, D8 and D9 — the Phase 1
ledger — and exits `0`.

- [ ] **Step 8: Commit and open the pull request**

```bash
git add -A
git commit -m "docs(context-router): document the router, record decisions and update handoff"
git push -u origin HEAD
gh pr create --title "Portable context router scaffold (thin slice)" --body "$(cat <<'BODY'
Adds a portable context router that generated projects inherit: three context
profiles chosen by override, fixture-scored qualification, degradation state and
task-risk floors, rendering an explainable context plan.

Routes context depth and timing only. Acceptance criteria, safety boundaries,
validation and approval points are identical under every profile, proven by
AC-14.

Thin slice: scaffold, two migrated skills (context-packet, review-loop), the
wiki method/product split, and a generated-project acceptance fixture. Broad
AGENTS.md and skill migration is deferred to Phase 1; `project check` warns on
the remaining duplications as a ledger.

Also catalogues eight previously unreachable skills and runs `project self-test`
in CI for the first time.
BODY
)"
```

---

## Self-review

**Spec coverage.** All fifteen numbered requests are covered: inspection (A1),
duplication and prescriptiveness (A2), root-file migration (A3), tool guidance (A4),
architecture (A5), template/project boundary (A6), taxonomy and migration map (A3, A7),
routing policy and override, qualification, observation and recovery formats (A8, Tasks
2, 4, 9), the two commands (Tasks 7, 9), two migration skills (A10, Tasks 10-11), the
acceptance fixture (A11, Tasks 13-14), all twelve test categories (mapped below),
terminology (Task 15), assumptions and exclusions (A13), and the stop-before-migration
review (all of Part A). The mid-turn request for a methodology/product convention is
A12 and Task 12.

**Test-category coverage.** Routing precedence → `test_router_precedence.py` rows 1-15;
force overrides → tests 01-07, 14 and AC-6; qualification pass/fail/uncertain →
`test_qualification.py`; task-risk floors → tests 03, 04, 12, 13 and AC-9; requested
effort → test 15 and `test_effort_changes_directives_but_not_the_profile`; source
recovery → `TestDegradationLadder` and AC-10; bounded retry →
`test_first_degradation_recovers_before_escalating` and
`test_second_degradation_escalates_exactly_one_step`; taxonomy validation →
`TestTaxonomyValidation`; canonical-source uniqueness → `TestCanonicalSourceUniqueness`;
generated-project scaffolding → `TestAC1Inheritance`, `TestAC2ProjectValidates`;
explainability → `TestExplainability`, `TestAC13andAC14Explainability`; observation
invalidation → `TestLookup.test_invalidated_when_the_contract_changes` and AC-12.

**No cross-task test dependencies.** Every task's tests pass when that task is complete.
Tasks 6 and 8 assert against synthetic fixtures built in scratch repositories
(`_support.temp_repo`, `_support.write_skill`, `CheckTestCase.add_topic`) rather than
against real skills or real topics, so no test waits on a later task and no
`@unittest.expectedFailure` appears anywhere. Tasks 10 and 11 are consequently pure
documentation migrations, and Task 10's topic promotion is the pattern each later dedupe
repeats: remove the duplication, promote the entry, in one change.

**Naming consistency.** `resolve()`, `Decision`, `Environment`, `Task`, `Lookup`,
`Outcome`, `Skill`, `Result`, `validate()`, `pack()`, `score()`, `build()`,
`classify_risk()`, `file_digest()`, `contract_fingerprint()`, `record_event()`,
`record_qualification()` and `recovery_source()` are each defined once and used with the
same signature throughout. Profile names are always `lean`/`standard`/`guarded`; layer
names always use `failure_modes` in metadata and `failure-modes.md` on disk, bridged by
`skills.LAYER_FILES`.
