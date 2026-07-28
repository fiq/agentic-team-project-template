# Review: Portable Context Router — Build and DX

Two independent reviews of the context-router work (Tasks 1-13, commits
`76f86db..654759f` on `feat/portable-context-router`).

---

## Review 1: Build correctness and architecture

### Verdict: sound, with three findings to address before merge

The context router is well-structured: a pure library layer (`toon.py`,
`router.py`, `skills.py`, `plan.py`, `qualification.py`, `observations.py`,
`environment.py`) with no I/O in the resolution path, a thin command layer
(`bin/context`), and a fixture-scored qualification system that is genuinely
unguessable. The test suite (164 tests) is strong on contract coverage. The
scaffold is dry-run-by-default, respects project-owned files, and the generated
fixture proves the inheritance works end-to-end.

### Finding B1 — `ROOT = Path.cwd()` is fragile (Important)

[`context`](.agentic-template/bin/context:23) sets `ROOT = Path.cwd()`. Every
command — `explain`, `check`, `qualify`, `scaffold` — depends on the caller
being in the repo root. This is correct when invoked through
`project context <subcommand>` (the `project` facade runs from the repo root),
but:

- The scaffold test calls `scaffold_into(self.project)` with `cwd=ROOT` — so
  `ROOT` is the template repo, and the target is `self.project`. This works,
  but only because the test knows to set `cwd=ROOT`. A user running
  `project context scaffold --into ../other-project` from a subdirectory would
  get `ROOT` pointing at the subdirectory, not the repo root.
- The `cmd_check` function calls `validate(ROOT)` — if `ROOT` is wrong, the
  check scans the wrong directory.

**Recommendation**: resolve `ROOT` from the `context` script's own location
(`ROOT = Path(__file__).resolve().parents[1]`), not from `cwd()`. The `project`
facade already handles `cwd` correctly; the context bin should not depend on it.

### Finding B2 — scaffold does not preserve executable bit on `context` (Important)

[`cmd_scaffold`](.agentic-template/bin/context:410) uses `shutil.copy2` for
files, which preserves permissions. But the fixture's `project` facade is
created with `chmod +x` in the fixture, not by the scaffold. When the scaffold
copies `bin/context` to a target project, the executable bit is preserved
(because `copy2` preserves mode). However, the fixture's `project` facade is
part of the fixture, not scaffolded — a real project that doesn't already have
a `project` facade won't get one from the scaffold. The scaffold prints a note
if the facade doesn't dispatch `context`, but doesn't offer to fix it.

**Recommendation**: this is acceptable for now (the scaffold is explicitly
"install the router", not "install the project facade"), but the note should
be more actionable: print the exact line to add, not just "add a 'context'
entry to its COMMANDS table."

### Finding B3 — `context-test` removed from `SCAFFOLD_COPY` (Minor, tracked)

The plan included `.agentic-template/bin/context-test` in `SCAFFOLD_COPY`, but
it doesn't exist yet (forward reference to Task 14). I removed it to unblock
the scaffold. This is correct, but should be recorded as a follow-up so Task 14
adds it back.

### What's good

- **Provider isolation preserved**: the router, qualification, scaffold and
  taxonomy layers are all template-internal. No provider-specific paths are
  merged.
- **Test-first discipline**: every task wrote the failing test first, verified
  it failed, then implemented. The qualification fixture's defeat-score
  acceptance criterion (0 of 6 blind) is genuinely adversarial.
- **Standing guards**: the nonce-leak guard and the gating-answer-must-carry-
  the-nonce guard are automated properties, not one-time findings. Any future
  fixture edit that reintroduces guessability fails the suite immediately.
- **Scoring precedence fix**: a demonstrated failure now outranks an omission.
  The test pins it.
- **Wiki axis enforcement**: `_check_wiki_axis` is a cheap deterministic
  fitness function that catches methodology/product drift at `project check`
  time, not at review time.

---

## Review 2: Developer experience and adoption

### Verdict: strong foundation, but the adoption story has a gap

The context router is the most thoughtful piece of agent infrastructure I've
reviewed in this repo. The reasoning page
([`context-router.md`](docs/wiki/method/context-router.md)) is clear, honest
about what it is not, and cites its sources. The scaffold makes the router
portable. But the adoption story — how a user actually gets from "I have an
existing project" to "the router is working in my project" — has a gap.

### Finding D1 — three adoption paths, only one is documented (Important)

The user asked about three adoption paths:

1. **Template project** (primary): `Use this template` on GitHub → `project init`
2. **Existing project**: `project context scaffold --into .` → wire up the
   `project` facade
