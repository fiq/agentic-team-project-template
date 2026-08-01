---
id: INBOX-009
type: inbox
title: Route context depth by observed capability and task risk
status: superseded
superseded_by: PAT-001-portable-context-router
summary: A portable context router with three profiles (lean, standard, guarded) chosen by override, fixture-scored qualification, degradation state and task-risk floors. Profiles change how much context is loaded, never required behaviour. Promoted to PAT-001.
proposal_type: pattern
relates_to:
  - INBOX-003
  - INBOX-008
  - PAT-001-portable-context-router
  - PROJECT_PROFILE.toon#decisions.portable_context_router
  - PROJECT_PROFILE.toon#decisions.capability_by_observation_not_registry
  - PROJECT_PROFILE.toon#decisions.wiki_method_product_axis
  - PROJECT_PROFILE.toon#decisions.yaml_skill_frontmatter_deviation
evidence:
  - https://www.infoq.com/articles/ai-speed-context-store-architecture/
  - docs/wiki/method/context-router.md
  - .agents/context/ROUTER.toon
  - .agents/context/qualification/QUALIFICATION.toon
  - .agentic-template/fixtures/qualification-repo
  - .agentic-template/fixtures/generated-project
  - .agentic-template/bin/context
  - .agentic-template/tests/test_scaffold_acceptance.py
  - real-project scaffold verification (fresh clone of an existing project)
created_during: portable context router thin slice
recommended_action: promoted to PAT-001 after a real-project scaffold verified the router works end-to-end
expires_after: 2026-10-28
---

# Portable Context Router

## Proposal

Route context depth and timing by profile (`lean`, `standard`, `guarded`), never
required behaviour. A precedence chain — maintainer override, fixture-scored
qualification, recorded degradation, task-risk floor, irreversible guard — chooses
the profile, and every step can only raise it. Uncertainty resolves to `standard`,
never `lean`.

Capability is never inferred from a model's name. It is measured by
`project context qualify`, which scores observable behaviour against a synthetic
fixture: reading the contract from disk, resolving a skill path through the
catalog, using the command facade, honouring a stop condition, grounding an
answer in a file, and recovering after being handed a wrong path.

When output degrades, the policy is to reload the authoritative source named in
`RECOVERY.toon` and retry once before escalating the profile. Every context plan
entry carries its source path and digest so the reload can be targeted.

The router is portable: `project context scaffold --into <dir>` installs it
into any project, and the portable test suite travels with it.

## Evidence so far

The only evidence is the template's own fixture and acceptance suite (177 tests,
22 acceptance scenarios). The fixture proves the router works mechanically —
profiles preload the right layers, qualification is unguessable (defeat score
0 of 6 blind), the scaffold produces a project that passes `context check`, and
degradation recovery and observation invalidation work end to end.

Promotion needs a real generated project to report that profile-based preloading
improves startup, review or handoff quality without excess ceremony.
