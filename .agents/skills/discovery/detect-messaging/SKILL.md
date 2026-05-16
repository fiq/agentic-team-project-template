---
name: detect-messaging
---

# Detect Messaging

Look for active semantics, not just dependencies:

- Kafka consumer, producer or Streams
- event publisher or listener
- queue worker
- stream processor
- synchronous HTTP-only service

Decide from interaction semantics:

```
caller needs response now -> synchronous interface
long-running independent work -> asynchronous path
many consumers need event -> event propagation candidate
replay matters -> durable event log candidate
```

Kafka evidence does not automatically justify event-driven architecture.
