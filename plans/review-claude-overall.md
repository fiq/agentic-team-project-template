# Claude Overall Review — 2026-08-02

> **Status: all findings addressed.** This document was written as a review,
> then the owner asked for the findings to be fixed. Everything below is
> preserved as the original analysis; see
> [Second Pass](#second-pass--remaining-findings-addressed) at the end for
> what changed, including two places where acting on a finding proved the
> original recommendation wrong. Test count went 272 → 325; nothing is
> committed.

## Verdict: needs work, mostly fixed inline during this review

This review covers the shift-left pipeline, the self-extending runtime
pattern, the scaffold adoption path, secret scanning, the TOPICS.toon
duplication registry (called a "dedupe ledger" in HANDOFF.toon — renamed here;
see the note in that section), the surrounding docs/config, and a DX
value-proposition/portability pass added mid-review at the user's request.

Several findings were fixed inline (the user authorised this explicitly
mid-review) rather than only reported. Every fix was verified by re-running
the full test suite (`python3 -m unittest discover -s .agentic-template/tests`,
272 tests), `project check`, `project ready`, and `project self-test` — all
pass. **Nothing has been committed** — all changes are uncommitted working-tree
edits on `main`, left for the user to review and commit. See "Fixes Applied
During This Review" for the full file list.

The most significant finding is that `project ready`'s test for "has this
command actually been specialised yet" was structurally incapable of working
— it always evaluated true, for every project past template state, regardless
of real specialisation. It has never manifested in anger because no real
project has gone through `/specialise` with this code yet (per HANDOFF.toon's
own next-actions). Caught and fixed before the first real adopter would have
hit it.

## Focal Area Findings

### 1. Shift-left pipeline coherence

**Verdict:** needs work → fixed inline

**Findings:**

- [`.agentic-template/bin/project-ready` (pre-fix, ~line 80-135)] The
  readiness gate detected whether `test`/`lint`/`integration-test`/
  `contract-test` were specialised by parsing `project --list` output and
  checking `"lint" in specialised_commands`. But `project --list`
  (`.agentic-template/bin/project:113`) unconditionally prints
  `set(COMMANDS) | UNSPECIALISED | {"help"}` — every command name appears in
  that union whether or not it has actually been moved out of
  `UNSPECIALISED`. The check could never be false once `is_template` was
  false. Reproduced live: a simulated project with only `test` specialised
  (moved into `COMMANDS`, removed from `UNSPECIALISED`) still had `project
  ready` attempt `lint`, `integration-test` and `contract-test`, all of which
  failed with "harness not specialised" and dragged the summary to `READY:
  FAIL`. **Fixed**: `project-ready` now imports the `project` dispatcher
  module directly (`importlib.machinery.SourceFileLoader`) and checks
  membership in its real `UNSPECIALISED` set. Re-verified against the same
  simulated scenario: `lint` and `test` now correctly show as PASSED,
  `integration-test`/`contract-test` are correctly omitted (still
  unspecialised) rather than counted as FAIL.
- [`.agentic-template/bin/project-ready` (pre-fix, ~line 94-100)] Even when
  the detection above worked by chance in this repo's own template state
  (nothing runs, so nothing was exercised), `test` was queued before `lint`,
  contradicting AGENTS.md's explicit rule ("`project lint` runs before
  `project test` in CI", AGENTS.md:110 and :157) and the `ci`/`static-analysis`
  skills' pipeline diagrams. `project build` was never invoked anywhere in
  `project-ready` at all — grepped the whole `.agentic-template/bin/`
  tree to confirm. **Fixed**: reordered to lint → build → test →
  integration-test → contract-test, and added the missing build step.
- [AGENTS.md:110,157 vs `.agents/skills/specialise/ci/SKILL.md:24` and
  `.agents/skills/specialise/static-analysis/SKILL.md:134`, both pre-fix]
  AGENTS.md states lint "runs before" test as a hard, twice-repeated rule.
  Both specialise skills hedged this to "before or in parallel with" /
  "early and in parallel with" — a real contradiction about whether a lint
  failure should ever let the test suite run anyway. **Fixed**: both skills
  now say "before"; the "parallel" language was re-scoped to lint's own
  sub-categories (type-check/SAST/dependency-scan/complexity running in
  parallel with each other), which is what a CI author most plausibly meant
  and doesn't contradict the gate semantics. (An existing test,
  `test_ci_skill_mentions_parallel`, locks in the word "parallel" appearing
  somewhere in `ci/SKILL.md` — the rewritten wording satisfies it without
  reintroducing the contradiction.)
