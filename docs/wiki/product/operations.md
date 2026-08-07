---
axis: product
---

# Operations

Document runtime topology, deployment, health checks, migration order and
rollback or forward-fix policy after project specialisation.

Do not add cloud emulators, Kubernetes or service dependencies without evidence.

## Observability

Design for prod from the start. Every generated project records an
observability decision at `/specialise` covering traces, structured logs and
metrics.

- prefer OpenTelemetry (OTel) as the unified standard for traces and metrics;
- structured JSON logs with correlation IDs tie logs to traces;
- local instrumentation that works in dev and CI, not just prod — make the
  local collector opt-in;
- do not log sensitive data, credentials, bearer tokens or signed URLs.

See `specialise/observability`.

## Dependency vulnerability audit

`project dep-audit` scans dependency manifests with osv-scanner via a
repeatable ladder: a devshell-provided tool first, then a pinned container
(`ghcr.io/google/osv-scanner`), then an explicit skip. A skip is never a silent
pass — it prints a visible warning and records the reason. The audit runs as
part of `project check` and therefore in CI. With no dependency manifests it
reports `not_applicable`.
