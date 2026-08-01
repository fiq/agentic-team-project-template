---
name: runtime-go
description: Specialise Go, modules, and ecosystem conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Go

Detect Go modules (`go.mod`), Go version, web frameworks (gin, echo, fiber,
chi, net/http), database drivers (database/sql, pgx, gorm, sqlx), gRPC,
context usage, and test frameworks (built-in, testify, ginkgo, goconvey).

Classify application shape from code and config, not framework. Prefer the
existing build tool (`go build`, `go test`). Add migration and test harness
guidance only when evidence requires it.

## Build and tooling

- Go modules are the canonical dependency manager; `go.mod` and `go.sum` are
  committed.
- `go build`, `go test`, `go vet` are the standard commands.
- Workspaces (`go.work`) are used for multi-module development; detect and
  respect the existing structure.
- Nix owns the developer toolchain; do not introduce gvm or similar version
  managers on NixOS.

## Static analysis (see specialise/static-analysis)

Go has strong built-in analysis and a rich ecosystem of linters. The
per-runtime defaults are evolvable — new tools emerge regularly.

| Category | Default tool | Notes |
|---|---|---|
| lint | golangci-lint | meta-linter; configure via `.golangci.yml` |
| type_check | go vet | built into the Go toolchain |
| sast | gosec | security-focused linter for Go |
| dependency_scan | govulncheck | `go vuln check` (Go 1.18+) |
| complexity | gocyclo / golangci-lint | cyclomatic complexity via golangci-lint |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. staticcheck, nilaway, errcheck, revive), record it in
`PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

Ignored errors (`_ = err`); `panic` in non-init code; global mutable state;
`interface{}` where a concrete type suffices; deep nesting where early return
is clearer; `context.Background()` in request handlers instead of the passed
context; `sync.Mutex` where a channel is more idiomatic; `time.Sleep` in
tests instead of synchronization; `init()` side effects; large structs passed
by value; `string` concatenation in loops instead of `strings.Builder`.

## Testing

- `go test` is the default; respect existing test organisation.
- Tests live in `_test.go` files alongside source.
- Table-driven tests are idiomatic; respect the pattern.
- Benchmark tests (`func Benchmark*`) are built in.
- Fuzzing (`func Fuzz*`) is built in since Go 1.18.
- Integration tests may use build tags (`//go:build integration`).

## Ecosystem openness

Go's tooling ecosystem evolves. This skill provides defaults, not a closed
list. When encountering a tool or convention not covered here:

- inspect the project's `go.mod`, `Makefile`, `.golangci.yml`, and
  `.go-version` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