- [Broken cross-references — 7 occurrences, all pre-fix: `ci/SKILL.md:28`,
  `infra-decision/SKILL.md:61`, `container-build/SKILL.md:15`,
  `build-pipeline/SKILL.md:32,79`, `deployment-pipeline/SKILL.md:74`,
  `static-analysis/SKILL.md:135`] Every sibling cross-reference between the
  pipeline skills used a bare relative link, e.g.
  `[specialise/ci](ci/SKILL.md)` written *inside*
  `specialise/static-analysis/SKILL.md` — which resolves to
  `specialise/static-analysis/ci/SKILL.md` (doesn't exist), not
  `specialise/ci/SKILL.md`. Caught live by the editor's diagnostics on one
  instance after an unrelated edit touched that line; grepping the pattern
  found six more identical cases across the same five files. **Fixed**: all
  seven corrected to `../<skill>/SKILL.md`.
- [AGENTS.md:113-114, `static-analysis/SKILL.md:92-104`,
  `docs/wiki/method/glossary.md:29`, `CUSTOMIZE_THIS_PROJECT.toon:65` vs
  `.agentic-template/bin/install-hooks` (pre-fix)] Five places describe the
  opt-in pre-commit hook as running "a fast subset of `project lint`"; the
  actual hook only ran `project check-wiki` and never touched lint. Only
  `docs/wiki/method/development.md:53-54` matched the real (pre-fix)
  behaviour. This is the kind of gap that would embarrass the project if
  someone tried the documented feature and found it didn't do what five
  separate documents said it does. **Fixed**: `install-hooks` now also wires
  `project lint` (non-blocking, same pattern as check-wiki);
  `development.md` updated to mention both checks.

**Recommended actions:**

1. Done — fixed `project-ready`'s specialisation detection, pipeline order,
   and missing build step.
2. Done — aligned `ci`/`static-analysis` wording with AGENTS.md's "before"
   rule.
3. Done — fixed the 7 broken relative links.
4. Done — made `install-hooks` match its documentation.
5. If any real project has already run `project install-hooks` before this
   fix lands, re-running it will regenerate the hook with the lint line
   included (the installer overwrites its own previously-installed hook).

### 2. Self-extending runtime pattern

**Verdict:** needs work

**Findings:**

- [`.agents/skills/specialise/runtime-{node,elixir,godot,python}/SKILL.md`]
  Four of the eleven runtime skills (python, node, elixir, godot) contain only
  a "Language smells" section (~20 lines total). The other seven (rust, go,
  csharp, jvm, perl, ruby, php) additionally have "Build and tooling",
  "Static analysis" (with an evolvable per-runtime tool table), "Testing",
  and "Ecosystem openness" sections — the exact checklist `init/SKILL.md`
  step 10 gives for creating a *new* runtime skill. An agent told to "follow
  the pattern of the existing runtime skills" for a 12th language is handed
  two contradictory patterns; if it copies python's (previously 2nd in the
  hand-written example list), the result silently drops the static-analysis
  table and ecosystem-openness guidance that the newer skills all have.
- [`.agents/skills/init/SKILL.md:106-107`, pre-fix] The hard-coded example
  list — "Java, Python, Node/TS, Elixir, Godot, Rust, Go, C#/.NET" — was
  stale twice over: "Java" should read "JVM" (the skill was renamed to
  `runtime-jvm` and now also covers Kotlin/Scala/Clojure), and the list
  omits Perl, PHP and Ruby, which already ship as skills. **Fixed**:
  replaced the hand-maintained list with a pointer to `CATALOG.toon`, and
  pointed "follow the pattern" at `runtime-rust`/`runtime-go` specifically
  (the fullest, most representative examples) so the instruction can't go
  stale again and no longer defaults to the thin pattern.
