---
name: messaging-kafka
description: Specialise Kafka semantics, reliability concerns and tests when active Kafka roles exist.
---

# Messaging: Kafka

Specialise only when Kafka is active or required.

Assess event ownership, schema evolution, partition key, ordering,
at-least-once delivery, idempotency, duplicates, poison events, retries, DLQ,
consumer lag, topic depth, observability and replay behaviour.

Do not generate Kafka infrastructure merely because a client dependency exists.
