---
name: sql-migrations
---

# SQL Migrations

Trigger when persistent relational storage is selected.

1. Detect existing migration tool.
2. Preserve project conventions.
3. Choose stack-appropriate tooling when absent: Flyway or Liquibase for Java,
   Alembic or Django migrations for Python, Ecto for Elixir, project ORM
   tooling for Node.
4. Configure migration execution.
5. Test from an empty schema.
6. Test upgrade from representative previous schema where risk matters.
7. Define rollback or forward-fix policy.
8. Document deployment ordering.
9. Integrate checks into CI.

Production relational schema changes must not rely solely on automatic DDL.
