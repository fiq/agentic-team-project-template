# Context Packet — Procedure

1. Run `project context explain --skill <target skill> --risk <risk>` and keep the TOON
   plan; it already lists the preload set, the deferred set and the required
   verification.
2. State the objective in one sentence and the exact requested output.
3. Copy the acceptance conditions verbatim from the change scenario. Do not paraphrase
   them: they are the contract.
4. List non-goals. Most over-delivery comes from their absence.
5. Add facts, each with a `source`. Anything you cannot source is an assumption; move
   it there.
6. Add files with `sha` digests rather than contents. Add a snippet only where exact
   wording or code shape matters.
7. Attach the routing block so the receiver inherits the same profile and can recover
   against the same sources.
8. Check the packet against the budget for the receiver's window. If it exceeds it,
   split the work rather than compressing the meaning.
9. Record `ask_before` for any destructive or irreversible step.
