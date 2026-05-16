---
name: test-first
---

# Test-first Workflow

```
behaviour -> smallest failing test -> minimal implementation
  -> test passes -> refactor if useful -> increase fidelity for remaining risk
```

Ask:

1. What behaviour are we proving?
2. What is the cheapest test that can fail for the right reason?
3. Which integration semantics remain untested?
4. Is a real dependency cheap enough to use?
5. What added fidelity buys real confidence?

Do not force theatre when work is exploratory or test cost exceeds learning.
