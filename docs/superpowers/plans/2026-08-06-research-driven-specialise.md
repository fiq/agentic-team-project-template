# Research-Driven /specialise Consultation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `/specialise` so undecided stack dimensions are resolved through research-driven consultation (framework/DB/hosting options with recommendations, budget-aware hosting, repo topology, security-vetted dependencies, repeatable scaffolding), backed by a new `project dep-audit` command and eight new lazy-loaded skills.

**Architecture:** The template's intelligence lives in concise `SKILL.md` descriptor files (frontmatter `name`/`description` + short markdown body) lazy-loaded through `.agents/skills/CATALOG.toon`, plus deterministic Python check scripts under `.agentic-template/bin/` dispatched by `.agentic-template/bin/project`. This feature adds four `consult/*` skills, four `specialise/*` skills, one new `dep-audit` command, extends `infra-check` for Kubernetes, and wires a consult branch into the orchestrator's decide phase. The orchestrator skill stays at `.agents/skills/init/SKILL.md` with `name: init` — an earlier draft of this plan proposed renaming it to `specialise/SKILL.md` for naming consistency with the `/specialise` slash command; that rename never happened and is out of scope here. `main` already solved the same UX goal more cheaply: `.claude/commands/specialise.md` is a thin wrapper that points at `init/SKILL.md`, so `/specialise` already works without an invasive, multi-file rename. This plan targets `init/SKILL.md` as-is.

**Tech Stack:** Python 3 standard library (no third-party deps), TOON descriptor files, Markdown skills, Nix flake devshell, Docker, osv-scanner, kubeconform.

## Global Constraints

Copied verbatim from `docs/superpowers/specs/2026-07-16-research-driven-specialise-design.md` and `AGENTS.md`. Every task's requirements implicitly include this section.

- Local Nix devshell is always retained; developer tooling stays Nix-owned. Nix must never be assumed as the only path — repeatable execution falls back to pinned containers, then a documented one-shot.
- Every consultation ends in documented decisions: `PROJECT_PROFILE.toon` entries plus an ADR under `docs/decisions/` for material choices. Never just conversation.
- Question discipline: smallest useful question set, one question at a time, multiple choice with a recommendation first, "Other" always offered.
- Evidence always wins. Consultation fills gaps or supports an explicit user-requested reconsideration; it never overrides what the repository demonstrably already is.
- Consult skills are harness-agnostic and self-sufficient: each one carries its own direct method to reach its outcome (structured dialogue, documented decisions, verification) and must produce the same result whether or not any external process tooling is present. Superpowers (`brainstorming`, `writing-plans`, `verification-before-completion`) — or an equivalent process capability in whatever agent is running — is an optional accelerator to reuse when available, never a dependency. When such tooling is present, contribute domain content only and do not duplicate its machinery; when it is absent, run the skill's own method and aim for the identical outcome. Never assume the runner is Claude Code or has Superpowers.
- New `SKILL.md` files MUST start with `---\n` frontmatter containing `name:` and `description:` lines (validated by `check-repo-contract`).
- Python scripts use only the standard library and must be executable (`chmod +x`).
- `CLAUDE.md` is a symlink to `AGENTS.md`; edit `AGENTS.md` only for the shared command table.
- Skipping a security scan is never a silent pass: it prints a visible warning and records the skip reason.
- No committed secrets; pinned images; deterministic cleanup for any container use.
- Use real commit dates. Do not backdate.
- This repo's own wiki has adopted the method/product axis layout (`docs/wiki/method/`, `docs/wiki/product/`, each page frontmatter `axis: method` or `axis: product`). Any wiki edit in this plan must keep that frontmatter and land in the matching directory — `project check` enforces it once any axis directory exists.

---

## File Structure

New files:
- `.agentic-template/bin/dep-audit` — osv-scanner wrapper command (Python, stdlib).
- `.agents/skills/consult/stack-research/SKILL.md`
- `.agents/skills/consult/budget-hosting/SKILL.md`
- `.agents/skills/consult/repo-topology/SKILL.md`
- `.agents/skills/consult/dependency-vetting/SKILL.md`
- `.agents/skills/specialise/scaffold-execution/SKILL.md`
- `.agents/skills/specialise/security-scanning/SKILL.md`
- `.agents/skills/specialise/infra-k8s/SKILL.md`
- `.agents/skills/specialise/local-sandbox/SKILL.md`

Modified files:
- `.agentic-template/bin/project` — register `dep-audit` command and add it to the `check` composite (Task 1).
- `.agentic-template/bin/check-repo-contract` — register the new command file, executable, project command, and eight skills (Tasks 1, 3, 4).
- `.agentic-template/bin/infra-check` — add Kubernetes (kustomize/kubeconform) validation (Task 2).
- `.agentic-template/bin/self-test` — fixtures for `dep-audit` and the `infra-check` Kubernetes branch (Tasks 1, 2).
- `.agents/skills/CATALOG.toon` — entries with triggers for all eight new skills (Tasks 3, 4).
- `.agents/skills/init/SKILL.md` — decide-phase consult branch (Task 5).
- `AGENTS.md` — command table gains `project dep-audit` (Task 6). `CLAUDE.md` follows via symlink.
- `docs/wiki/method/development.md` — describe the consult flow (Task 6).
- `docs/wiki/product/operations.md` — describe `dep-audit` (Task 6).

---

## Task 1: `project dep-audit` command

**Files:**
- Create: `.agentic-template/bin/dep-audit`
- Modify: `.agentic-template/bin/project` (`COMMANDS` dict, currently lines 10-47: the `"check"` list at lines 14-24 and a new standalone entry)
- Modify: `.agentic-template/bin/check-repo-contract` (`REQUIRED_FILES` list, currently lines 9-89; `PROJECT_COMMANDS` list, currently lines 144-153)
- Test: `.agentic-template/bin/self-test` (fixture added in this task, anchored after the `"project --list includes check-readme"` line, currently line 458)

