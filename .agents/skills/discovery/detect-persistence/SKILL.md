---
name: detect-persistence
description: Identify persistence evidence and separate engine, provider and usage semantics.
---

# Detect Persistence

Understand:

- none
- in-memory
- fixture or static repository
- H2
- SQLite
- PostgreSQL
- Supabase as provider plus Postgres as engine
- MySQL or MariaDB
- MongoDB
- AWS DocumentDB
- Redis
- external API as source of truth
- object storage

Do not confuse H2 test dependencies with production persistence. Do not treat
Redis as universal persistence. Relational production state activates
`sql-migrations`.
