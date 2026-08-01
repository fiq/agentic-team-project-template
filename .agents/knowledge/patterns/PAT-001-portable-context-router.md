---
id: PAT-001
type: pattern
title: Portable context router
status: canonical
summary: Route context depth and timing by profile (lean, standard, guarded) chosen by override, fixture-scored qualification, degradation state and task-risk floors; profiles change how much context is loaded, never required behaviour.
owners: [tech-lead]
tags: [context, routing, profiles, qualification, portability]
relates_to:
  - INBOX-003
  - INBOX-008
  - Q-002-codex-context-router-findings
decisions:
  - portable_context_router
  - capability_by_observation_not_registry
  - wiki_method_product_axis
  - yaml_skill_frontmatter_deviation
risks:
  - tool deprecation in per-runtime static-analysis suggestions
  - skill proliferation as the catalog grows
evidence:
  - .agents/context/ROUTER.toon
  - .agents/context/qualification/QUALIFICATION.toon
  - .agentic-template/bin/context
  - .agentic-template/tests/test_scaffold_acceptance.py
  - .agentic-template/tests/test_taxonomy_check.py
  - docs/wiki/method/context-router.md
  - /tmp/vrunnable-scaffold-test (real-project scaffold verification)
reviewed_at: 2026-08-01
review_after: 2026-10-28
---

# Portable Context Router

## Use When

- an agent needs to decide how much context to preload for a task;
- a project wants profile-based context routing without adopting the full
  template;
- capability should be measured by observation, not assumed from a model name;
- output degrades and the recovery policy needs a targeted reload.

## Avoid When

- the project has no meaningful context to route (trivial or single-file);
- a fixed context size is provably sufficient for every reader;
- the team prefers a single canonical context packet for all tasks.

## Steps

1. Choose the profile by the precedence chain — maintainer override,
   fixture-scored qualification, recorded degradation, task-risk floor,
   irreversible guard. Each step can only raise the level.
2. Resolve uncertainty to `standard`, never `lean`.
3. Measure capability with `project context qualify`, scoring observable
   behaviour against a synthetic fixture (contract read, skill resolution,
   facade use, stop condition, file grounding, wrong-path recovery).
4. On degradation, reload the authoritative source named in `RECOVERY.toon`
   and retry once before escalating the profile.
5. Install into an existing project with
   `project context scaffold --into <dir> --apply`; the portable test suite
   travels with it.

## Evidence

The pattern is validated by the template's own acceptance suite (239 tests,
22 acceptance scenarios) and by a real-project scaffold into a fresh VRunnable
clone: `context check` passes (`CONTEXT ROUTER OK`) and `context explain`
resolves a skill and routes to `standard` for an unqualified environment.

The real-project test surfaced one adoption gap — the scaffold did not create
a `CATALOG.toon` when the target had none — which was fixed so the router-only
adoption path works without manual repair.
