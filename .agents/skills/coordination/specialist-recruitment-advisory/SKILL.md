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
