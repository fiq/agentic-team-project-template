---
name: runtime-godot
description: Specialise Godot runtime, export and headless test conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Godot

Detect `project.godot`, Godot version, GDScript, C#, native extensions,
GDExtension, OpenXR, Android export and Quest or VR concerns.

Treat Godot separately from Python. Prefer fast script tests, headless tests,
scene-level behaviour tests and platform/device validation as separate fidelity.

## Build and tooling

- `project.godot` is the canonical manifest; the `config/features` block
  records the engine version and renderer.
- Export presets live in `export_presets.cfg`; treat them as build
  configuration and keep credentials out of the committed file.
- Builds run through the Godot binary in headless mode:
  `godot --headless --export-release "<preset>" <output>`.
- Detect whether the project is GDScript-only or uses the .NET/C# build
  (`*.csproj` alongside `project.godot`); the C# path also needs the
  `runtime-csharp` guidance.
- GDExtension native code (C++/Rust) has its own build step (SCons, Cargo);
  detect and respect it rather than folding it into the Godot export.
- Nix owns the developer toolchain; pin the Godot version rather than relying
  on an ambient editor install.
- Commit `.godot/` exclusions; the import cache is generated, not source.

## Static analysis (see specialise/static-analysis)

Godot's analysis story is thinner than a general-purpose runtime, and several
categories are legitimately `not_applicable`. Record the reason rather than
leaving them unresolved — see `specialise/static-analysis`.

| Category | Default tool | Notes |
|---|---|---|
| lint | gdlint (godot-gdscript-toolkit) | plus editor warnings; gdformat for formatting |
| type_check | GDScript static typing | enable typed GDScript and treat warnings as errors |
| sast | not_applicable (usually) | record a reason; games rarely have a code-level attack surface |
| dependency_scan | not_applicable (usually) | asset/addon provenance matters more than a CVE feed |
| complexity | gdlint | function length and nesting checks |
| dast | n/a | only when the project ships a networked service |

For the C#/.NET path, use the `runtime-csharp` table instead — Roslyn
analyzers apply normally there.

These are starting points, not a closed list. If the project uses a tool not
listed here, record it in `PROJECT_PROFILE.toon.static_analysis` with a
`revisit_trigger`.

## Language smells (for review-loop)

Per-frame allocations in `_process`; `get_node` path lookups in hot loops;
deep scene-tree coupling via absolute paths; god scripts; untyped GDScript on
boundaries; signals bypassed by direct cross-node calls; logic in `_ready`
that belongs in a resource; unbounded node instancing without pooling.

## Testing

- GUT (Godot Unit Test) and GdUnit4 are the common GDScript frameworks;
  detect which the project uses rather than imposing one.
- Run tests headless (`godot --headless`) so they work in CI without a
  display server.
- Keep pure logic (rules, math, state machines) in plain scripts or resources
  that can be tested without instantiating a scene — this is the fastest and
  largest layer.
- Scene-level behaviour tests are the integration layer; keep them focused on
  interactions that pure logic tests cannot express.
- Device and platform validation (VR headsets, mobile export, input devices)
  is a separate, manual fidelity. Record it as a validation path in
  `PROJECT_PROFILE.toon` rather than pretending it is automated.

## Ecosystem openness

Godot's tooling changes between major versions, and the addon ecosystem is
community-driven. This skill provides defaults, not a closed list. When
encountering a tool or convention not covered here:

- inspect the project's `project.godot`, `export_presets.cfg`, `addons/` and
  any `*.csproj` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
