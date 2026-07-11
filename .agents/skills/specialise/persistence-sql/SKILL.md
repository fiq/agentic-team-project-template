---
name: persistence-sql
description: Specialise relational persistence boundaries, tests and migration expectations.
---

# Persistence: SQL

Prefer relational persistence when transactional state, relational integrity,
durable projections or query patterns justify it. Represent engine and provider
separately, for example `engine: postgres` and `provider: supabase`.

Relational production schema changes require migrations and migration tests.
