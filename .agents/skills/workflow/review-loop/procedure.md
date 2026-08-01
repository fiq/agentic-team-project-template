# Review Loop — Procedure

```
diff ──► pass 1: smells + coupling ──► apply safe cleanups (tests green)
     └─► pass 2: re-check ──► record residual findings ──► stop (≤2 passes)
```

1. Take the diff, not the whole repository. `git diff --stat` bounds the scope.
2. Pass 1: read the diff against the core checklist. Note every finding before
   changing anything, so the pass does not become an unplanned refactor.
3. Apply the cleanups that are safe with tests green. Leave the rest as findings.
4. Run the verification gate. If it is not green, stop and fix before continuing.
5. Pass 2: re-read the changed region only. Confirm the cleanups did not introduce new
   coupling.
6. Record residual findings as knowledge entries or follow-up changes, then stop.
