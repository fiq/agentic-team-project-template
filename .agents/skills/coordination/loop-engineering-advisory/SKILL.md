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
