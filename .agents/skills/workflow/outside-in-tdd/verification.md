# Outside-in TDD — Verification

## A test you have not seen fail is not evidence

A passing test proves nothing on its own. It may assert something always true,
exercise a path it never reaches, or pass with the implementation deleted.
Agents produce these readily: the test was written to make the suite green, and
a green suite is exactly what a vacuous test delivers.

So the obligation is not "write a test". It is **prove the test can fail, and
fails for the right reason.**

```
red first     ── the test fails BEFORE the implementation exists
green         ── the smallest change makes it pass
prove it      ── break the code again; the SAME test must fail
```

Step three is not optional ceremony. It is the only step that distinguishes a
test that guards behaviour from a test that decorates it.

## Red first

Write the test before the implementation and watch it fail. Read the failure:

- it must fail on the **assertion**, not on an import error, typo, missing
  fixture or syntax error;
- the message must name the behaviour you intend to add;
- if it fails for an unrelated reason, that run proved nothing — fix the test
  and get a real red.

A test written after the implementation has never been observed failing. It
must be mutation-checked before it counts.

## Mutation check

After the test is green, deliberately break what it claims to protect and
confirm it goes red. Then restore.

| You claim the test guards | Break it by |
|---|---|
| a return value or calculation | changing the constant, operator or sign |
| a branch or guard clause | inverting or deleting the condition |
| an error path | removing the raise, or widening the catch |
| a validation rule | removing the validator |
| an ordering or sequencing rule | swapping the order |
| a configuration or wiring rule | removing the entry it reads |

Then check the restore: **the suite must be green again**, from a real rerun,
not from assumption.

If the test still passes while the behaviour is broken, the test is wrong.
Fix the test, not the code. Common causes:

- asserting on a mock's configured return rather than real behaviour;
- asserting something tautological (`assertEqual(x, x)`, a truthy check on a
  non-empty literal);
- asserting a type or shape where the value was the point;
- the code path is never reached — the setup does not do what it appears to;
- an over-broad `try`/`except` in the test swallowing the failure.

## When the change is a bug fix

Reproduce first. The regression test must fail against the **unfixed** code,
for the reason described in the bug report. A regression test that passes
before the fix is not a regression test.

```
reproduce (red on unfixed code) ── fix ── green ── revert fix ── red again
```

## When the change is to tooling, config or a check

Same rule, and it is easier to skip here because there is no obvious
"implementation" to break. Break the input instead:

- a validator: feed it the invalid document it should reject;
- a gate or hook: plant the condition it exists to catch, and confirm it
  blocks;
- a linter rule: write the violation;
- a detection routine: remove the thing being detected.

## Recording it

When a change adds or modifies tests, `HANDOFF.toon.tests_run` records the
verification actually performed, not the intention. If a test was
mutation-checked, say so. If it was not, say that too, with the reason — an
untested test is a known gap, and a silently assumed one is a hidden gap.

## Do not

- Report a test as proving something when it has only ever been observed
  passing.
- Weaken an assertion to make a suite green; that converts a real failure into
  a permanent blind spot.
- Delete or skip a failing test to unblock a commit without recording why.
- Mutation-check by editing the test's expected value — that proves the
  assertion is read, not that the behaviour is guarded.
- Leave the deliberate break in place. Restore, rerun, confirm green.
