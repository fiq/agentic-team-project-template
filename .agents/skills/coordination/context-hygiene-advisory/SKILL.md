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