**Interfaces:**
- Produces: executable `.agentic-template/bin/dep-audit` returning exit 0 and printing `status: not_applicable` when no dependency manifests exist; registered as project command `dep-audit`; included in the `check` composite. Later tasks (Task 4 `specialise/security-scanning`) reference this command by name `project dep-audit`.

- [ ] **Step 1: Add a failing self-test fixture**

In `.agentic-template/bin/self-test`, find this exact block (search for `"project --list includes check-readme"`):

```python
        if not expect(work, "project --list includes check-readme", PROJECT + ["--list"], 0, "check-readme"):
            failures += 1
```

Immediately after it (before the `"project --list includes startup"` line), insert:

```python
        if not expect(work, "project --list includes dep-audit", PROJECT + ["--list"], 0, "dep-audit"):
            failures += 1
        if not expect(
            work,
            "dep-audit is not_applicable on template with no manifests",
            PROJECT + ["dep-audit"],
            0,
            "not_applicable",
        ):
            failures += 1
```

- [ ] **Step 2: Run self-test to verify it fails**

Run: `.agentic-template/bin/project self-test`
Expected: FAIL — `failed  project --list includes dep-audit` and `failed  dep-audit is not_applicable ...` (command not registered yet), ending `SELF TEST FAILED`.

- [ ] **Step 3: Create the `dep-audit` script**

Create `.agentic-template/bin/dep-audit` with exactly:

```python
#!/usr/bin/env python3
"""Dependency vulnerability audit via osv-scanner.

Runs osv-scanner over the repository's dependency manifests using a
repeatable execution ladder: a tool provided by the Nix devshell first,
then a pinned official container, then an explicit skip. Skipping is never
a silent pass: it prints a visible WARNING and records the skip reason.

Requires network access to reach the OSV database. Does not modify the
repository. Returns not_applicable (exit 0) when no dependency manifests
exist.
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path.cwd()
OSV_IMAGE = "ghcr.io/google/osv-scanner:v1.9.2"

MANIFEST_NAMES = [
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "mix.exs",
    "Gemfile.lock",
    "composer.lock",
]


def has_manifests():
    for name in MANIFEST_NAMES:
        if list(ROOT.rglob(name)):
            return True
    return False


def skip(reason):
    print("DEP AUDIT SKIPPED")
    print()
    print(f"WARNING: dependency audit skipped: {reason}")
    print("status: skipped")
    print("This is not a pass. Re-run with osv-scanner or docker available")
    print("and network access to obtain a real result.")
    return 0


def run_native():
    result = subprocess.run(["osv-scanner", "-r", "."], cwd=str(ROOT))
    if result.returncode == 0:
        print("DEP AUDIT OK (osv-scanner)")
    return result.returncode


def run_container():
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{ROOT}:/src:ro",
            OSV_IMAGE, "-r", "/src",
        ],
        cwd=str(ROOT),
    )
    if result.returncode == 0:
        print(f"DEP AUDIT OK (osv-scanner container {OSV_IMAGE})")
    return result.returncode


def main():
    if not has_manifests():
        print("DEP AUDIT: no dependency manifests found")
        print("status: not_applicable")
        return 0

    if shutil.which("osv-scanner"):
        return run_native()

    if shutil.which("docker"):
        return run_container()

    return skip("neither osv-scanner nor docker is available on PATH")


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Make it executable**

Run: `chmod +x .agentic-template/bin/dep-audit`

- [ ] **Step 5: Register the command in the dispatcher**

In `.agentic-template/bin/project`, the `"check"` list currently reads:

```python
    "check": [
        [str(BIN / "check-repo-contract")],
        [str(BIN / "check-project-profile")],
        [str(BIN / "check-handoff")],
        [str(BIN / "check-knowledge")],
        [str(BIN / "check-changes")],
        [str(BIN / "check-tooling")],
        [str(BIN / "check-mcp")],
        [str(BIN / "check-secrets")],
        [str(BIN / "context"), "check"],
    ],
```

Add `dep-audit` as the last entry (it needs network access, so it runs after the fully-deterministic checks):

```python
    "check": [
        [str(BIN / "check-repo-contract")],
        [str(BIN / "check-project-profile")],
        [str(BIN / "check-handoff")],
        [str(BIN / "check-knowledge")],
        [str(BIN / "check-changes")],
        [str(BIN / "check-tooling")],
        [str(BIN / "check-mcp")],
        [str(BIN / "check-secrets")],
        [str(BIN / "context"), "check"],
        [str(BIN / "dep-audit")],
    ],
```

Then add a standalone entry next to the other single-script commands. Find:

```python
    "check-readme": [[str(BIN / "check-readme")]],
```

Add immediately after it:

```python
    "dep-audit": [[str(BIN / "dep-audit")]],
