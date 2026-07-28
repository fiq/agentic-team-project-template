# PR Review: Portable Context Router (Second Pass)

Two independent reviews of PR #5 (`feat/portable-context-router`, 42 commits,
`76f86db..2bc49e2`), conducted after the first review's findings were addressed.

---

## Review 1: Build correctness and architecture (second pass)

### Verdict: approve for merge

The first review found one blocking issue (B1: `ROOT = Path.cwd()`) and two
minor issues (B2, B3). All three are fixed. The second pass finds no new
blocking issues.

### What was fixed since the first review

- **B1 (fixed)**: [`TEMPLATE_ROOT`](.agentic-template/bin/context:27) is now
  resolved from the script's own location. The scaffold uses `TEMPLATE_ROOT`
  for source paths; `ROOT` (cwd) remains for project-level commands. Correct.
- **B2 (fixed)**: The scaffold's facade note now prints the exact line:
  `"context": [[str(BIN / "context")]],`. Actionable.
- **B3 (fixed)**: `context-test` exists and is back in `SCAFFOLD_COPY`.
- **D3 (fixed)**: Scaffold summarises by default, `--verbose` for full list.
- **D4 (fixed)**: Scaffold creates a minimal `project` facade when one doesn't
  exist, with `chmod 0o755`.
- **context-test is self-contained**: resolves repo root and PYTHONPATH from
  its own location. No manual env vars needed. Works from any cwd.
- **Nix flake check**: `context-router-tests` check added, runs the full suite.

### New findings (second pass)

**Finding B4 — `context-test` uses `__import__("os")` inline (Minor)**

[`context-test`](.agentic-template/bin/context-test:23) uses
`env = dict(__import__("os").environ)` instead of `import os` at the top.
This works but is unconventional. Not blocking — it's a one-liner in a
script that's unlikely to grow.

**Finding B5 — CI runs `self-test` which is slow (Minor)**

The CI workflow now runs `project self-test`, which includes the full 177-test
context router suite plus all the repo-contract fixture tests. This is correct
but adds ~10s to CI. Not blocking — it's the richest suite and it was
previously unreachable.

**Finding B6 — `check-wiki` warns about knowledge drift (Expected)**

`check-wiki` reports "knowledge changed after the wiki was last updated" —
this is expected because INBOX-009 was just added. The wiki-tidy skill should
be run to update the wiki's knowledge-changed timestamp. Not blocking — it's
a warning, not an error.

### Architecture assessment

- **Provider isolation**: preserved. No provider-specific paths merged.
- **Purity**: `resolve()` is pure; I/O is at the boundary layer.
- **Testability**: 177 tests, 22 acceptance scenarios, adversarial qualification.
- **Reversibility**: every change is a small, named commit. The scaffold is
  dry-run-by-default. Project-owned files are never touched.
- **Idempotency**: the scaffold is safe to re-run; it reports `unchanged` for
  files that match and `update` for those that differ.

### Recommendation: merge.

---

## Review 2: Developer experience and adoption (second pass)

### Verdict: approve for merge

The first review found two important issues (D1: undocumented existing-project
path, D2: no MCP statement) and two minor issues (D3, D4). All four are fixed.
The second pass finds no new blocking issues.

### What was fixed since the first review

- **D1 (fixed)**: README now has a "Using the context router in an existing
  project" section with a 5-step guide and a minimal project facade.
- **D2 (fixed)**: context-router page now states "Not an MCP server" with
  reasoning.
- **D3 (fixed)**: scaffold summarises by default.
- **D4 (fixed)**: scaffold installs a minimal facade when one doesn't exist.

### New findings (second pass)

**Finding D5 — the README's existing-project section doesn't mention `--verbose` (Trivial)**

The README's scaffold example uses `--apply` but doesn't mention `--verbose`.
A user who wants to see what will change before applying would need to read
the help text. Not blocking — the dry-run (default) already shows the summary.

**Finding D6 — the context-router page's "Related" section links to `.agents/context/README.md` which now exists (Good)**

The first review noted this link might be broken. It's not — the file was
created in Task 15. No action needed.

**Finding D7 — INBOX-009's `relates_to` doesn't link to the decisions in PROJECT_PROFILE.toon (Minor)**

INBOX-009 links to INBOX-003 and INBOX-008 but not to the four decisions it
informed (`portable_context_router`, `capability_by_observation_not_registry`,
`wiki_method_product_axis`, `yaml_skill_frontmatter_deviation`). The knowledge
graph would be more connected if it did. Not blocking — the decisions are
recorded in PROJECT_PROFILE.toon and the handoff cites INBOX-009.

### DX assessment

- **Discoverability**: the router is linked from README, docs map, docs README,
  startup, AGENTS.md, and the wiki index. Six entry points.
- **Approachability**: the wiki index explains the method/product split in
  plain language with a "New here?" pointer. The context-router page has a
  one-line intro before diving into reasoning.
- **Navigability**: every page cross-links. No dead-ends.
- **Honesty**: the reasoning page states what the router is not (not a model
  registry, not a benchmark, not an MCP server, not host auto-memory).
- **Portability**: the scaffold works from any cwd, creates a facade when
  needed, and the test runner is self-contained.

### Recommendation: merge.

---

## Summary

| Area | First review | Second pass | Verdict |
|---|---|---|---|
| Build correctness | B1 blocking, B2/B3 minor | All fixed; B4/B5/B6 minor | Approve |
| Test coverage | Strong (164 tests) | Stronger (177 tests, 22 ACs) | Approve |
| Provider isolation | Preserved | Preserved | Approve |
| DX — template path | Well-documented | Unchanged | Approve |
| DX — existing project | D1 important | Fixed | Approve |
| DX — MCP | D2 confirmed | Fixed | Approve |
| DX — scaffold output | D3 minor | Fixed | Approve |
| DX — fixture facade | D4 minor | Fixed | Approve |
| DX — knowledge graph | Not reviewed | D7 minor (not blocking) | Approve |

**Both reviews recommend merge.** No blocking findings remain. The minor
findings (B4, B5, B6, D5, D7) can be addressed in follow-up work.
