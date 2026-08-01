---
name: observability
description: Every generated project records an observability decision from /specialise; OTel traces, structured logs, local instrumentation, Observability 2.0.
---

# Observability

## Policy

Every generated project must record an observability decision at
`/specialise`. The decision covers traces, structured logs, and metrics.
Design for prod from the start, with local instrumentation that works in dev
and CI, not just prod.

## Observability 2.0 framing

Prefer OpenTelemetry (OTel) as the unified standard for traces and metrics.
Structured JSON logs with correlation IDs tie logs to traces. This is
Observability 2.0: traces, logs and metrics are correlated, not siloed.

```
request ──► trace (span tree)
              │
              ├──► log events (correlated by trace_id / span_id)
              └──► metrics (counters, histograms)
```

## Local instrumentation

The dev shell and container should emit traces/logs to a local collector
(e.g. OTel collector, Jaeger UI) for debugging. This is a dev-time concern,
not a prod-only afterthought. Local instrumentation catches issues before they
reach CI or prod.

- make the local collector opt-in (do not require a running collector for
  local dev by default);
- provide a documented way to start the collector locally;
- ensure the same instrumentation works in CI and prod.

## Per-runtime guidance

Lightweight, not shims. Suggest the OTel SDK per runtime; structured logging
library per runtime. The framework is adaptable: pick the right tools per
runtime and pivot easily when better options emerge.

| Runtime | traces | logs | metrics |
|---|---|---|---|
| Java | OTel SDK | structured (SLF4J/Logback JSON) | OTel / Micrometer |
| Node/TS | OTel SDK | structured (pino/winston JSON) | OTel / prom-client |
| Python | OTel SDK | structured (structlog/json) | OTel / prometheus |
| Rust | OTel SDK | structured (tracing) | OTel |
| Elixir | OTel SDK | structured (Logger JSON) | OTel / Telemetry |
| Godot | n/a | n/a | n/a |

## Required state

Record in `PROJECT_PROFILE.toon`:

```toon
observability:
  traces: infer       # otel | none
  logs: structured    # structured | plain
  metrics: infer      # otel | prometheus | none
  local_collector: infer
  revisit_trigger: ...
```

## Do not

- Add a full APM SaaS by default.
- Require a running collector for local dev (make it opt-in).
- Log sensitive data, credentials, bearer tokens or signed URLs.
- Treat observability as a prod-only afterthought.
- Add per-runtime shims; use evolvable per-runtime guidance.
