---
name: static-analysis
description: Every generated project makes an explicit static-analysis decision at /specialise; opinionated about categories, evolvable per-runtime tools.
---

# Static Analysis

## Policy

Every generated project must make an explicit static-analysis decision at
`/specialise`. The decision covers required analysis *categories*, not specific
tools. Tools are evolvable defaults recorded with a deprecation revisit trigger.

Static analysis is a shift-left gate: it runs before tests in CI and catches
defects, style violations, type errors, security vulnerabilities (SAST),
dependency vulnerabilities, complexity drift and dead code before they reach
review or production. This is broader than just "lint" — it encompasses the
full static analysis spectrum: SAST, DAST (where applicable), dependency
scanning, type-checking, complexity analysis and style enforcement.

The framework is opinionated about *categories* (every project must address
them) but adaptable about *tools* (pick the right ones per runtime, and pivot
easily when better options emerge). The per-runtime table below is a starting
point, not a closed list. Adding static analysis for a new runtime should be
natural: identify the category-appropriate tools, record them with a revisit
trigger, and wire `project lint`. Engineering generalisation, not tool
avoidance, is the goal.

## Required categories

The project must address each category. A category may be recorded as
`not_applicable` with a reason when the runtime genuinely does not support it.

| Category | Purpose |
|---|---|
| `lint` | Style and convention enforcement |
| `type_check` | Static type checking where the runtime supports it |
| `sast` | Static application security testing — code-level security analysis |
| `dependency_scan` | Dependency vulnerability scanning (SCA) |
| `complexity` | Cyclomatic/cognitive complexity or dead-code detection |
| `dast` | Dynamic application security testing — optional, runtime-level, when the project has a running service |

## Per-runtime tool suggestions

These are evolvable defaults, not authoritative mandates. Record the chosen
tool in `PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`. Prefer
OSS tools. Watch for upstream deprecation or abandonment.

| Runtime | lint | type_check | sast | dependency_scan | complexity |
|---|---|---|---|---|---|
| JVM/Java | Checkstyle, PMD | compiler, NullAway | SpotBugs | OWASP Dep-Check | PMD |
| JVM/Kotlin | ktlint, detekt | compiler | detekt | OWASP Dep-Check | detekt |
| JVM/Scala | scalafix | compiler | wartremover | sbt-dep-graph | scalafix |
| JVM/Clojure | clj-kondo | n/a | clj-kondo | n/a | clj-kondo |
| Node/TS | ESLint | tsc --noEmit | eslint-security | npm audit, audit-ci | ESLint complexity rules |
| Python | ruff | mypy, pyright | bandit | pip-audit | ruff, radon |
| Rust | clippy | compiler | clippy | cargo-audit | clippy |
| Go | golangci-lint | go vet | gosec | govulncheck | golangci-lint |
| C#/.NET | dotnet format | compiler | Roslyn analyzers | dotnet list --vulnerable | Roslyn analyzers |
| Elixir | credo | dialyzer | sobelow | mix audit | credo |
| Ruby | RuboCop | Sorbet (if adopted) | brakeman | bundler-audit | RuboCop |
| Perl/Raku | perlcritic | n/a | Perl::Critic security | CPAN audit | perlcritic |
| Godot | GDScript warnings | built-in | n/a | n/a | n/a |

## Evolvability and deprecation risk

Tools change. Upstream projects get deprecated or abandoned. The skill
deliberately avoids per-tool shims or scripts. Instead:

- record the chosen tool and its upstream health signal (active, maintained,
  archived);
- record a `revisit_trigger` (e.g. "tool deprecated", "better OSS alternative
  emerges", "language version upgrade");
- prefer tools that are actively maintained and have a clear governance model;
- avoid tools that require a SaaS account for basic linting unless the project
  explicitly opts in.

## Command surface

Expose `.agentic-template/bin/project lint`. It must:

- run all configured static-analysis tools for the project (lint, type-check,
  SAST, dependency scanning, complexity, DAST where applicable);
- fail (non-zero exit) on violations unless the project explicitly records a
  warn-only policy with a revisit trigger;
- be deterministic and repeatable in CI and locally.

Libraries and Godot projects may record `lint` as `not_applicable` with a
reason, but must not leave it unspecialised after `/specialise`.

## Pre-commit hook

Generated projects should install a pre-commit hook that runs a fast subset
of `project lint` (typically lint and type-check, not full SAST or dependency
scanning which may be slower) before a commit is created. This catches defects
at the earliest possible point — before the developer even stages or pushes.

- the hook must be non-blocking by default for the template (opt-in via
  `project install-hooks`);
- the hook should run in under 5 seconds for fast feedback;
- full SAST, dependency scanning and DAST run in CI, not the pre-commit hook,
  unless the project explicitly opts in;
- the hook must not require network access or external services.

## Profile state

Record in `PROJECT_PROFILE.toon`:

```toon
static_analysis:
  lint:
    tool: ...
    status: specialised | not_applicable
    warn_only: false
  type_check:
    tool: ...
    status: specialised | not_applicable
  sast:
    tool: ...
    status: specialised | not_applicable
  dependency_scan:
    tool: ...
    status: specialised | not_applicable
  complexity:
    tool: ...
    status: specialised | not_applicable
  revisit_trigger: tool_deprecation_or_better_alternative
  enforce_in_ci: true
```

## CI integration

CI must call `project lint` early in the pipeline, before or in parallel with
`project test`. See [`specialise/ci`](ci/SKILL.md).

## Do not

- Hard-pin specific tools in the template; use evolvable per-runtime defaults.
- Leave `lint` unspecialised after `/specialise`.
- Add per-tool shims or scripts in the template.
- Run lint as warn-only without recording the reason and revisit trigger.
- Add every category when the runtime does not support it; record
  `not_applicable` with a reason.
- Require a SaaS account for basic static analysis.
