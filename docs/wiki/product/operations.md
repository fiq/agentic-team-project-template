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
