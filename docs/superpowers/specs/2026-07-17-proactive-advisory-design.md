# Proactive Advisory Skills

Date: 2026-07-17
Status: approved

## Goal

Give agents working in this template three narrow, proactive advisory
behaviours that fire during any workflow, not just at team kickoff:

1. Notice when work is safely decomposable into a bounded, repeatable
   test-driven loop and recommend it (with a deterministic fallback when no
   loop-orchestration tooling is available).
2. Notice when a specific specialist would materially help and explicitly
   offer it, instead of quietly doing everything solo.
3. Notice when the main thread's context is growing heavy or a natural task
   boundary has been reached, and recommend delegating or clearing.

These are judgment/instruction skills, not deterministic checks — they
follow the same shape as the existing `coordination/team-selection` and
`coordination/agent-team-fallback` skills.

## Scope

- Three new skills under `.agents/skills/coordination/`:
  `loop-engineering-advisory`, `specialist-recruitment-advisory`,
  `context-hygiene-advisory`.
- `CATALOG.toon` entries with triggers for all three.
- `check-repo-contract` registration (presence + frontmatter validation
  only — no new deterministic behaviour to test).
- An optional `loop_state:` block documented in
  `.agents/schemas/handoff.schema.md` for the loop-engineering fallback.
- README skill-category table and full skill-list table updated.

Out of scope: any new `.agentic-template/bin/` script, any change to
`team-selection`, `agent-team-fallback`, or `handoff-maintenance` beyond
cross-references, and any change to the `research-driven-specialise` branch
(separate bounded issue, not touched here).

## Skills

### coordination/loop-engineering-advisory

Trigger: `repeating_bounded_subtask_pattern_detected`.

- Notice when current work is the same sub-pattern repeated N times, each
  iteration independently testable and low-risk to hand off (e.g. "write one
  skill file, register it, verify" x4).
- Recommend real loop-orchestration tooling when present: a `/loop`-style
  skill, or `superpowers:subagent-driven-development` / `executing-plans`.
  Never assume either is available.
- Deterministic fallback when no such tooling exists: track loop progress in
  an on-disk `loop_state:` block in `HANDOFF.toon`:

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
  resets, session restarts, or a model/provider swap mid-loop, consistent
  with the existing "Team and model fallback" recording discipline in
  `AGENTS.md`.
- Advise, don't silently execute: surface the recommendation (tooling choice
  or fallback) and let the human or lead agent confirm before iterating.

### coordination/specialist-recruitment-advisory

Trigger: `task_matches_specialist_domain_and_none_engaged`.

- Notice mid-task — not just at kickoff — that a specific specialist
  (code-review, security-review, deep research/broad exploration,
  architecture challenge) would materially help and none has been engaged.
- Ask explicitly: "would you like [named specialist] to assist with this?"
  rather than proceeding solo or waiting to be asked by name.
- Distinct from `team-selection`: that skill builds the roster once a team
  is starting. This skill is the earlier tripwire that triggers considering
  a specialist mid-flight. On acceptance, hand off to `team-selection` for
  the actual role mechanics.

### coordination/context-hygiene-advisory

Trigger: `context_growing_or_natural_task_boundary_reached`.

- Notice when the main thread's context is accumulating heavy tool output,
  or a natural boundary has been reached (a plan committed, a PR merged, an
  investigation concluded).
- Recommend delegating the next bounded unit of work to a subagent or
  worktree to protect the main context, or recommend clearing/starting
  fresh.
- Complements `workflow/handoff-maintenance` (keeps `HANDOFF.toon` itself
  lean) and the existing worktree rules in `AGENTS.md`; does not duplicate
  either.

## Registration

- `CATALOG.toon` gains three entries with the triggers above, following the
  existing `coordination_*` naming pattern.
- `check-repo-contract` `REQUIRED_SKILLS` gains the three new skill paths;
  existing frontmatter validation applies automatically.
- `.agents/schemas/handoff.schema.md` gains one documented optional field:
  `loop_state` (present only while a fallback loop is active).

## Documentation updates

- README's "Skill categories" table: add the three skills to the
  Coordination row.
- README's "Full skill list" Coordination sub-table: add rows for all three
  with path and trigger.
- No `AGENTS.md` command-table change (these are not `project` commands).

## Testing rationale

Consistent with the existing coordination skills, these are pure judgment
skills validated by presence and frontmatter checks in
`check-repo-contract`, not by behavioural `self-test` fixtures — there is no
deterministic script output to assert. The `loop_state` schema addition is
documentation only; `check-handoff` already validates by required-section
presence, not strict schema, so no script change is needed there.
