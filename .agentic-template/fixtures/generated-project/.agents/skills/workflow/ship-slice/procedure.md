# Ship Slice — Procedure

1. Pick one acceptance scenario from the capability spec.
2. Implement the thinnest end-to-end path that satisfies it, behind a feature flag
   defaulted off.
3. Write the test that proves the scenario passes with the flag on.
4. Deploy with the flag off. Confirm the regression test passes (flag off = old
   behaviour).
5. Flip the flag on for the target environment. Monitor. Roll back by flipping off.
