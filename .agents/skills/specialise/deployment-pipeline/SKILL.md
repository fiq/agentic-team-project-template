---
name: deployment-pipeline
description: Every generated project records a deployment pipeline decision from /specialise; evolvable targets, promotion model, catered from the start.
---

# Deployment Pipeline

## Policy

Every generated project must record a deployment pipeline decision at
`/specialise`. The decision may be `deferred` but must have a concrete revisit
trigger. No project is left with an implicit or unrecorded deployment pipeline
decision after `/specialise`.

Deployment is catered for from the start, even when the target is unknown.
The pipeline is evolvable: container deploy, Lambda, Fly, static host, etc.
The skill provides a decision framework, not a fixed target.

## Promotion model

Record the promotion path. Even a manual promotion path is recorded.

```
build ──► test ──► image ──► push ──► deploy
```

- `automated`: CI builds, tests and deploys on merge (or tag).
- `manual`: CI builds and tests; a human promotes.
- `deferred`: the promotion path is recorded but not yet wired.

## Required state

Record the following in `PROJECT_PROFILE.toon`:

```toon
deployment:
  pipeline:
    status: required | deferred | not_applicable
    target: container | lambda | fly | static | unknown
    promotion: automated | manual | deferred
    revisit_trigger: ...
  cd_tool: infer    # GitHub Actions, ArgoCD, etc.
```

## When a deployment target is known

- Create only the smallest useful pipeline skeleton.
- Wire promotion through repository commands (`project build`, `project test`,
  `project image-test`).
- Never automatically deploy from generic template CI.
- Do not require cloud credentials for static validation.

## When the target is unknown

Record `deferred` and a concrete revisit trigger:

```toon
deployment:
  pipeline:
    status: deferred
    target: unknown
    promotion: deferred
    revisit_trigger: deployment target selected
  cd_tool: null
```

## Applicability

Libraries, mobile apps, desktop apps and Godot projects may record
`not_applicable` with a reason but must not leave the decision implicit.

## Relationship to infra-decision

The [`specialise/infra-decision`](infra-decision/SKILL.md) skill records IaC
status (infrastructure-as-code). This skill records the CD flow (how built
artefacts are promoted to environments). They are complementary: IaC defines
what infrastructure exists; the deployment pipeline defines how software
reaches it.

## Do not

- Leave deployment implicit after `/specialise`.
- Provision infrastructure or deploy from generic template CI.
- Require cloud credentials for static validation.
- Add deployment tools without a recorded target.
