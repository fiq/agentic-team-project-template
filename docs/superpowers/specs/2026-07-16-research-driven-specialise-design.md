# Research-Driven Stack Consultation for /specialise

Date: 2026-07-16
Status: approved

## Goal

Extend the `/specialise` flow so that undecided stack dimensions are resolved
through research-driven consultation: current best-practice options with
recommendations, budget-aware hosting choices, repo topology selection,
security vetting of dependencies, and repeatable scaffold execution — while
keeping local Nix always and ensuring every deployable component builds in
both Nix and Docker.

## Scope

- New `consult/*` skill cluster (4 skills) and 4 new `specialise/*` skills,
  registered in `.agents/skills/CATALOG.toon`.
- One new branch in the `init` orchestrator decide phase.
- One new canonical command: `project dep-audit`.
- Extensions to `check-repo-contract` and `self-test` fixtures.
- Documentation updates (AGENTS.md command table, CLAUDE.md, wiki).

Out of scope: changing the evidence-first discovery skills, changing existing
specialise skills beyond routing references, provisioning any cloud
infrastructure.

## Trigger model

The consultation is **always available**:

1. Greenfield: discovery finds no runtime/framework evidence → consult skills
   resolve all material undecided dimensions.
2. Gaps: partial evidence (e.g. Java present, no framework; app present, no
   hosting decision) → consult only the undecided dimensions.
3. Explicit request: the user asks to reconsider a dimension on an existing
   project (e.g. hosting). Consult runs for that dimension only.

Evidence always wins. Consultation never overrides what the repository
demonstrably already is; it fills gaps or supports an explicit, user-requested
reconsideration recorded as a decision change.

## Routing and orchestration

`init/SKILL.md` decide phase gains a consult branch:

1. After discovery, list undecided material dimensions from
   `PROJECT_PROFILE.toon`: language, backend framework, frontend, persistence,
   hosting/budget, repo topology, local sandbox needs.
2. If any dimension is undecided (or reconsideration was requested), load only
   the matching `consult/*` skills via `CATALOG.toon`. Do not preload the
   cluster.
3. Each resolved dimension is written to `PROJECT_PROFILE.toon` as a decision
   and, where material, an ADR under `docs/decisions/`.

### Superpowers integration (non-clobbering)

Each consult skill begins with a harness check:

- If the Superpowers plugin is available, the consultation runs inside its
  conventions: `superpowers:brainstorming` owns the dialogue pattern (one
  question at a time, options with a recommendation),
  `superpowers:writing-plans` owns implementation planning after decisions,
  and `superpowers:verification-before-completion` gates the validate phase.
- The consult skills contribute domain content only: option shortlists,
  budget tables, vetting rules. They must not duplicate or re-implement
  Superpowers process machinery, and must not override its instructions.
- Without Superpowers, each skill carries a minimal inline fallback dialogue
  pattern (one question at a time, multiple choice with recommendation first,
  "Other" always offered).

## Consult skills

### consult/stack-research

- Ask language preference only if not inferable from evidence or
  `CUSTOMIZE_THIS_PROJECT.toon`; offer common options plus Other.
- Research the current framework landscape and versions with live web search:
  shortlist 2–4 options per dimension (backend framework, frontend, database)
  with a recommendation and reasons. Example: Java → Spring Boot vs Quarkus vs
  Micronaut.
- Versions default to current LTS/stable; confirm with the user when the
  choice is material (e.g. JDK LTS vs latest).
- Prefer proven, actively maintained frameworks and official scaffold tools
  over niche or hand-rolled alternatives.
- Degradation: if web search is unavailable, fall back to model knowledge,
  explicitly flag recommendations as potentially stale, point the user at
  credible references to verify (official project docs, endoflife.date), and
  record the staleness caveat in `PROJECT_PROFILE.toon` unknowns.
- Every material pick produces an ADR and a profile decision. Consultations
  always end in documented decisions, never just conversation.
- Each candidate passes `consult/dependency-vetting` before being offered.

### consult/budget-hosting

- Ask budget tier: hobby, pre-seed, startup, scaleup, enterprise (plus Other).
- Map tier to a hosting shortlist, always including a Kubernetes option where
  viable and always including Other:
  - hobby: GitHub Pages (static), Fly.io, Supabase, Cloudflare Pages/Workers,
    SQLite-class persistence.
  - pre-seed: Fly.io, Supabase, Render/Railway-class PaaS, managed Postgres
    (e.g. Neon); minimal ops.
  - startup: PaaS vs managed Kubernetes (GKE/EKS/AKS) trade-off, managed
    database.
  - scaleup: managed Kubernetes, IaC status `required`.
  - enterprise: managed or on-prem Kubernetes, compliance-aware defaults,
    IaC status `required`.
- The shortlist is a starting point, refreshed by live research when
  available, not a frozen list.
