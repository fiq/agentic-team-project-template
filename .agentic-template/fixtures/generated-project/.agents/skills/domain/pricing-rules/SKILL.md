---
name: pricing-rules
description: How discount, tax and rounding rules compose in this domain.
id: SKILL-pricing-rules
triggers: [price_rule_change_requested]
default_task_risk: high
layers:
  core: core.md
  references: references.md
verification: [.agentic-template/bin/project contract-test]
recovery_sources: [specs/capabilities/]
status: active
---

# Pricing Rules

## Outcome

A price change composes correctly with existing discount, tax and rounding rules.
