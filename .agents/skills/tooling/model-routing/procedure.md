# Model Routing — Procedure

## Handoff protocol

Before changing model or provider:

1. update `HANDOFF.toon`;
2. record fixed decisions;
3. record unresolved ambiguity;
4. preserve test results;
5. record branch, worktree and commit state;
6. create a `context-packet` sized to the target context window;
7. identify safe bounded next work.

## When to escalate

Escalate when:

- architecture assumptions conflict;
- public contracts change;
- tests repeatedly fail;
- security or privacy risk appears;
- reviewers disagree;
- the task can no longer be safely bounded.
