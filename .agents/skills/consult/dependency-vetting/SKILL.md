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
