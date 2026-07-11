---
name: detect-runtime
description: Identify runtime, framework and package-management evidence.
---

# Detect Runtime

## Evidence

- Node or TypeScript: `package.json`, locks, `tsconfig.json`, Vite, React,
  Next.js, package manager files. Do not treat `npx` as a runtime.
- Java: `pom.xml`, `build.gradle`, wrappers, JDK metadata, Spring Boot,
  Quarkus, Micronaut, JHipster, LangChain4j, Spring AI.
- Python: `pyproject.toml`, `uv.lock`, Poetry, requirements, pytest, FastAPI,
  Flask, Django, LangChain, LangGraph, Pydantic, SQLAlchemy, Alembic.
- Godot: `project.godot`, export presets, GDScript, C#, GDExtension, OpenXR,
  Android or Quest settings.
- Elixir: `mix.exs`, Phoenix, LiveView, Ecto, Oban, ExUnit, releases.

Respect existing runtime management. On NixOS, prefer one source of runtime
truth and do not add NVM unless compatibility requires it.
