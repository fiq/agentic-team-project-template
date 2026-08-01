---
name: context-qualification
description: Check whether this model and runtime can be trusted with lean progressive disclosure here.
triggers: [no_observation_for_this_environment, profile_dispute, contract_changed]
default_task_risk: low
verification: [".agentic-template/bin/project context qualify --score answers.toon"]
recovery_sources: [.agents/context/qualification/QUALIFICATION.toon]
---

# Context Qualification

## Outcome

A recorded, machine-scored judgement about whether the active model-runtime pair
handles this repository's contract, catalog and stop conditions reliably enough for
`lean` context. Qualification measures behaviour on a fixture; it never trusts a
model's claim about itself.

## Use when

`project context explain` reports `observation_status: absent` or `invalidated`, or a
contract file changed and the recorded evidence no longer applies.

## Loop

```
project context qualify              emit the versioned probe pack
   ▼ answer every probe from the fixture repository only
   ▼ write answers.toon to the schema
project context qualify --score answers.toon [--record]
   ▼ pass ──► lean is licensed for this environment
   ▼ fail / uncertain ──► standard; fix the behaviour, not the score
```

## Do not

- Answer from memory of this repository instead of reading the fixture.
- Record a result for an environment other than the one that answered.
- Treat a `pass` as permanent: it is scoped to a contract fingerprint.
