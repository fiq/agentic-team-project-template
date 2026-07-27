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
