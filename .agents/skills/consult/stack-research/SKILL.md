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
