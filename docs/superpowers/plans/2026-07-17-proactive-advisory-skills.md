# Proactive Advisory Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three narrow, instructional coordination skills — `loop-engineering-advisory`, `specialist-recruitment-advisory`, `context-hygiene-advisory` — that fire proactively during any workflow, register them in the catalog and repo contract, document an optional `loop_state` handoff field, and update the README skill tables.

**Architecture:** These are pure judgment/instruction skills (frontmatter + concise markdown), the same shape as the existing `coordination/team-selection` and `coordination/agent-team-fallback` skills. No new `.agentic-template/bin/` script is added — validation is presence and frontmatter checks only, via the existing `check-repo-contract`.

**Tech Stack:** Markdown `SKILL.md` files, TOON catalog/schema entries, no code.

## Global Constraints

Copied verbatim from `docs/superpowers/specs/2026-07-17-proactive-advisory-design.md`. Every task's requirements implicitly include this section.

- These are judgment/instruction skills, not deterministic checks — no new `.agentic-template/bin/` script.
- New `SKILL.md` files MUST start with `---\n` frontmatter containing `name:` and `description:` lines (validated by `check-repo-contract`'s `check_skill_frontmatter`).
- No new `self-test` fixtures: validated by `check-repo-contract` presence + frontmatter checks only, matching how the other coordination skills are tested today.
- `loop_state` in `HANDOFF.toon` is optional and present only while a fallback loop is active; it must not become a required field (`check-handoff` must keep passing on the template's baseline `HANDOFF.toon`, which has no `loop_state` block).
- Never assume `/loop`-style tooling or `superpowers:subagent-driven-development` is available — the fallback must work standalone.
- Out of scope: any change to `team-selection`, `agent-team-fallback`, `handoff-maintenance` beyond a one-line cross-reference, and any change to the `research-driven-specialise` branch.

---

## File Structure

New files:
- `.agents/skills/coordination/loop-engineering-advisory/SKILL.md`
- `.agents/skills/coordination/specialist-recruitment-advisory/SKILL.md`
- `.agents/skills/coordination/context-hygiene-advisory/SKILL.md`

Modified files:
- `.agents/skills/CATALOG.toon` — three entries after the `agent_team_fallback:` entry.
- `.agentic-template/bin/check-repo-contract` — three paths added to `REQUIRED_SKILLS`.
- `.agents/schemas/handoff.schema.md` — one documented optional field.
- `README.md` — Coordination row in the skill-categories table (line 215) and three rows in the Coordination skills table (after line 284).

---

## Task 1: Loop-engineering-advisory skill

This is the first of three near-identical "write skill, register, verify" iterations (Tasks 1-3) — a loop-engineering candidate in its own right. Each iteration is independently verifiable via `repo-check`; no orchestration tooling is required to run them in sequence since each is fully self-contained.

**Files:**
- Create: `.agents/skills/coordination/loop-engineering-advisory/SKILL.md`
- Modify: `.agents/skills/CATALOG.toon:74-76` (insert after `agent_team_fallback`)
- Modify: `.agentic-template/bin/check-repo-contract:83` (insert after `"coordination/agent-team-fallback",`)

**Interfaces:**
- Produces: skill registered at catalog key `loop_engineering_advisory`, path `coordination/loop-engineering-advisory/SKILL.md`. No other task consumes this directly; it is a leaf skill.

- [ ] **Step 1: Add the failing repo-contract expectation**

In `.agentic-template/bin/check-repo-contract`, in `REQUIRED_SKILLS`, add after line 83 (`"coordination/agent-team-fallback",`):

```python
    "coordination/loop-engineering-advisory",
```

- [ ] **Step 2: Run repo-check to verify it fails**

Run: `.agentic-template/bin/project repo-check`
Expected: FAIL — `REPO CONTRACT FAILED` listing `missing skill coordination/loop-engineering-advisory`.

- [ ] **Step 3: Create the skill file**

Create `.agents/skills/coordination/loop-engineering-advisory/SKILL.md`:

`````markdown
---
name: loop-engineering-advisory
description: Notice bounded, repeatable TDD-shaped work and recommend running it as an explicit N-iteration loop.
---

# Loop-Engineering Advisory

## Outcome

Work that is safely decomposable into bounded, independently-verifiable,
test-driven iterations gets surfaced as a recommendation, not executed
silently as one large undifferentiated pass.

## When to advise

The current task is the same sub-pattern repeated N times, where each
repetition is:

- independently testable (has its own pass/fail signal);
- low blast radius (a bad iteration is easy to revert or redo alone);
- structurally identical to its neighbours (e.g. "write one skill file,
  register it, verify" repeated per skill).

## What to recommend

1. Prefer real loop-orchestration tooling when present in the current
   harness: a `/loop`-style skill, or `superpowers:subagent-driven-development`
   / `superpowers:executing-plans`. Never assume either is available.
2. When no such tooling exists, use a deterministic on-disk fallback instead
   of skipping the discipline: track progress in an optional `loop_state:`
   block in `HANDOFF.toon`:

   ```toon
   loop_state:
     plan: docs/superpowers/plans/<plan-file>.md
     task: "Task 3: consult skill cluster"
     iteration: 2
     of: 4
     last_step_completed: "run self-test, passed"
     next_step: "write consult/repo-topology/SKILL.md"
   ```

   This block is optional and present only while a fallback loop is active;
   remove it once the loop completes. It exists so the loop survives context
   resets, session restarts, or a model/provider swap mid-loop.
3. Surface the recommendation and the chosen mechanism explicitly; let the
   human or lead agent confirm before iterating. Do not silently batch the
   work into one large step.

## Do not

- Assume `/loop` or Superpowers subagent tooling is present.
- Leave a stale `loop_state:` block in `HANDOFF.toon` after the loop
  completes.
- Use this skill to justify skipping per-iteration verification.
`````

- [ ] **Step 4: Register the skill in the catalog**

In `.agents/skills/CATALOG.toon`, insert after line 76 (the `agent_team_fallback` `trigger:` line, before the blank line at 77):

```toon

  loop_engineering_advisory:
    path: coordination/loop-engineering-advisory/SKILL.md
    trigger: repeating_bounded_subtask_pattern_detected
```

- [ ] **Step 5: Run repo-check to verify it passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK`.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/coordination/loop-engineering-advisory .agents/skills/CATALOG.toon .agentic-template/bin/check-repo-contract
git commit -m "feat: add loop-engineering-advisory coordination skill"
```

---

## Task 2: Specialist-recruitment-advisory skill

Second loop iteration — same pattern as Task 1.

**Files:**
- Create: `.agents/skills/coordination/specialist-recruitment-advisory/SKILL.md`
- Modify: `.agents/skills/CATALOG.toon` (insert after the `loop_engineering_advisory` entry added in Task 1)
- Modify: `.agentic-template/bin/check-repo-contract` (insert after `"coordination/loop-engineering-advisory",` added in Task 1)

**Interfaces:**
- Consumes: nothing from Task 1 (independent leaf skill); relies on `coordination/team-selection` existing (it does — see `.agents/skills/coordination/team-selection/SKILL.md`) for the hand-off it documents.
- Produces: skill registered at catalog key `specialist_recruitment_advisory`.

- [ ] **Step 1: Add the failing repo-contract expectation**

In `.agentic-template/bin/check-repo-contract`, in `REQUIRED_SKILLS`, add immediately after the `"coordination/loop-engineering-advisory",` line from Task 1:

```python
    "coordination/specialist-recruitment-advisory",
```

- [ ] **Step 2: Run repo-check to verify it fails**

Run: `.agentic-template/bin/project repo-check`
Expected: FAIL — `missing skill coordination/specialist-recruitment-advisory`.

- [ ] **Step 3: Create the skill file**

Create `.agents/skills/coordination/specialist-recruitment-advisory/SKILL.md`:

```markdown
---
name: specialist-recruitment-advisory
description: Notice mid-task when a specific specialist would materially help and offer it explicitly, instead of proceeding solo.
---

# Specialist-Recruitment Advisory

## Outcome

A task that matches a known specialist domain gets an explicit offer of
help — "would you like [named specialist] to assist with this?" — instead
of being handled solo by default or only escalated when the user happens to
name a specialist first.

## When to advise

Mid-task, not just at kickoff, notice that the current work matches a
specialist domain and no matching specialist has been engaged yet:

- a code change is about to be reviewed -> code-review specialist;
- a security- or privacy-sensitive change is in play -> security-review
  specialist;
- the task requires sweeping many files or directories for a conclusion,
  not full file review -> a broad-exploration agent;
- an irreversible or contested architectural decision is on the table ->
  an architecture-challenger role or `coordination/adversarial-debate`.

## What to do

1. Name the specific specialist and ask explicitly, as its own offer, before
   proceeding — do not bury the offer inside an unrelated question.
2. If accepted, hand off to
   [`coordination/team-selection`](../team-selection/SKILL.md) for the
   actual role and ownership mechanics; this skill only owns the tripwire
   and the ask, not the roster.
3. If declined, proceed solo and do not ask again for the same decision
   point in the same task.

## Do not

- Duplicate `team-selection`'s role-selection procedure.
- Ask about every possible specialist for every task — only where the task
  genuinely matches a domain and none has been engaged.
- Proceed solo on a specialist-shaped task without surfacing the offer at
  least once.
```

- [ ] **Step 4: Register the skill in the catalog**

In `.agents/skills/CATALOG.toon`, insert immediately after the `loop_engineering_advisory` entry added in Task 1:

```toon

  specialist_recruitment_advisory:
    path: coordination/specialist-recruitment-advisory/SKILL.md
    trigger: task_matches_specialist_domain_and_none_engaged
```

- [ ] **Step 5: Run repo-check to verify it passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK`.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/coordination/specialist-recruitment-advisory .agents/skills/CATALOG.toon .agentic-template/bin/check-repo-contract
git commit -m "feat: add specialist-recruitment-advisory coordination skill"
```

---

## Task 3: Context-hygiene-advisory skill

Third loop iteration — same pattern as Tasks 1-2.

**Files:**
- Create: `.agents/skills/coordination/context-hygiene-advisory/SKILL.md`
- Modify: `.agents/skills/CATALOG.toon` (insert after the `specialist_recruitment_advisory` entry added in Task 2)
- Modify: `.agentic-template/bin/check-repo-contract` (insert after `"coordination/specialist-recruitment-advisory",` added in Task 2)

**Interfaces:**
- Consumes: nothing from Tasks 1-2 (independent leaf skill); cross-references `workflow/handoff-maintenance` (exists at `.agents/skills/workflow/handoff-maintenance/SKILL.md`) without duplicating it.
- Produces: skill registered at catalog key `context_hygiene_advisory`.

- [ ] **Step 1: Add the failing repo-contract expectation**

In `.agentic-template/bin/check-repo-contract`, in `REQUIRED_SKILLS`, add immediately after the `"coordination/specialist-recruitment-advisory",` line from Task 2:

```python
    "coordination/context-hygiene-advisory",
```

- [ ] **Step 2: Run repo-check to verify it fails**

Run: `.agentic-template/bin/project repo-check`
Expected: FAIL — `missing skill coordination/context-hygiene-advisory`.

- [ ] **Step 3: Create the skill file**

Create `.agents/skills/coordination/context-hygiene-advisory/SKILL.md`:

```markdown
---
name: context-hygiene-advisory
description: Notice when the main thread's context is growing heavy or a natural task boundary is reached, and recommend delegating or clearing.
---

# Context-Hygiene Advisory

## Outcome

A session that is accumulating heavy context, or has just reached a natural
boundary, gets a proactive recommendation to protect focus — rather than
silently continuing to build on an increasingly long transcript.

## When to advise

- The main thread has accumulated large tool output (broad file reads,
  long exploration, big diffs) that a subagent could have absorbed instead.
- A natural boundary has just been reached: a plan was committed, a PR was
  merged, an investigation concluded, or a bounded issue's work is done.

## What to recommend

1. For the next bounded unit of work, recommend delegating to a subagent or
   an isolated worktree (see `CLAUDE.md` worktree rules) rather than
   continuing to grow the current thread.
2. At a natural boundary, recommend clearing context or starting a fresh
   session before beginning the next unit.
3. State the recommendation plainly and let the human or lead agent decide;
   do not clear or delegate unilaterally without saying so.

## Relationship to other skills

- [`workflow/handoff-maintenance`](../../workflow/handoff-maintenance/SKILL.md)
  keeps `HANDOFF.toon` itself lean; this skill is about the live
  conversation's context, not the persisted handoff file. Use both together
  rather than treating either as covering the other.
- Worktree rules in `AGENTS.md` govern isolation between agents; this skill
  is the trigger that suggests reaching for that isolation, not a
  replacement for it.

## Do not

- Clear context or spawn a subagent silently without telling the user.
- Duplicate `handoff-maintenance`'s include/exclude rules for `HANDOFF.toon`
  content.
```

- [ ] **Step 4: Register the skill in the catalog**

In `.agents/skills/CATALOG.toon`, insert immediately after the `specialist_recruitment_advisory` entry added in Task 2:

```toon

  context_hygiene_advisory:
    path: coordination/context-hygiene-advisory/SKILL.md
    trigger: context_growing_or_natural_task_boundary_reached
```

- [ ] **Step 5: Run repo-check to verify it passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK`.

- [ ] **Step 6: Commit**

```bash
git add .agents/skills/coordination/context-hygiene-advisory .agents/skills/CATALOG.toon .agentic-template/bin/check-repo-contract
git commit -m "feat: add context-hygiene-advisory coordination skill"
```

---

## Task 4: Document the optional `loop_state` handoff field

**Files:**
- Modify: `.agents/schemas/handoff.schema.md` (30 lines total)

**Interfaces:**
- Consumes: the `loop_state:` shape documented in Task 1's skill file (must match exactly).
- Produces: no code interface; documentation only.

- [ ] **Step 1: Add the optional field to the schema doc**

In `.agents/schemas/handoff.schema.md`, insert a new section after the closing "Prefer knowledge IDs over copied content." line (currently the last line, line 30):

`````markdown

## Optional: loop_state

While a `coordination/loop-engineering-advisory` fallback loop is active
(no `/loop`-style tooling or `superpowers:subagent-driven-development`
available), `HANDOFF.toon` may additionally carry:

```toon
loop_state:
  plan: docs/superpowers/plans/<plan-file>.md
  task: "<task name>"
  iteration: <current iteration number>
  of: <total iterations>
  last_step_completed: "<short description>"
  next_step: "<short description>"
```

This block is optional. Remove it once the loop completes; do not leave it
as stale state after the last iteration.
`````

- [ ] **Step 2: Verify `check-handoff` still passes on the template's baseline `HANDOFF.toon`**

Run: `.agentic-template/bin/project check-handoff`
Expected: `HANDOFF OK` (the field is documentation-only; `check-handoff` validates required-section presence, not a fixed schema, so no script change is needed and the check must still pass with no `loop_state` block present).

- [ ] **Step 3: Commit**

```bash
git add .agents/schemas/handoff.schema.md
git commit -m "docs: document optional loop_state handoff field"
```

---

## Task 5: README skill tables

**Files:**
- Modify: `README.md:215` (skill-categories table, Coordination row)
- Modify: `README.md` (Coordination skills table, after line 284)

**Interfaces:**
- Consumes: the three skills created in Tasks 1-3 and their catalog triggers.
- Produces: no code interface; documentation only.

- [ ] **Step 1: Update the skill-categories table**

In `README.md`, change line 215 from:

```markdown
| Coordination | `team-selection`, `sudo`, `adversarial-debate`, `agent-team-fallback` | Select agent roles, switch personas, debate decisions, degrade gracefully |
```

to:

```markdown
| Coordination | `team-selection`, `sudo`, `adversarial-debate`, `agent-team-fallback`, `loop-engineering-advisory`, `specialist-recruitment-advisory`, `context-hygiene-advisory` | Select agent roles, switch personas, debate decisions, degrade gracefully, and proactively advise on looping, specialist help and context hygiene |
```

- [ ] **Step 2: Add rows to the Coordination skills table**

In `README.md`, immediately after the `agent-team-fallback` row (currently line 284):

```markdown
| `loop-engineering-advisory` | [`coordination/loop-engineering-advisory/SKILL.md`](.agents/skills/coordination/loop-engineering-advisory/SKILL.md) | repeating bounded subtask pattern detected |
| `specialist-recruitment-advisory` | [`coordination/specialist-recruitment-advisory/SKILL.md`](.agents/skills/coordination/specialist-recruitment-advisory/SKILL.md) | task matches specialist domain and none engaged |
| `context-hygiene-advisory` | [`coordination/context-hygiene-advisory/SKILL.md`](.agents/skills/coordination/context-hygiene-advisory/SKILL.md) | context growing or natural task boundary reached |
```

- [ ] **Step 3: Verify no whitespace regressions**

Run: `git diff --check`
Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: list new advisory skills in README skill tables"
```

---

## Final verification

After all tasks:

- [ ] Run `.agentic-template/bin/project repo-check` — expect `REPO CONTRACT OK`.
- [ ] Run `.agentic-template/bin/project check` — expect all checks pass.
- [ ] Run `.agentic-template/bin/project self-test` — expect `SELF TEST OK` (no new fixtures added, so this only confirms no regression).
- [ ] Run `git diff --check` — expect clean.
- [ ] Update `HANDOFF.toon` to record delivery state and open a PR; human or lead agent owns merge.