- [`.agentic-template/tests/test_static_analysis.py`] Only rust, go and
  csharp have dedicated test classes (frontmatter validity, catalog
  registration, "not a closed list" acknowledgment). jvm, perl, ruby, php and
  the original four runtimes have none. None of the existing tests check for
  the richer sections either way — they only grep for keywords — so the
  two-tier thin/rich split above isn't something CI would ever catch or
  prevent from recurring.

**Recommended actions:**

1. Done — pointed `init/SKILL.md` at `CATALOG.toon` and the fullest examples
   instead of a hand-maintained, staleness-prone list.
2. Not applied inline (content-authoring, not a targeted fix): backfill
   Build/Static analysis/Testing/Ecosystem sections for `runtime-python`,
   `runtime-node`, `runtime-elixir`, `runtime-godot` to match the other
   seven.
3. Extend `test_static_analysis.py` with per-runtime test classes for jvm,
   perl, ruby, php, and add an assertion that checks for the "Ecosystem
   openness" and "Static analysis" headers specifically, so the thin/rich
   split can't silently reappear once (2) is done.

### 3. Scaffold adoption path

**Verdict:** needs work → mostly fixed inline

**Findings:**

- [`.agentic-template/bin/context:386`, pre-fix, inside `_scaffold_actions`]
  Every directory-type `SCAFFOLD_COPY` entry
  (`.agentic-template/fixtures/qualification-repo`,
  `.agents/context/qualification`) was reported as `update` on *every* run,
  even immediately after a clean, unmodified `--apply` — the code took
  `source.is_dir()` as sufficient reason to call it changed, without
  comparing contents. Reproduced live: scaffolding into a fresh target twice
  in a row, with zero changes in between, showed `2 update` in the second
  dry run. This only misled the reported summary (`--apply`'s actual copy via
  `shutil.copytree` is idempotent either way), but it undermines trust in
  `--verbose` dry-run output specifically for the two directories most likely
  to matter (the qualification fixture and config). **Fixed**: added a real
  recursive content comparison (`_dir_contents_match`); the second dry run
  now correctly reports `22 unchanged` with no spurious `update` entries.
- [`.agentic-template/fixtures/rust-sample-project/docs/wiki/operations.md`,
  `.agentic-template/bin/context:257-268` `_check_wiki_axis`] The Rust
  fixture's "legacy flat wiki" scenario only tests a wiki with *zero*
  method/product directories, which makes `_check_wiki_axis` skip the whole
  check (`has_axis_dirs` is False by construction — verified via `find` over
  the fixture, which has only `docs/wiki/operations.md` and nothing else
  under `docs/wiki/`). That's the easy case. The harder, more realistic case
  — a project that has *started* migrating to the method/product layout but
  still has old flat pages sitting alongside it — isn't covered: the moment
  any axis directory exists anywhere in the wiki, `_check_wiki_axis` flags
  every remaining flat page (any `.md` directly under `docs/wiki/` other than
  `index.md`) as an error. The fixture's own README claims "a flat legacy
  wiki... must not fail the axis check" — true only for the all-flat case,
  not the more common partial-migration case a real adopting project would
  actually be in.
- [`.agentic-template/bin/context:25` `ROOT = Path.cwd()`] Carried over from
  a prior review (`plans/review-build-and-dx.md`, finding B1) — confirmed
  already resolved: `TEMPLATE_ROOT` is now resolved from `__file__`
  (`.agentic-template/bin/context:29`), decoupling "where to copy scaffold
  source from" (the template) from "what to validate" (the invoking cwd /
  target project). No further action needed.

**Recommended actions:**

