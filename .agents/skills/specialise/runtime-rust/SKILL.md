---
name: runtime-rust
description: Specialise Rust, Cargo, and ecosystem conventions; evolvable, acknowledges unknown tools.
---

# Runtime: Rust

Detect Cargo, edition, workspace structure, async runtime (tokio, async-std,
smol), web frameworks (axum, actix, rocket, poem), database drivers (sqlx,
diesel, sea-orm), serde, tracing, and test frameworks (built-in, proptest,
quickcheck, insta).

Classify application shape from code and config, not framework. Prefer the
existing build tool (Cargo). Add migration and test harness guidance only when
evidence requires it.

## Build and tooling

- Cargo is the canonical build tool; `cargo build`, `cargo test`, `cargo clippy`.
- Workspaces (`[workspace]` in the root `Cargo.toml`) are common for
  multi-crate projects; detect and respect the existing structure.
- `Cargo.lock` is committed for binaries, not for libraries — respect the
  existing convention.
- Nix owns the developer toolchain; do not introduce rustup on NixOS.

## Static analysis (see specialise/static-analysis)

The Rust toolchain has strong built-in analysis. The per-runtime defaults are
evolvable — Rust's ecosystem moves fast and new tools emerge.

| Category | Default tool | Notes |
|---|---|---|
| lint | clippy | `cargo clippy -- -D warnings` |
| type_check | compiler | `cargo check` |
| sast | clippy | clippy covers many security-adjacent lints; cargo-audit for dependencies |
| dependency_scan | cargo-audit | `cargo audit` for known CVEs in dependencies |
| complexity | clippy | clippy has cognitive-complexity and needless-complexity lints |
| dast | n/a | only when the project has a running service |

These are starting points, not a closed list. If the project uses a tool not
listed here (e.g. cargo-deny, cargo-machete, cargo-udeps, miri), record it in
`PROJECT_PROFILE.toon.static_analysis` with a `revisit_trigger`.

## Language smells (for review-loop)

Excessive `unwrap()`/`expect()` in non-test code; `clone()` where borrowing
suffices; `unsafe` without a safety comment; `String` where `&str` suffices;
blocking calls in async code; `unwrap()` on `Result` from external APIs;
overuse of `Arc<Mutex<>>` where simpler patterns exist; `todo!()` or
`unimplemented!()` left in production code; large `match` arms that should be
extracted; `pub use` re-exports that hide the real module structure.

## Testing

- `cargo test` is the default; respect existing test organisation.
- Integration tests live in `tests/`; unit tests in `src/` alongside code.
- Property testing: proptest or quickcheck when invariants matter.
- Snapshot testing: insta when output stability matters.
- `cargo nextest` is a faster test runner if the project adopts it — detect
  and respect, do not impose.

## Ecosystem openness

Rust's ecosystem evolves rapidly. This skill provides defaults, not a closed
list. When encountering a tool or convention not covered here:

- inspect the project's existing `Cargo.toml`, `.cargo/config.toml`, and
  `rust-toolchain.toml` for evidence;
- respect the existing convention;
- record the tool in `PROJECT_PROFILE.toon` if it is material;
- do not impose a tool the project does not already use unless evidence
  justifies it.