3. **Skills/MCP**: use the skills without the full template

Path 1 is well-documented in the README. Path 2 is the scaffold's purpose, but
the README doesn't mention it — a user with an existing project would have to
discover `project context scaffold` by reading the context bin's help text or
the plan. Path 3 is not addressed at all.

**Recommendation**: add a "Using the context router in an existing project"
section to the README, after the "Get started" section. It should cover:
- `git clone` the template, run `project context scaffold --into /your/project --apply`
- Wire up the `project` facade (or use `context` directly)
- Run `project context check` to verify

### Finding D2 — MCP does not make sense here (Confirmed)

The user asked whether MCP makes sense. It does not, for this project:

- MCP is a tool-calling protocol for agents to invoke external tools. The
  context router is not a tool — it's a file-based resolver that runs as a
  shell command. An agent doesn't "call" the router; it runs
  `project context explain` and reads the output.
- The router's value is that it's portable, versioned and reviewable in a
  pull request. Wrapping it in an MCP server would add a runtime dependency,
  a network boundary, and a failure mode, for no gain: the agent still needs
  filesystem access to read the preloaded files.
- The router already works with any agent that can read Markdown and run shell
  commands. MCP would narrow compatibility, not broaden it.

**Recommendation**: state this explicitly in the context-router reasoning page,
under "What this deliberately is not", so future readers don't re-litigate it.

### Finding D3 — the scaffold's "next" message is good but the dry-run output is noisy (Minor)

The scaffold prints every action (create/update/unchanged/keep/skip) for every
file. For a first-time user, this is 25+ lines of output before the "next"
message. The signal-to-noise ratio is low: most lines are "create" or
"unchanged", which is expected.

**Recommendation**: in dry-run mode, summarise ("12 files to create, 2 to
update, 2 starters, 2 skipped") and only print the full list with a `--verbose`
flag. In apply mode, print only what changed.

### Finding D4 — the fixture's `project` facade is too minimal for real use (Minor)

The fixture's [`project`](.agentic-template/fixtures/generated-project/.agentic-template/bin/project)
only dispatches `context`. A real generated project needs the full `project`
facade (startup, check, docs, etc.). The scaffold doesn't create one — it
expects the target to already have one, or prints a note.

This is correct for the fixture (it only tests the router), but a user
scaffolding into an existing project that has no `project` facade would get
a router they can't invoke through the canonical command surface.

**Recommendation**: the scaffold should offer to install a minimal `project`
facade that dispatches `context` when one doesn't exist, with a clear comment
that it's a starting point to extend.

### What's good for DX

- **Dry-run by default**: the scaffold writes nothing unless `--apply` is
  passed. This is the right default for a command that modifies a project.
- **The reasoning page is genuinely useful**: it explains *why* the router
  exists, not just *what* it does. A user who disagrees with the design can
  find the reasoning and the tradeoffs.
- **The wiki axis split is a real DX improvement**: methodology (inherited)
  and product (project-written) are now physically separated. A generated
  project's users don't read template operating procedure next to their own
  domain model.
- **The qualification system is honest**: it doesn't claim a model is capable
  — it proves it. The defeat-score acceptance criterion is adversarial in the
  right way.
- **The context-packet skill now has source digests**: this makes recovery
  targeted rather than wholesale, which is a real operational improvement.

---

## Summary

| Area | Verdict | Blocking? |
|---|---|---|
| Build correctness | Sound; `ROOT = Path.cwd()` is fragile | B1 should be fixed before merge |
| Test coverage | Strong (164 tests, adversarial qualification) | No |
| Provider isolation | Preserved | No |
| DX — template path | Well-documented | No |
| DX — existing-project path | Undocumented | D1 should be addressed |
| DX — MCP | Correctly not pursued | No |
| DX — scaffold output | Noisy but functional | D3 is minor |
| DX — fixture facade | Too minimal for real use | D4 is minor |

### Recommended next actions (before merge)

1. **B1**: Fix `ROOT` resolution in `bin/context` — use the script's location,
   not `cwd()`.
2. **D1**: Add an "Existing project" adoption section to the README.
3. **D2**: Add "Not an MCP server" to the context-router page's "What this
   deliberately is not" list.
4. **B3**: Record the `context-test` follow-up for Task 14.

### Recommended later actions

5. **D3**: Add a `--verbose` flag to the scaffold and summarise by default.
6. **D4**: Offer to install a minimal `project` facade when one doesn't exist.
7. **B2**: Make the scaffold's facade note more actionable (print the exact
   line to add).
