# Adversarial Debate — Procedure

1. Define the proposal or decision under debate in one paragraph.
2. **Advocate pass**: argue why the proposal is correct, safe, and the best
   available option. Surface evidence supporting the proposal.
3. **Critic pass**: argue why the proposal is wrong, risky, or incomplete.
   Surface evidence against the proposal. Identify missing alternatives.
4. **Synthesis**: the lead agent weighs both passes, identifies the strongest
   points from each, and records the decision with confidence and conditions.
5. Record the debate summary in `HANDOFF.toon` or an ADR if the decision is
   durable.

## Using with `/sudo`

```
/sudo architect advocate for the proposed persistence boundary
/sudo tech-lead criticise the proposed persistence boundary
```

Or run both passes as the same agent using sequential `/sudo` calls. Note
that sequential passes by the same agent are not equivalent to independent
review — record this limitation.

## Patterns

| Pattern | Advocate | Critic |
|---|---|---|
| Architecture | argues for the boundary, dependency direction, or integration | argues for simplicity, alternative boundaries, or coupling risk |
| Build vs buy | argues for building in-house | argues for buying or reusing |
| Scope | argues for including a feature | argues for deferring or removing |
| Technology | argues for a tool or framework | argues against it or for alternatives |
