---
name: ci
description: Specialise CI so workflows call repository command primitives.
---

# CI

CI must call repository primitives such as `.agentic-template/bin/project check`,
`.agentic-template/bin/project test`, `.agentic-template/bin/project integration-test`
and `.agentic-template/bin/project image`. Do not duplicate build logic in YAML.

Generic template CI must not require interactive AI tooling, MCP servers,
Superpowers or external model access.
