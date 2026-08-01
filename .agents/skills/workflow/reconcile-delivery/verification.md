# Reconcile Delivery — Verification

## Ready gate

`project ready` must fail when:

- README or AGENTS still describes the project as a template;
- documentation references missing services or files;
- active specs claim major components that are not delivered or explicitly
  deferred;
- commands documented in README do not exist.
