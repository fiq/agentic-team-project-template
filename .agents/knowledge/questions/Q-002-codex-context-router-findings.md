---
id: Q-002-codex-context-router-findings
title: Codex review findings on context router (PR #5)
status: open
type: question
summary: Seven Codex review findings on the context router code; all addressed in this PR.
relates_to:
  - INBOX-009-portable-context-router
---

# Codex Review Findings on Context Router

Codex reviewed commit `2bc49e2` on PR #5 and raised 7 inline findings. All
are against the context router code, not the shift-left pipeline changes.

## P1 — Register the scaffolded qualification skill

When the scaffold is applied to an existing project, its catalog may lack
`context_qualification`, but the scaffold copies the `SKILL.md`. The next
`context check` then fails because every installed skill must be catalogued.

**Fix:** merge the required entry into an existing catalog or create a starter
catalog so the router-only adoption path works without manual repair.

**File:** `.agentic-template/bin/context` (scaffold command)

## P2 — Derive escalation from the active profile

For the common unqualified environment, `context explain` starts at
`standard`, but a user following the documented recovery flow without
supplying the optional flag records the second degradation relative to `lean`.
The stored escalation is therefore only `standard`, so the post-retry plan
does not add any context.

**Fix:** derive the current profile or require it instead of silently
defaulting to `lean`.

**File:** `.agentic-template/bin/context`

## P2 — Invalidate observations when qualification changes

After a model records a passing qualification, changing `QUALIFICATION.toon`
or any fixture evidence leaves the fingerprint unchanged, so `lookup()`
continues treating the obsolete pass as current.

**Fix:** include the qualification contract and fixture in the fingerprint or
explicitly validate their version.

**File:** `.agentic-template/lib/environment.py`

## P2 — Verify actual context dispatch in existing facades

When an existing project facade merely mentions `context` in a comment or
unrelated command such as `context-packet`, the substring test suppresses the
wiring warning even though `project context` remains unavailable.

**Fix:** inspect the actual dispatch table or execute a bounded help probe
rather than searching arbitrary text.

**File:** `.agentic-template/bin/context`

## P2 — Keep qualification citations inside the fixture

A submitted `source` or `recovered_from` can be an absolute path or traverse
out of the fixture, such as `../../../answers.toon`. A directory claim also
reaches `read_text()` and crashes scoring.

**Fix:** resolve the candidate, require containment under the fixture, and
require a regular file.

**File:** `.agentic-template/lib/qualification.py`

## P2 — Scope wiki-axis checks to projects that adopt the layout

When the portable scaffold is installed into an existing project that already
has a conventional root page such as `docs/wiki/operations.md`, the advertised
`context check` fails solely because that unrelated documentation was not
migrated into the template's method/product layout.

**Fix:** make axis enforcement opt-in or scaffold a migration before treating
legacy pages as errors.

**File:** `.agentic-template/bin/context`

## P2 — Preserve empty containers at the head of list maps

When a TOON document contains a list-map whose first field is an empty map or
list, the writer emits it through `_emit_scalar`, producing quoted `"{}"` or
`"[]"`. Loading the emitted document then returns a string rather than the
original container.

**Fix:** handle empty containers structurally so the writer's claimed
round-trip behavior holds for valid control data.

**File:** `.agentic-template/lib/toon.py`

## Scope

These findings are against the context router thin slice, not the shift-left
pipeline changes (commits `c1d8f98`, `d041e9e`). They should be addressed in a
follow-up branch, not blocked on the shift-left pipeline merge.
