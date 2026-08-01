---
name: runtime-csharp
description: Specialise .NET, C#, and ecosystem conventions; evolvable, acknowledges unknown tools.
---

# Runtime: C# / .NET

Detect .NET SDK version, project files (`.csproj`, `.fsproj`), solution files
(`.sln`), frameworks (ASP.NET Core, Blazor, MAUI, WPF, WinForms), ORMs
(Entity Framework, Dapper, NHibernate), test frameworks (xUnit, NUnit, MSTest),
and source generators.

Classify application shape from code and config, not framework. Prefer the
existing build tool (`dotnet`). Add migration and test harness guidance only
when evidence requires it.

## Build and tooling

- `dotnet` CLI is the canonical build tool; `dotnet build`, `dotnet test`.
- `dotnet restore` is implicit in modern SDKs but may be explicit in older
  projects.
- Solution files (`.sln`) or solution filters (`.slnf`) group projects;
  detect and respect the existing structure.
- `Directory.Build.props` and `Directory.Packages.props` centralise build
  configuration and package versioning.
- Nix owns the developer toolchain; do not introduce dotnet-version managers
  on NixOS.

## Static analysis (see specialise/static-analysis)

.NET has Roslyn analyzers built in and a rich ecosystem of analysis tools.
The per-runtime defaults are evolvable.

| Category | Default tool | Notes |
|---|---|---|
| lint | dotnet format | code style and formatting enforcement |
| type_check | compiler | `dotnet build` with nullable reference types enabled |
| sast | Roslyn analyzers | Security analyzers from Microsoft.CodeAnalysis.NetAnalyzers |
| dependency_scan | dotnet list package --vulnerable | built-in vulnerability scan (NET 6+) |
| complexity | Roslyn analyzers | complexity analyzers via .NET analyzers |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. SonarAnalyzer, StyleCop, Roslynator, ReSharper,
BenchmarkDotNet), record it in `PROJECT_PROFILE.toon.static_analysis` with a
`revisit_trigger`.

## Language smells (for review-loop)

`async void` outside event handlers; `.Result` or `.Wait()` on async code;
swallowed exceptions in catch blocks; `public` fields instead of properties;
`var` where the type is not obvious; God classes with too many
responsibilities; `new` without dependency injection; magic strings instead
of constants or enums; `Task.Run` for CPU-bound work in ASP.NET; missing
`ConfigureAwait(false)` in library code; `IEnumerable` multiple enumeration;
`string` concatenation in loops instead of `StringBuilder`.

## Testing

- xUnit is the most common test framework; NUnit and MSTest are also used.
- `dotnet test` runs all tests in the solution.
- Integration tests may use `WebApplicationFactory` for ASP.NET Core.
- Snapshot testing: Verify or SnapshotTesting.
- Benchmarking: BenchmarkDotNet.
- Respect the existing test framework; do not impose a different one.

## Ecosystem openness

.NET's ecosystem evolves. This skill provides defaults, not a closed list.
When encountering a tool or convention not covered here:

- inspect the project's `.csproj`, `.sln`, `Directory.Build.props`,
  `Directory.Packages.props`, and `global.json` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