- Output feeds the `infrastructure:` block of `PROJECT_PROFILE.toon`
  (local_topology, deployment_target, iac status) and routes to the matching
  specialise skill: `infra-fly`, `infra-aws`, or the new `infra-k8s`.
- Infra and container best practice is assumed, not interrogated: pinned
  images, health checks, no secrets, deterministic cleanup per existing rules.

### consult/repo-topology

- Ask monorepo vs separate repos; recommend monorepo for small teams and
  single-runtime projects.
- Separate repos: each component directory gets its own `git init`, its own
  `flake.nix` devshell, Dockerfile, CI workflow, and a sliced README/AGENTS.
  The top-level checkout becomes a thin coordination repo: it tracks the
  component repos as git submodules and keeps `HANDOFF.toon`, cross-repo
  compose topology, and cross-cutting docs.
- Submodules are registered with relative paths immediately; remote URLs are
  fixed up when the sub-repos are pushed. If remotes are unknown, record a
  revisit trigger in the profile rather than blocking.
- A dirty working tree blocks the split; the user is asked to commit or stash
  first.

### consult/dependency-vetting

Hard rules applied to every framework, scaffold tool, and notable dependency
offered by the other consult skills:

- No unpatched high or critical CVEs (check OSV / GitHub advisories via
  research).
- No abandoned projects: a release or meaningful commit within ~12 months.
- Reputable maintaining organisation or clearly healthy community.
- Licence compatible with project intent.
- Typosquat check on package names.

The assessment is recorded alongside the stack ADR. Candidates failing hard
rules are not offered (or are offered only with an explicit warning if the
user insists via Other).

## Specialise skills

### specialise/scaffold-execution

Run the official scaffolder (Spring Initializr, create-vite, mix phx.new,
etc.) repeatably, via a fallback ladder:

1. Tool provided by the Nix devshell, if the flake provides it and Nix is
   present.
2. Pinned official container (`docker run` with a pinned tag or digest).
3. Documented one-shot execution with exact tool versions recorded.

Scaffold into a temporary directory, then merge into the template structure,
preserving `.agents/`, `.agentic-template/`, `PROJECT_PROFILE.toon`,
`HANDOFF.toon` and related state files. The exact scaffold command, image
digest and versions are recorded in the ADR. A failed rung falls back one
level with the reason recorded.

### specialise/security-scanning

- New canonical command `project dep-audit` wrapping osv-scanner (or the
  ecosystem-native audit tool when clearly better), executed via the same
  Nix-or-container ladder.
- Wired into `project check` and generated CI.
- Offline or network-restricted environments: skip with an explicit warning,
  never a silent pass.

### specialise/infra-k8s

- Smallest useful Kubernetes skeleton (kustomize base + overlay), pinned
  images, resource requests, probes.
- Static validation via kubeconform wired into `project infra-check`.
- kind or k3d offered for local smoke testing when Kubernetes is the
  deployment target.
- Never applied automatically; no cloud credentials required for validation.

### specialise/local-sandbox

Triggered when local development needs cloud service semantics beyond plain
containers, or collaborators need a shared sandbox:

- AWS: LocalStack. Azure: Azurite. GCP: official emulators.
  Supabase: `supabase` local stack. Plus Other.
- Follows existing Compose rules: pinned images, health checks, health-aware
  ordering, deterministic cleanup, no committed secrets.
- Recorded in the profile as part of local topology.

## Invariants

- Local Nix devshell is always retained; developer tooling stays Nix-owned.
- Nix must not be assumed as the only path: repeatable execution falls back
  to containers so collaborators without Nix can work.
- Every deployable component builds and smoke-tests in both Nix and Docker;
  `project ready` covers both where applicable.
- Proven scaffold tools are preferred over hand-rolled skeletons.
- Every consultation ends in documented decisions: profile entries plus ADRs
  for material choices.
- Question discipline: smallest useful question set, one at a time, multiple
  choice with a recommendation first, Other always available.

## Error handling

| Failure | Behaviour |
|---|---|
| No web search available | Model-knowledge fallback, staleness caveat, credible references, unknown recorded |
| Scaffolder rung fails | Fall back one ladder rung, record reason |
| Dirty repo before topology split | Block, ask user to commit or stash |
| Unknown sub-repo remotes | Relative-path submodules now, revisit trigger recorded |
| dep-audit offline | Skip with warning, never silent pass |

## Testing

- `project self-test` fixtures: greenfield consult routing (undecided
  dimensions detected), separate-repos split (sub-repo init + tracker state),
  `dep-audit` command smoke.
- `check-repo-contract` extended to validate the new skills and catalog
  entries.
- New skill files follow the existing SKILL.md frontmatter format so existing
  validation applies.

## Documentation updates

- AGENTS.md / CLAUDE.md canonical command table gains `project dep-audit`.
- `init/SKILL.md` phases updated (decide-phase consult branch).
- `CATALOG.toon` gains entries with triggers for all 8 new skills.
- Wiki development/operations pages updated where they describe /specialise.