1. Done — fixed the directory unchanged-detection bug.
2. Add a fixture scenario (or extend the Rust fixture) with one page already
   migrated to `docs/wiki/method/` sitting alongside the existing flat
   `operations.md`, and decide + assert the intended behaviour for partial
   migration (currently unspecified and, if it were exercised, would fail).

### 4. Secret scanning

**Verdict:** needs work → partially fixed

**Findings:**

- [`.agentic-template/bin/check-secrets:23`, pre-fix] The "OpenAI-style API
  key" pattern (`\bsk-[A-Za-z0-9]{20,}\b`) does not match Anthropic keys
  (`sk-ant-api03-...`) or OpenAI's current project-scoped keys
  (`sk-proj-...`), because both embed a hyphen immediately after `sk-` and
  the character class doesn't allow it. Verified directly: both example
  formats produced `NO MATCH` against the pre-fix pattern. Notable given this
  template's whole premise is Claude/Anthropic-centric agent workflows —
  exactly the kind of key most likely to end up in a project like this one.
  **Fixed**: added two explicit patterns anchored to the real prefixes
  (`sk-ant-api\d{2}-[A-Za-z0-9_-]{20,}`, `sk-proj-[A-Za-z0-9_-]{20,}`),
  verified against synthetic keys and against a clean run on this repo
  (`SECRETS CHECK OK`).
- [`.agentic-template/bin/check-secrets:2,18,44`, docstring vs
  implementation] The docstring says "Scan tracked files for
  credential-shaped values," but the implementation walks the entire working
  tree via `Path.cwd().rglob("*")` with no git-awareness. Verified live: an
  untracked scratch file in the repo root was flagged. This means it also
  scans anything gitignored that happens to exist on disk —
  `node_modules/`, `.venv`, a developer's real local `.env` (the exact file
  the tool's own remediation message tells you to move secrets *into*) —
  which can produce noisy failures unrelated to what would actually be
  committed, and wastes time walking large ignored trees if they exist. Not
  fixed inline: switching to `git ls-files --cached --others
  --exclude-standard` changes behaviour in a way that deserves a deliberate
  decision (a real secret sitting in a gitignored `.env` arguably *should*
  still be flagged, on a "catch it before someone `git add`s it by mistake"
  theory), so this is a recommendation rather than a silent behaviour
  change.
