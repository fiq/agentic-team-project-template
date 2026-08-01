---
name: runtime-elixir
description: Specialise Elixir, Mix, Phoenix, Ecto and OTP project conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Elixir

Detect Mix, OTP applications, Phoenix, LiveView, Ecto, Oban, Broadway, ExUnit
and release configuration. Use Elixir and Erlang versions from project evidence
where available.

Prefer ExUnit, boundary tests, Ecto sandbox where applicable and OTP process
behaviour tests where semantics matter.

## Build and tooling

- Mix is the canonical build tool; `mix.exs` and `mix.lock` are committed.
- `mix deps.get`, `mix compile`, `mix test` are the standard commands.
- Umbrella projects (`apps/`) group related applications; detect and respect
  the existing structure.
- Releases are built with `mix release`; detect `rel/` and runtime
  configuration in `config/runtime.exs`.
- Compile with warnings as errors in CI (`mix compile --warnings-as-errors`);
  the compiler catches a great deal in this ecosystem.
- Nix owns the developer toolchain; do not introduce asdf or kiex on NixOS.

## Static analysis (see specialise/static-analysis)

Elixir leans on the compiler plus a small set of mature tools. The per-runtime
defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | Credo | `mix credo --strict`; style and consistency |
| type_check | Dialyzer | via dialyxir; set up a PLT cache in CI |
| sast | Sobelow | Phoenix-focused security scanner |
| dependency_scan | `mix hex.audit` / mix_audit | retired and vulnerable package checks |
| complexity | Credo | complexity and nesting checks are built in |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. Gradient, Styler, Boundary, ExCoveralls), record it in
`PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

Rescuing without re-raising; overusing processes as mutable state; unsupervised
processes; `with` chains that hide error paths; N+1 Ecto queries; business
logic in controllers or LiveViews; atoms from untrusted input; large context
modules; ignoring `{:error, _}` returns.

## Testing

- ExUnit is the built-in framework; `mix test` is the standard command.
- `async: true` on test cases that do not share global state; the Ecto sandbox
  makes most database tests safely async.
- Use `Ecto.Adapters.SQL.Sandbox` for database isolation rather than manual
  cleanup.
- Property testing: StreamData when invariants matter.
- Test OTP behaviour (supervision, restarts, timeouts) where those semantics
  carry real risk, not by default.
- Phoenix: `ConnCase` for controller tests, `LiveViewTest` for LiveView.

## Ecosystem openness

The Elixir ecosystem is small but evolves steadily. This skill provides
defaults, not a closed list. When encountering a tool or convention not
covered here:

- inspect the project's `mix.exs`, `mix.lock`, `.credo.exs`,
  `.tool-versions` and `config/` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