```

- [ ] **Step 6: Register in the repo contract**

In `.agentic-template/bin/check-repo-contract`, `REQUIRED_FILES` ends with:

```python
    "docs/wiki/method/context-router.md",
    "docs/wiki/index.md",
]
```

Add the new executable before the closing `]`:

```python
    "docs/wiki/method/context-router.md",
    "docs/wiki/index.md",
    ".agentic-template/bin/dep-audit",
]
```

`REQUIRED_EXECUTABLES` is derived from `REQUIRED_FILES` by prefix filter, so no separate edit is needed there.

In `PROJECT_COMMANDS`, find:

```python
PROJECT_COMMANDS = [
    "help", "startup", "init", "inspect", "check", "backlog", "test",
    "contract-test", "integration-test", "component-test", "e2e-test",
    "lint", "build", "run", "image", "image-test", "repo-check", "check-profile",
    "check-handoff", "check-knowledge", "check-tooling", "check-mcp",
    "check-secrets", "check-readme", "ready", "compose-config", "compose-test",
    "infra-check",
    "docs", "doctor", "self-test", "worktree-status", "context",
    "install-hooks", "hooks",
]
```

Add `"dep-audit"` after `"check-readme"`:

```python
PROJECT_COMMANDS = [
    "help", "startup", "init", "inspect", "check", "backlog", "test",
    "contract-test", "integration-test", "component-test", "e2e-test",
    "lint", "build", "run", "image", "image-test", "repo-check", "check-profile",
    "check-handoff", "check-knowledge", "check-tooling", "check-mcp",
    "check-secrets", "check-readme", "dep-audit", "ready", "compose-config",
    "compose-test",
    "infra-check",
    "docs", "doctor", "self-test", "worktree-status", "context",
    "install-hooks", "hooks",
]
```

- [ ] **Step 7: Run self-test to verify it passes**

Run: `.agentic-template/bin/project self-test`
Expected: PASS — `ok      project --list includes dep-audit`, `ok      dep-audit is not_applicable on template with no manifests`, ending `SELF TEST OK`.

- [ ] **Step 8: Verify the repo contract and check composite pass**

Run: `.agentic-template/bin/project repo-check && .agentic-template/bin/project check`
Expected: `REPO CONTRACT OK`, and `check` runs to completion printing `DEP AUDIT: no dependency manifests found` / `status: not_applicable`.

- [ ] **Step 9: Commit**

```bash
git add .agentic-template/bin/dep-audit .agentic-template/bin/project .agentic-template/bin/check-repo-contract .agentic-template/bin/self-test
git commit -m "feat: add project dep-audit dependency vulnerability command"
```

---

## Task 2: Extend `infra-check` for Kubernetes

**Files:**
- Modify: `.agentic-template/bin/infra-check` (`has_iac_files()` at lines 23-33; add `has_k8s_files()` and `check_kubernetes()`; `main()` at lines 97-110)
- Test: `.agentic-template/bin/self-test` (fixture added in this task, anchored after the `"infra-check returns not_applicable when no IaC files"` block, currently lines 573-581)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `project infra-check` returns `not_applicable` (exit 0) when neither IaC nor Kubernetes manifests exist, and fails clearly (`kubeconform not found`) when Kubernetes manifests exist without the validator. Task 4's `specialise/infra-k8s` skill references this behaviour.

- [ ] **Step 1: Add a failing self-test fixture**

In `.agentic-template/bin/self-test`, find this exact block:

```python
        # ---- infra-check with no IaC files ----
        if not expect(
            work,
            "infra-check returns not_applicable when no IaC files",
            PROJECT + ["infra-check"],
            0,
            "not_applicable",
        ):
            failures += 1
```

Immediately after it, insert (guarded so it only asserts when `kubeconform` is genuinely absent, matching the template devshell):

```python
        # ---- infra-check with kubernetes manifests but no kubeconform ----
        if shutil.which("kubeconform") is None:
            kustomization = work / "kustomization.yaml"
            kustomization.write_text("resources:\n  - deployment.yaml\n")
            if not expect(
                work,
                "infra-check fails clearly for k8s manifests without kubeconform",
                PROJECT + ["infra-check"],
                1,
                "kubeconform not found",
            ):
                failures += 1
            kustomization.unlink()
        else:
            print("ok      infra-check k8s fixture skipped (kubeconform present)")
```

`shutil` is already imported at the top of `self-test`.

- [ ] **Step 2: Run self-test to verify it fails**

Run: `.agentic-template/bin/project self-test`
Expected: FAIL — `failed  infra-check fails clearly for k8s manifests without kubeconform` (infra-check currently returns not_applicable / has no k8s awareness), ending `SELF TEST FAILED`.

- [ ] **Step 3: Add Kubernetes detection to `infra-check`**

In `.agentic-template/bin/infra-check`, `has_iac_files()` currently reads:

```python
def has_iac_files():
    indicators = [
        "*.tf",
        "*.tf.json",
        "Pulumi.yaml",
        "terragrunt.hcl",
    ]
    for pattern in indicators:
        if list(ROOT.glob(pattern)):
            return True
    return False
```

Add a `has_k8s_files()` function immediately after it:

```python
def has_k8s_files():
    if list(ROOT.glob("kustomization.yaml")) or list(ROOT.glob("kustomization.yml")):
        return True
    for base in ("k8s", "deploy", "manifests"):
        directory = ROOT / base
        if directory.is_dir() and (
            list(directory.rglob("*.yaml")) or list(directory.rglob("*.yml"))
        ):
            return True
    return False
```

- [ ] **Step 4: Add Kubernetes validation**

`check_pulumi()` currently ends with:

```python
    print("INFRA CHECK OK (pulumi)")
    return 0