- [`.agentic-template/bin/check-secrets:6-7`] The docstring honestly
  disclaims full-history scanning ("not a substitute for... gitleaks,
  trufflehog"). Given the repo is meant to go public, recommend a one-time
  `gitleaks detect --log-opts="--all"` (or trufflehog) pass over full git
  history at the point of making it public — this working-tree-only check
  cannot catch a secret that was committed and later removed.

**Recommended actions:**

1. Done — added Anthropic/OpenAI-project-key patterns.
2. Decide and implement: scope the scan to `git ls-files --cached --others
   --exclude-standard` (respects `.gitignore`, still catches new untracked
   files), or explicitly document why scanning the full tree is intentional.
3. Run a one-time full-history secret scan (gitleaks/trufflehog) before or at
   the point this repo is made public.

### 5. TOPICS.toon duplication registry

*(HANDOFF.toon calls this a "dedupe ledger" — renamed to "duplication
registry" here at the user's request, since "ledger" collides with an
unrelated bounded context they need to keep separate. Same recommendation
applies to the source text — see below.)*

**Verdict:** needs work → fixed

**Findings:**

- [`.agents/context/TOPICS.toon`, pre-fix; `HANDOFF.toon:59`] The five
  `candidates` entries (D1, D2, D4, D8, D9) were carried since "Phase 1" as
  "known duplications awaiting migration... they warn, they do not fail."
  Verified programmatically — using the router's own TOON parser and the
  exact `scan_roots`/`exclude`/case-insensitive matching logic
  `_check_markers` uses — that none of the five markers currently appears
  anywhere outside its own canonical file. The underlying duplication was
  already resolved at some point; the ledger entries were simply never
  promoted, so nothing currently guards against the same duplication being
  reintroduced. **Fixed**: promoted all five to the enforced `topics:` list;
  re-verified `project check` and `project context check` both still pass.
- Terminology: recommend rewording HANDOFF.toon's "Phase 1 dedupe ledger"
  risk entry to "duplication registry" — not applied inline, since
  HANDOFF.toon is active work-state the team should edit directly rather
  than have a review pass touch.

**Recommended actions:**

1. Done — promoted the five verified-resolved candidates to enforced
   `topics:` entries.
2. Reword "dedupe ledger" → "duplication registry" in HANDOFF.toon and any
   other prose referring to this mechanism.

### 6. DX value proposition and portability framing

*(Added mid-review at the user's request: make sure the docs pre-empt an
advanced agentic-tooling user asking "why is this not just a skill for my
agent?", and that the subagents/TOON/knowledge-graph story is sold clearly.)*

**Verdict:** needs work

**Findings:**

- [`README.md`] The README already carries "agent-agnostic" framing, a
  "Compatible agents" table, and a "Deliberate non-goals" line ("Coupled to a
  single agent or platform") — but nowhere does it directly answer the
  sharper, more skeptical question an advanced Claude Code user is likely to
  ask: *why is this not just a skill/CLAUDE.md I write myself?* Grepped
  README.md, AGENTS.md and the whole wiki for "why not", "lock-in", "vendor",
  "just a skill" — the only hit is `docs/wiki/method/context-router.md:64`'s
  "Why not a model registry" section, which answers a narrower, different
  objection.
- [`.agents/knowledge/TAXONOMY.md`] The knowledge graph — typed nodes
  (`DOM-`/`SYS-`/`CON-`/`ARCH-`/`ADR-`/`PAT-`/`RISK-`/`Q-`/`LRN-`/`INBOX-`/
  `CAP-`/`CHG-`), typed edges (`depends_on`/`consumes`/`produces`/
  `decisions`/`patterns`/`risks`/`supersedes`/...), and enforced referential
  integrity via `check-knowledge`/`check-changes` — is a genuinely
  distinctive feature, closer to a small, git-native, queryable knowledge
  graph than a typical project wiki. README.md's only mention of it is one
  bullet ("Knowledge forms one graph... Agents search before acting.",
  README.md:201), which undersells what TAXONOMY.md actually describes. A
  skeptical reader has to go find and read TAXONOMY.md themselves to see the
  differentiation the user wants surfaced.
- The strongest, least-articulated argument is verification: this template's
  rules are backed by *executable* checks (`project check` alone runs 9
  deterministic gates: repo-contract, project-profile, handoff, knowledge,
  changes, tooling, mcp, secrets, context), whereas a hand-written CLAUDE.md
  or a single skill file is unverified prose an agent can silently drift
  from with no way to catch it. This is implied by the feature list but
  never stated explicitly as a rebuttal to "I can just write my own
  instructions."

**Recommended actions:**

1. Add a short, direct section (in README.md, or a new
   `docs/wiki/method/why-not-a-skill.md` linked from it) answering "I
   already have a CLAUDE.md / skill — why this?" — lead with verification
   (checks are executable, not just prose an agent can forget), then the
   knowledge graph, then portability framed as a hedge against future tool
   churn rather than a today-only benefit.
2. Elevate the knowledge-graph description in README.md from one bullet to a
   short paragraph naming the shape explicitly: typed nodes, typed edges,
   enforced referential integrity, git-versioned — this is the most novel,
   least-obvious-from-a-skim feature in the template.
3. Not applied inline: this is a positioning/voice decision for the project
   owner to shape directly, not something to rewrite unilaterally during a
   code review.

## Other Findings

Covers the "also review" checklist and the public-repo leak scan.

- [AGENTS.md, 409 lines] Dense but well-organised with clear headers;
  appropriate for the "principal-level decisions" audience it explicitly
  targets. A junior developer would lean on the wiki glossary alongside it,
  which exists and is already cross-linked — no change needed.
- [README.md] Lifecycle diagram and "Get started" flow both check out
  against the actual command surface and skill catalog. The "Using the
  context router in an existing project" section is already a good, concrete
  answer to "I don't want the whole template" for the router specifically —
  see focal area 6 for where the broader pitch could go further.
- [`CUSTOMIZE_THIS_PROJECT.toon`] The new `static_analysis`/`build`/
  `deployment`/`observability`/`budget` blocks match the state shapes their
  corresponding `SKILL.md` files document. `pre_commit_hook: opt_in`
  (line 65) was the field most directly contradicted by the pre-fix
  `install-hooks` behaviour — now accurate per focal area 1's fix.
- [`PROJECT_PROFILE.toon`] The four new decisions
  (`static_analysis_from_specialise`, `nix_first_build_pipeline`,
  `deployment_pipeline_from_specialise`, `observability_from_specialise`)
  each carry reason/confidence/validation/consequence_if_changed, consistent
  with the older decisions in shape and rigor. No issues found.
- [Wiki pages: `testing.md`, `development.md`, `glossary.md`,
  `operations.md`] Terse, well-diagrammed, terminology-first — accessible to
  a reader who already has the method glossary open alongside. glossary.md's
  "Pre-commit hook" definition (line 29) was the fifth place asserting the
  (until this review's fix) incorrect lint claim; it didn't need editing
  since its definition matched the *documented* intent, which is now also
  the actual behaviour.
- [Test coverage] 272 tests, all passing throughout this review including
  after every inline fix. Two concrete gaps: (1) runtime skills beyond
  rust/go/csharp have no dedicated tests (focal area 2); (2) nothing tested
  `project-ready`'s specialisation-detection logic directly — the bug fixed
  in focal area 1 would have been caught by a test that simulates a
  partially-specialised project, and no such test exists yet. This is the
  single highest-value test gap this review found.
- [`HANDOFF.toon`] The next-actions list is accurate and reflects real,
  unclosed work (apply the pipeline to a real project via `/specialise`;
  review the new skills on a real specialisation) — nothing fabricated or
  stale found.
- [Leaked secrets / project names / IP — public-repo check] No credentials,
  private IPs, internal-confidentiality markers, or personal emails found
  beyond the expected git commit author identity (normal for any public
  repo). `HANDOFF.toon`'s own risk note about scrubbing the project name from
  `INBOX-004/005/006` appears already done — all three currently refer to
  "an existing project" generically, no name or company is present. One
  faint residual fingerprint: INBOX-004 mentions "VR runbooks" as the kind of
  domain-specific content that was deliberately *not* copied — it doesn't
  name anything, but it's a hint about the source project's domain. Low
  priority; reword only if the source project needs to stay unidentifiable
  even by category.

## Fixes Applied During This Review

All changes below are uncommitted working-tree edits on `main` — nothing has
been committed or pushed. Verified after every change with the full test
suite (272 tests, `python3 -m unittest discover -s .agentic-template/tests`),
`project check`, `project ready`, and `project self-test` — all green.

| File | Change |
|---|---|
| `.agentic-template/bin/project-ready` | Fixed specialisation-detection (import dispatcher module instead of parsing `--list`); reordered lint → build → test; added missing build step |
| `.agentic-template/bin/check-secrets` | Added Anthropic (`sk-ant-api\d{2}-`) and OpenAI project-key (`sk-proj-`) patterns |
| `.agentic-template/bin/context` | Fixed directory unchanged-detection in `_scaffold_actions` (real recursive comparison instead of always-update) |
| `.agentic-template/bin/install-hooks` | Pre-commit hook now also runs `project lint`, matching its own documentation |
| `.agents/context/TOPICS.toon` | Promoted 5 verified-resolved duplication candidates (D1/D2/D4/D8/D9) to enforced `topics:` |
| `.agents/skills/init/SKILL.md` | Replaced stale hard-coded runtime example list with a pointer to `CATALOG.toon`; pointed at rust/go as fullest examples |
| `.agents/skills/specialise/ci/SKILL.md` | Fixed "lint before test" wording; fixed 2 broken relative links |
| `.agents/skills/specialise/static-analysis/SKILL.md` | Fixed "lint before test" wording; fixed 1 broken relative link |
| `.agents/skills/specialise/build-pipeline/SKILL.md` | Fixed 2 broken relative links |
| `.agents/skills/specialise/container-build/SKILL.md` | Fixed 1 broken relative link |
| `.agents/skills/specialise/deployment-pipeline/SKILL.md` | Fixed 1 broken relative link |
| `.agents/skills/specialise/infra-decision/SKILL.md` | Fixed 1 broken relative link |
| `docs/wiki/method/development.md` | Updated pre-commit hook description to mention lint alongside wiki-drift |

Not fixed inline (recommendations only, see per-area sections above): backfill
thin runtime skills (focal area 2), runtime skill test coverage (focal area
2), partial-migration wiki fixture scenario (focal area 3), git-aware
secret-scan scoping and a one-time full-history scan (focal area 4), HANDOFF
terminology reword (focal area 5), DX/portability positioning copy (focal
area 6), `project-ready` regression test (Other Findings).

## Summary

| Area | Verdict | Blocking? |
|---|---|---|
| Shift-left pipeline coherence | needs work → fixed | No |
| Self-extending runtime pattern | needs work (partial fix; content-authoring left open) | No |
| Scaffold adoption path | needs work → mostly fixed | No |
| Secret scanning | needs work → partially fixed | No |
| TOPICS.toon duplication registry | needs work → fixed | No |
| DX value proposition & portability framing | needs work (positioning, left for owner) | No |
| AGENTS.md / README / profiles / wiki / tests / HANDOFF | sound, minor notes | No |
| Leaked secrets / project names / IP | sound | No |

---

# Second Pass — Remaining Findings Addressed

Written after the owner asked for the open findings to be fixed. Test count
went **272 → 325**. All of `project check`, `ready`, `self-test` and `hooks`
pass. Still nothing committed.

Two findings changed shape once acted on, and one new capability was added at
the owner's request mid-pass.

## Where the original review was wrong

**Partial wiki migration (focal area 3) — recommendation reversed.** The
review said a half-migrated wiki "would fail" and implied it should be
tolerated. Implementing that revealed the argument was weak: migrating a wiki
is a single mechanical change (move the pages, add frontmatter), so there is
no incremental state to protect. Tolerating a mixed tree would have forfeited
the check's actual job — catching a page later dropped in the wrong place —
in exchange for convenience during a one-commit operation that does not need
it. The rule is now strict and, more importantly, *specified*, which was the
real gap:

```
no axis directory   -> pre-adoption legacy wiki, not checked at all
any axis directory  -> adopted; every page must be migrated
```

The permissive version was written, tested, and reverted. Four states are now
covered by tests (`.agentic-template/tests/test_scaffold_acceptance.py`):
wholly flat passes, adoption-with-a-straggler fails, fully migrated passes,
wrong-axis-frontmatter fails.

**Thin runtime skills (focal area 2) — larger than reported.** The review
named four thin skills (python, node, elixir, godot). Adding a check across
all eleven found three more with partial gaps: `runtime-jvm` and
`runtime-perl` were missing Build and Testing sections, `runtime-php` was
missing Testing. All eleven now carry the full pattern.

## What was fixed

| Finding | Resolution |
|---|---|
| 4 (really 7) thin runtime skills | Backfilled Build/Static analysis/Testing/Ecosystem across python, node, elixir, godot, jvm, perl, php. Godot records `not_applicable` with reasons for sast/dependency_scan rather than inventing tools |
| No runtime skill test coverage | `TestEveryRuntimeSkillIsComplete` **discovers** runtime skills from disk rather than listing them, so a runtime added later is held to the same bar automatically |
| No `project-ready` regression test | New `test_project_ready.py` (11 tests). `select_runtime_commands` extracted as a pure function; one test documents *why* `project --list` cannot be used |
| Secret scan scanned ignored paths | Scoped to `git ls-files --cached --others --exclude-standard`; falls back to a tree walk outside a git repo. Verified across four cases: clean, untracked, gitignored, non-git |
| No full-history scan | Ran the `check-secrets` patterns over every blob in history — 759 blobs, **no findings**. The docstring now states the history limitation explicitly |
| "ledger" terminology | Reworded in `.agents/context/README.md` and `HANDOFF.toon` (owner keeps a separate `ledger` bounded context). Historical plan docs under `docs/superpowers/plans/` left as-is — they are an archival record |
| "VR runbooks" domain hint | Removed from INBOX-004 |
| No "why not just a skill" answer | New `docs/wiki/method/why-this-not-a-skill.md`, linked from the wiki index and answered directly in README |
| Knowledge graph undersold | README bullet expanded to name typed nodes, typed edges and enforced referential integrity |

## Added at the owner's request: a declarative pre-commit gate

The original hook was a fixed shell script running one check. It is now a
small system, on the brief that it stay fast, be agent-manageable, and never
bottleneck development.

`.agents/hooks.toon` (project-owned) declares the checks:

```toon
pre_commit:
  parallel: true
  default_timeout_seconds: 15
  checks:
    - id: secrets
      command: [.agentic-template/bin/project, check-secrets]
      blocking: true
      why: a leaked credential must never reach a commit
```

`.agentic-template/bin/run-hooks` executes them:

- **concurrent** — the gate costs its slowest check, not the sum. Measured at
  **0.1s** for the three shipped checks; a test asserts three 1-second sleeps
  finish in under 2.5s;
- **per-check timeouts** — a hung check reports and cannot stall a commit
  indefinitely;
- **blocking vs advisory** — secrets blocks, wiki drift advises;
- **unspecialised targets skip, not fail** — so the template's unwired `lint`
  does not break commits before `/specialise`;
- **declaration-order output** — reproducible regardless of finish order;
- **no reinstall on edit** — the hook delegates to the config.

Verified end-to-end in a scratch repo: a clean commit succeeded, and a commit
carrying a planted AWS key was **blocked**, with `git log` confirming it never
landed. Exposed as `project hooks` so agents can run the gate without
committing. 22 tests in `test_hooks.py`.

One real bug surfaced while testing it: TOON parses a bare `true` as a
boolean, so `command: [true]` became the string `"True"` and failed to
execute. Fixed with a token coercion helper, now tested.

## Verification

Every new test was mutation-checked — the fix was reverted and the test
confirmed to fail, then restored:

- restoring the `--list` detection bug → 2 failures in `test_project_ready.py`;
- stripping a section from a runtime skill → named failure identifying the
  skill and section.

```
python3 -m unittest discover -s .agentic-template/tests   325 tests, OK
project check                                             all gates OK
project ready                                             READY: PASS
project self-test                                         SELF TEST OK
project hooks                                             PRE-COMMIT OK (0.1s)
full-history secret scan                                  759 blobs, no findings
```

## Still open

- **Positioning copy is a first draft.** `why-this-not-a-skill.md` makes the
  argument I think is strongest (rules that fail beat rules that are merely
  written), but tone and emphasis are the owner's call.
- **`check-secrets` still does not scan history.** The one-off scan above is
  clean, but the committed tool remains working-tree only by design. Run
  gitleaks or trufflehog before publishing any repo with real history.
- **Nothing is committed.** 37 changed/new paths sit in the working tree on
  `main`; per the repo's own contract, direct commits to `main` need explicit
  authorisation.

## Second-pass summary

| Area | Verdict |
|---|---|
| Shift-left pipeline coherence | fixed |
| Self-extending runtime pattern | fixed, and enforced by discovery-driven tests |
| Scaffold adoption path | fixed; wiki rule specified after reversing the original recommendation |
| Secret scanning | fixed; history verified clean, limitation documented |
| TOPICS.toon duplication registry | fixed; terminology reworded |
| DX value proposition | drafted; tone left for the owner |
| Pre-commit gate | new capability, verified end-to-end |