```

Immediately after that function, add:

```python
def check_kubernetes():
    tool = shutil.which("kubeconform")
    if not tool:
        return fail("kubernetes manifests present but kubeconform not found on PATH")

    result = subprocess.run(
        [tool, "-strict", "-summary", "-ignore-missing-schemas", "-recursive", "."],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        return fail(f"kubeconform validation failed:\n{result.stdout.strip()}")

    print("INFRA CHECK OK (kubeconform)")
    return 0
```

- [ ] **Step 5: Route Kubernetes in `main()`**

Replace the current `main()`:

```python
def main():
    if not has_iac_files():
        print("INFRA CHECK: no IaC files found")
        print("status: not_applicable")
        return 0

    # Prefer terraform when present.
    if shutil.which("terraform"):
        return check_terraform()

    if shutil.which("pulumi"):
        return check_pulumi()

    return fail("IaC files present but no supported tool found on PATH")
```

with:

```python
def main():
    iac = has_iac_files()
    k8s = has_k8s_files()

    if not iac and not k8s:
        print("INFRA CHECK: no IaC files found")
        print("status: not_applicable")
        return 0

    # Prefer terraform when present.
    if iac and shutil.which("terraform"):
        return check_terraform()

    if iac and shutil.which("pulumi"):
        return check_pulumi()

    if k8s:
        return check_kubernetes()

    return fail("IaC files present but no supported tool found on PATH")
```

- [ ] **Step 6: Run self-test to verify it passes**

Run: `.agentic-template/bin/project self-test`
Expected: PASS — `ok      infra-check fails clearly for k8s manifests without kubeconform` (or the skip line if kubeconform is present), and `ok      infra-check returns not_applicable when no IaC files` still passes; ending `SELF TEST OK`.

- [ ] **Step 7: Verify no regression on the repo contract**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK`.

- [ ] **Step 8: Commit**

```bash
git add .agentic-template/bin/infra-check .agentic-template/bin/self-test
git commit -m "feat: validate kubernetes manifests via kubeconform in infra-check"
```

---

## Task 3: `consult/*` skill cluster

**Files:**
- Create: `.agents/skills/consult/stack-research/SKILL.md`
- Create: `.agents/skills/consult/budget-hosting/SKILL.md`
- Create: `.agents/skills/consult/repo-topology/SKILL.md`
- Create: `.agents/skills/consult/dependency-vetting/SKILL.md`
- Modify: `.agents/skills/CATALOG.toon` (insert after the `init:` block, currently lines 2-5, before `detect_project_shape:` at line 7)
- Modify: `.agentic-template/bin/check-repo-contract` (`REQUIRED_SKILLS` list, currently lines 95-142)

**Interfaces:**
- Produces: four registered skills at catalog keys `consult_stack_research`, `consult_budget_hosting`, `consult_repo_topology`, `consult_dependency_vetting`. Task 5 (`init/SKILL.md`) routes to these by path.

- [ ] **Step 1: Add failing skill registration to the repo contract**

In `.agentic-template/bin/check-repo-contract`, `REQUIRED_SKILLS` currently starts:

```python
REQUIRED_SKILLS = [
    "discovery/detect-runtime",
```

Add the four consult skills as new first entries:

```python
REQUIRED_SKILLS = [
    "consult/stack-research",
    "consult/budget-hosting",
    "consult/repo-topology",
    "consult/dependency-vetting",
    "discovery/detect-runtime",
```

- [ ] **Step 2: Run repo-check to verify it fails**

Run: `.agentic-template/bin/project repo-check`
Expected: FAIL — `REPO CONTRACT FAILED` listing `missing skill consult/stack-research` (and the other three).

- [ ] **Step 3: Create `consult/stack-research/SKILL.md`**

Create `.agents/skills/consult/stack-research/SKILL.md`:

```markdown
---
name: consult-stack-research
description: Research and recommend current best-practice framework, frontend and database options for undecided stack dimensions.
---

# Consult: Stack Research

## Outcome

Resolve undecided stack dimensions (language, backend framework, frontend,
database) with a researched shortlist and a recommendation, ending in a
documented decision and ADR. Never leave a material dimension resolved only
in conversation.

## Process (harness-agnostic)

This skill is self-sufficient and must reach the same outcome in any agent,
with or without external process tooling.

- Direct method (always applies): drive the dialogue one question at a time,
  multiple choice with the recommendation first, "Other" always offered; then
  record decisions and ADRs as described below.
- Optional accelerator: if Superpowers — or an equivalent brainstorming/planning
  capability in the host agent — is available, reuse it (`brainstorming` for the
  dialogue, `writing-plans` for follow-up planning) and contribute domain
  content only. Never assume it exists and never depend on it; its absence must
  not change the outcome.

## Method

1. Ask language preference only if it is not inferable from repository evidence
   or `CUSTOMIZE_THIS_PROJECT.toon`. Offer common options plus Other.
2. Research the current landscape and versions with live web search. Shortlist
   2-4 options per dimension with a recommendation and reasons
   (e.g. Java -> Spring Boot vs Quarkus vs Micronaut).
3. Default versions to current LTS/stable; confirm with the user when the
   choice is material (e.g. JDK LTS vs latest).
4. Prefer proven, actively maintained frameworks and official scaffold tools
   over niche or hand-rolled alternatives.
5. Run each candidate through `consult/dependency-vetting` before offering it.
6. Record every material pick as a `PROJECT_PROFILE.toon` decision and an ADR
   under `docs/decisions/`.

## Degradation

If web search is unavailable, fall back to model knowledge, explicitly flag the
recommendation as potentially stale, point the user at credible references to
verify (official project docs, endoflife.date), and record the staleness caveat
in `PROJECT_PROFILE.toon` unknowns.

## Do not

- Ask a giant technology checklist.
- Offer a candidate that has not passed dependency vetting.
- End the consultation without a recorded decision and ADR.
```

- [ ] **Step 4: Create `consult/budget-hosting/SKILL.md`**

Create `.agents/skills/consult/budget-hosting/SKILL.md`:

```markdown
---
name: consult-budget-hosting
description: Map a budget tier to a hosting shortlist and record the resulting infrastructure decision.
---

# Consult: Budget and Hosting

## Outcome

Resolve the hosting and budget dimension into the `infrastructure:` block of
`PROJECT_PROFILE.toon` and route to the matching specialise skill, ending in a
documented decision and ADR for material choices.

## Method

1. Ask the budget tier: hobby, pre-seed, startup, scaleup, enterprise
   (plus Other). One question, recommendation first.
2. Map the tier to a hosting shortlist, always including a Kubernetes option
   where viable and always including Other. The shortlist is a starting point,
   refreshed by live research when available, not a frozen list:
   - hobby: GitHub Pages (static), Fly.io, Supabase, Cloudflare Pages/Workers,
     SQLite-class persistence.
   - pre-seed: Fly.io, Supabase, Render/Railway-class PaaS, managed Postgres
     (e.g. Neon); minimal ops.
   - startup: PaaS vs managed Kubernetes (GKE/EKS/AKS) trade-off, managed
     database.
   - scaleup: managed Kubernetes, IaC status `required`.
   - enterprise: managed or on-prem Kubernetes, compliance-aware defaults,
     IaC status `required`.
3. Write `local_topology`, `deployment_target` and `iac.status` to the
   `infrastructure:` block and route to `specialise/infra-fly`,
   `specialise/infra-aws`, or `specialise/infra-k8s`. `specialise/infra-decision`
   then formalises the recorded target into the profile's required shape.
4. Assume infra and container best practice rather than interrogating it:
   pinned images, health checks, no secrets, deterministic cleanup.

## Do not

- Add cloud resources or credentials without a deployment target.
- Freeze the shortlist; refresh with live research when available.
- Leave the infrastructure decision implicit.
```

- [ ] **Step 5: Create `consult/repo-topology/SKILL.md`**

Create `.agents/skills/consult/repo-topology/SKILL.md`:

```markdown
---
name: consult-repo-topology
description: Choose monorepo versus separate repositories and record the resulting topology decision.
---

# Consult: Repository Topology

## Outcome

Decide monorepo versus separate repositories and record the decision. When
splitting, produce per-component repositories and a thin top-level coordination
repo, without losing template state.

## Method

1. Ask monorepo vs separate repos. Recommend monorepo for small teams and
   single-runtime projects.
2. Separate repos: each component directory gets its own `git init`, its own
   `flake.nix` devshell, Dockerfile, CI workflow, and a sliced README/AGENTS.
   The top-level checkout becomes a thin coordination repo that tracks the
   component repos as git submodules and keeps `HANDOFF.toon`, cross-repo
   compose topology, and cross-cutting docs.
3. Register submodules with relative paths immediately; fix up remote URLs when
   the sub-repos are pushed. If remotes are unknown, record a revisit trigger in
   the profile rather than blocking.

## Guards

- A dirty working tree blocks the split: ask the user to commit or stash first.
- Never remove a dirty worktree.

## Do not

- Split without an explicit decision.
- Discard `.agents/`, `.agentic-template/`, `PROJECT_PROFILE.toon` or
  `HANDOFF.toon` when carving components.
```

- [ ] **Step 6: Create `consult/dependency-vetting/SKILL.md`**

Create `.agents/skills/consult/dependency-vetting/SKILL.md`:

```markdown
---
name: consult-dependency-vetting
description: Apply hard security and health rules to every framework, scaffold tool and notable dependency before it is offered.
---

# Consult: Dependency Vetting

## Outcome

Every framework, scaffold tool and notable dependency offered by the other
consult skills passes hard vetting rules before it is offered. The assessment
is recorded alongside the stack ADR.

## Hard rules

- No unpatched high or critical CVEs (check OSV / GitHub advisories via
  research).
- No abandoned projects: a release or meaningful commit within ~12 months.
- Reputable maintaining organisation or clearly healthy community.
- Licence compatible with project intent.
- Typosquat check on package names.

## Outcome recording

- Record the vetting assessment alongside the stack ADR.
- Candidates failing hard rules are not offered, or are offered only with an
  explicit warning if the user insists via Other.
- Selection-time vetting complements the runtime `project dep-audit` scan; both
  are required.

## Do not

- Offer a candidate with an unpatched high or critical CVE by default.
- Skip the typosquat check on package names.
```

- [ ] **Step 7: Register the four skills in the catalog**

In `.agents/skills/CATALOG.toon`, the file currently opens:

```toon
skills:
  init:
    path: init/SKILL.md
    trigger: project_profile_absent_or_material_project_shape_unknown
    purpose: orchestrate discovery, specialisation, identity rewrite and validation

  detect_project_shape:
```

Insert a consult block between the `init:` entry and `detect_project_shape:`:

```toon
skills:
  init:
    path: init/SKILL.md
    trigger: project_profile_absent_or_material_project_shape_unknown
    purpose: orchestrate discovery, specialisation, identity rewrite and validation

  consult_stack_research:
    path: consult/stack-research/SKILL.md
    trigger: undecided_stack_dimension_or_reconsideration_requested
  consult_budget_hosting:
    path: consult/budget-hosting/SKILL.md
    trigger: hosting_or_budget_undecided
  consult_repo_topology:
    path: consult/repo-topology/SKILL.md
    trigger: repo_topology_undecided_or_split_requested
  consult_dependency_vetting:
    path: consult/dependency-vetting/SKILL.md
    trigger: candidate_dependency_requires_vetting

  detect_project_shape:
```

- [ ] **Step 8: Run repo-check to verify it passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK` (all four consult skills present with valid frontmatter).

- [ ] **Step 9: Commit**

```bash
git add .agents/skills/consult .agents/skills/CATALOG.toon .agentic-template/bin/check-repo-contract
git commit -m "feat: add consult skill cluster for research-driven specialise"
```

---

## Task 4: `specialise/*` skill cluster

**Files:**
- Create: `.agents/skills/specialise/scaffold-execution/SKILL.md`
- Create: `.agents/skills/specialise/security-scanning/SKILL.md`
- Create: `.agents/skills/specialise/infra-k8s/SKILL.md`
- Create: `.agents/skills/specialise/local-sandbox/SKILL.md`
- Modify: `.agents/skills/CATALOG.toon` (insert after the `infra_decision:` block, currently lines 233-235, before `deployment_pipeline:` at line 237)
- Modify: `.agentic-template/bin/check-repo-contract` (`REQUIRED_SKILLS` list)

**Interfaces:**
- Consumes: `project dep-audit` (Task 1) and the `infra-check` Kubernetes branch (Task 2), referenced by `security-scanning` and `infra-k8s` respectively.
- Produces: four registered skills at catalog keys `specialise_scaffold_execution`, `specialise_security_scanning`, `specialise_infra_k8s`, `specialise_local_sandbox`.

- [ ] **Step 1: Add failing skill registration to the repo contract**

In `.agentic-template/bin/check-repo-contract`, `REQUIRED_SKILLS` now contains (after Task 3) an `"specialise/infra-decision"` entry. Add the four new entries immediately after it:

```python
    "specialise/infra-decision",
    "specialise/scaffold-execution",
    "specialise/security-scanning",
    "specialise/infra-k8s",
    "specialise/local-sandbox",
    "specialise/deployment-pipeline",
```

- [ ] **Step 2: Run repo-check to verify it fails**

Run: `.agentic-template/bin/project repo-check`
Expected: FAIL — `missing skill specialise/scaffold-execution` (and the other three).

- [ ] **Step 3: Create `specialise/scaffold-execution/SKILL.md`**

Create `.agents/skills/specialise/scaffold-execution/SKILL.md`:

```markdown
---
name: specialise-scaffold-execution
description: Run the official project scaffolder repeatably via a Nix-then-container-then-one-shot ladder and merge into the template.
---

# Specialise: Scaffold Execution

## Outcome

Run the official scaffolder (Spring Initializr, create-vite, mix phx.new, etc.)
repeatably and merge its output into the template structure without losing
template state.

## Execution ladder

1. Tool provided by the Nix devshell, if the flake provides it and Nix is
   present.
2. Pinned official container (`docker run` with a pinned tag or digest).
3. Documented one-shot execution with exact tool versions recorded.

A failed rung falls back one level with the reason recorded.

## Merge

1. Scaffold into a temporary directory.
2. Merge into the template structure, preserving `.agents/`,
   `.agentic-template/`, `PROJECT_PROFILE.toon`, `HANDOFF.toon` and related
   state files.
3. Record the exact scaffold command, image digest and tool versions in the
   ADR.

## Invariants

- Local Nix devshell is always retained; Nix is never the only path.
- Prefer proven scaffold tools over hand-rolled skeletons.
- Every deployable component must build and smoke-test in both Nix and Docker.

## Do not

- Overwrite template state files during merge.
- Use an unpinned scaffold container.
```

- [ ] **Step 4: Create `specialise/security-scanning/SKILL.md`**

Create `.agents/skills/specialise/security-scanning/SKILL.md`:

```markdown
---
name: specialise-security-scanning
description: Wire the project dep-audit dependency vulnerability scan into project check and generated CI.
---

# Specialise: Security Scanning

## Outcome

Runtime dependency vulnerability scanning is available through
`project dep-audit` and runs as part of `project check` and generated CI.

## Method

1. `project dep-audit` wraps osv-scanner (or the ecosystem-native audit tool
   when clearly better), executed via the same Nix-or-container ladder used by
   scaffold execution.
2. It is already part of the `project check` composite; ensure generated CI
   runs `project check` so the audit is exercised.
3. Add osv-scanner to the Nix devshell for specialised projects so the native
   ladder rung is available.

## Degradation

Offline or network-restricted environments skip with an explicit warning, never
a silent pass. A skip is visibly reported and records its reason; it is not a
green result.

## Do not

- Treat a skipped scan as a pass.
- Duplicate build logic in CI instead of calling `project` commands.
```

- [ ] **Step 5: Create `specialise/infra-k8s/SKILL.md`**

Create `.agents/skills/specialise/infra-k8s/SKILL.md`:

```markdown
---
name: specialise-infra-k8s
description: Produce the smallest useful Kubernetes skeleton with kubeconform validation wired into project infra-check.
---

# Specialise: Kubernetes Infrastructure

## Outcome

The smallest useful Kubernetes skeleton exists, is statically validated, and is
never applied automatically.

## Method

1. Create a kustomize base plus overlay with pinned images, resource requests
   and probes.
2. Wire static validation via kubeconform into `project infra-check`
   (kustomization or `k8s/`, `deploy/`, `manifests/` manifests are detected and
   validated).
3. Offer kind or k3d for local smoke testing when Kubernetes is the deployment
   target.

## Guards

- Never applied automatically.
- No cloud credentials required for validation.
- Add kubeconform to the Nix devshell so `project infra-check` can validate.

## Do not

- Apply infrastructure from generic template CI.
- Require cloud credentials for static validation.
```

- [ ] **Step 6: Create `specialise/local-sandbox/SKILL.md`**

Create `.agents/skills/specialise/local-sandbox/SKILL.md`:

```markdown
---
name: specialise-local-sandbox
description: Add a local cloud-service sandbox (LocalStack, Azurite, GCP emulators, Supabase) when containers alone are insufficient.
---

# Specialise: Local Sandbox

## Outcome

Local development gains cloud-service semantics when plain containers are
insufficient or collaborators need a shared sandbox, recorded as part of local
topology.

## Method

1. Trigger when local development needs cloud service semantics beyond plain
   containers, or collaborators need a shared sandbox.
2. Choose the sandbox by target cloud (one question, recommendation first,
   Other offered):
   - AWS: LocalStack.
   - Azure: Azurite.
   - GCP: official emulators.
   - Supabase: `supabase` local stack.
3. Follow existing Compose rules: pinned images, health checks, health-aware
   ordering, deterministic cleanup, no committed secrets.
4. Record the sandbox in the profile as part of local topology.

## Do not

- Add a sandbox without an evidenced need.
- Commit secrets or leave containers running after a bounded smoke test.
```

- [ ] **Step 7: Register the four skills in the catalog**

In `.agents/skills/CATALOG.toon`, find:

```toon
  infra_decision:
    path: specialise/infra-decision/SKILL.md
    trigger: infrastructure_decision_required_after_init

  deployment_pipeline:
```

Insert between them:

```toon
  infra_decision:
    path: specialise/infra-decision/SKILL.md
    trigger: infrastructure_decision_required_after_init

  specialise_scaffold_execution:
    path: specialise/scaffold-execution/SKILL.md
    trigger: official_scaffolder_available_for_chosen_stack
  specialise_security_scanning:
    path: specialise/security-scanning/SKILL.md
    trigger: dependency_manifests_present
  specialise_infra_k8s:
    path: specialise/infra-k8s/SKILL.md
    trigger: kubernetes_deployment_target_selected
  specialise_local_sandbox:
    path: specialise/local-sandbox/SKILL.md
    trigger: local_cloud_service_semantics_required

  deployment_pipeline:
```

- [ ] **Step 8: Run repo-check to verify it passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK` (all four specialise skills present with valid frontmatter).

- [ ] **Step 9: Commit**

```bash
git add .agents/skills/specialise/scaffold-execution .agents/skills/specialise/security-scanning .agents/skills/specialise/infra-k8s .agents/skills/specialise/local-sandbox .agents/skills/CATALOG.toon .agentic-template/bin/check-repo-contract
git commit -m "feat: add specialise skill cluster (scaffold, security, k8s, sandbox)"
```

---

## Task 5: Wire the consult branch into the orchestrator

**Files:**
- Modify: `.agents/skills/init/SKILL.md` (`### 2. Decide` section, currently lines 57-69, immediately before `### 3. Specialise`)

**Interfaces:**
- Consumes: the four `consult/*` skills (Task 3) and four `specialise/*` skills (Task 4), referenced by catalog path.
- Produces: no code interface; an orchestration instruction change.

- [ ] **Step 1: Add the consult branch to the decide phase**

In `.agents/skills/init/SKILL.md`, the `### 2. Decide` section currently reads:

```markdown
### 2. Decide

1. Recommend the smallest useful architecture with confidence and evidence.
   Right-size to the calibrated audience: state what is deliberately excluded,
   secure buy-in, and record a bought-into right-sizing decision in
   `PROJECT_PROFILE.toon` (ADR when durable).
2. Explicitly record the container decision (default to a tested application
   image for deployable services unless a documented exception applies).
3. Explicitly record the local-topology and IaC decision (status: required,
   deferred, or not_applicable with a documented reason).
4. Select test layers from actual risks, not a fixed checklist.
5. Ask only remaining high-impact questions.
```

Replace it with:

```markdown
### 2. Decide

1. Recommend the smallest useful architecture with confidence and evidence.
   Right-size to the calibrated audience: state what is deliberately excluded,
   secure buy-in, and record a bought-into right-sizing decision in
   `PROJECT_PROFILE.toon` (ADR when durable).
2. Explicitly record the container decision (default to a tested application
   image for deployable services unless a documented exception applies).
3. Explicitly record the local-topology and IaC decision (status: required,
   deferred, or not_applicable with a documented reason).
4. Select test layers from actual risks, not a fixed checklist.
5. Ask only remaining high-impact questions.

#### Consult branch (research-driven)

Evidence always wins; consultation fills gaps or supports an explicit,
user-requested reconsideration recorded as a decision change.

1. List undecided material dimensions from `PROJECT_PROFILE.toon`: language,
   backend framework, frontend, persistence, hosting/budget, repo topology,
   local sandbox needs.
2. If any dimension is undecided (greenfield or partial evidence), or the user
   requested reconsideration of a dimension, load only the matching `consult/*`
   skills via `CATALOG.toon`. Do not preload the cluster.
   - stack dimensions -> `consult/stack-research`
     (each candidate first passes `consult/dependency-vetting`).
   - hosting/budget -> `consult/budget-hosting`, routing to
     `specialise/infra-fly`, `specialise/infra-aws` or `specialise/infra-k8s`,
     then `specialise/infra-decision` to formalise the recorded target.
   - monorepo vs separate repos -> `consult/repo-topology`.
   - local cloud-service semantics -> `specialise/local-sandbox`.
3. The consult skills are self-sufficient: they run their own structured
   dialogue and reach the same outcome in any agent. If Superpowers — or an
   equivalent process capability in the host agent — is available, reuse it
   (`brainstorming`, `writing-plans`, `verification-before-completion`) as an
   accelerator and contribute domain content only. Never assume it is present
   and never let its absence change the outcome.
4. Write each resolved dimension to `PROJECT_PROFILE.toon` as a decision and,
   where material, an ADR under `docs/decisions/`.
5. Run the chosen official scaffolder via `specialise/scaffold-execution` and
   ensure `specialise/security-scanning` (`project dep-audit`) is wired.
```

- [ ] **Step 2: Verify the repo contract still passes**

Run: `.agentic-template/bin/project repo-check`
Expected: `REPO CONTRACT OK` (`init/SKILL.md` frontmatter unchanged and valid).

- [ ] **Step 3: Verify no template markers or trailing whitespace regressions**

Run: `git diff --check`
Expected: no output (clean).

- [ ] **Step 4: Commit**

```bash
git add .agents/skills/init/SKILL.md
git commit -m "feat: add research-driven consult branch to the specialise decide phase"
```

---

## Task 6: Documentation

**Files:**
- Modify: `AGENTS.md` (command table, insert after the `project infra-check` row, currently line 57) — `CLAUDE.md` follows via symlink
- Modify: `docs/wiki/method/development.md`
- Modify: `docs/wiki/product/operations.md`

**Interfaces:**
- Consumes: the `dep-audit` command (Task 1) and consult flow (Tasks 3-5).
- Produces: no code interface.

- [ ] **Step 1: Add `project dep-audit` to the canonical command table**

In `AGENTS.md`, find:

```markdown
| `project infra-check` | IaC formatting and static validation |
| `project doctor` | Diagnostic summary of checks and blockers |
```

Insert the new row between them:

```markdown
| `project infra-check` | IaC formatting and static validation |
| `project dep-audit` | Dependency vulnerability audit via osv-scanner (skips with warning offline) |
| `project doctor` | Diagnostic summary of checks and blockers |
```

- [ ] **Step 2: Verify the symlinked CLAUDE.md reflects the change**

Run: `grep -c "project dep-audit" CLAUDE.md`
Expected: `1` (CLAUDE.md is a symlink to AGENTS.md, so the row appears once).

- [ ] **Step 3: Document the consult flow in the development wiki**

`docs/wiki/method/development.md` is on the `method` axis (frontmatter `axis: method`) and ends with the Pre-commit gate section. Append this section at the end of the file, keeping the existing frontmatter untouched:

```markdown

## Research-driven consultation during /specialise

When `/specialise` finds undecided stack dimensions (greenfield, partial
evidence, or an explicit reconsideration request), the decide phase loads only
the relevant `consult/*` skills:

- `consult/stack-research` — researched framework/frontend/database shortlists
  with a recommendation; each candidate passes `consult/dependency-vetting`.
- `consult/budget-hosting` — budget tier to hosting shortlist, routing to the
  matching infra skill (`infra-fly`, `infra-aws`, `infra-k8s`).
- `consult/repo-topology` — monorepo vs separate repos with a coordination
  tracker for the split case.
- `consult/dependency-vetting` — hard CVE/maintenance/licence/typosquat rules
  applied before any dependency is offered.

Every consultation ends in a `PROJECT_PROFILE.toon` decision plus an ADR for
material choices. Evidence always wins over consultation.
```

- [ ] **Step 4: Document `dep-audit` in the operations wiki**

`docs/wiki/product/operations.md` is on the `product` axis (frontmatter `axis: product`) and ends with the Observability section. Append this section at the end of the file, keeping the existing frontmatter untouched:

```markdown

## Dependency vulnerability audit

`project dep-audit` scans dependency manifests with osv-scanner via a
repeatable ladder: a devshell-provided tool first, then a pinned container
(`ghcr.io/google/osv-scanner`), then an explicit skip. A skip is never a silent
pass — it prints a visible warning and records the reason. The audit runs as
part of `project check` and therefore in CI. With no dependency manifests it
reports `not_applicable`.
```

- [ ] **Step 5: Verify no whitespace regressions**

Run: `git diff --check`
Expected: no output.

- [ ] **Step 6: Run the full check and self-test**

Run: `.agentic-template/bin/project check && .agentic-template/bin/project self-test`
Expected: all checks pass; `SELF TEST OK`.

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md docs/wiki/method/development.md docs/wiki/product/operations.md
git commit -m "docs: document dep-audit command and consult flow"
```

---

## Testing rationale (deviation from spec)

The spec's Testing section lists three self-test fixtures: `dep-audit` smoke,
"greenfield consult routing (undecided dimensions detected)", and
"separate-repos split (sub-repo init + tracker state)".

- **dep-audit smoke** is deterministic and implemented (Task 1: `--list`
  registration + `not_applicable` path). The `infra-check` Kubernetes branch
  gets an equivalent deterministic fixture (Task 2).
- **Consult routing** and **separate-repos split** are agent-driven skill
  behaviours, not deterministic Python scripts. `self-test` only exercises the
  `project` command surface, so it cannot assert agent routing without
  inventing helper scripts outside the skill-based design. These are instead
  validated by `check-repo-contract` (Tasks 3-4: the skills and catalog entries
  must exist and route by path), which `self-test` runs at baseline. This is a
  deliberate, called-out deviation: the deterministic contract validates
  presence and wiring; the behavioural scenarios remain manual/agent-verified.

If deterministic behavioural fixtures are later required, they need new helper
scripts (e.g. a `project consult-plan --dry-run` that emits the undecided
dimension list from `PROJECT_PROFILE.toon`), which is out of scope for this
plan and should be a separate spec.

## Final verification

After all tasks:

- [ ] Run `.agentic-template/bin/project check` — expect all checks pass, including `DEP AUDIT ... not_applicable`.
- [ ] Run `.agentic-template/bin/project self-test` — expect `SELF TEST OK`.
- [ ] Run `.agentic-template/bin/project ready` — expect `READY: PASS`.
- [ ] Run `python3 -m unittest discover .agentic-template/tests` — expect all pre-existing tests still pass (no regression).
- [ ] Run `nix flake check` if Nix is available — expect the repo-contract derivation to build (it runs `project check`).
- [ ] Run `git diff --check` — expect clean.
- [ ] Update `HANDOFF.toon` to record delivery state and open a PR; human or lead agent owns merge.
