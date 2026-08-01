# Orbit

A tiny 2D orbital physics sandbox written in Rust. A single planet and a ship;
gravity bends the ship's path. Press space to thrust, R to reset, Q to quit.

## Run

```sh
cargo run
```

## Why this fixture exists

This is a synthetic sample project used to exercise the agentic template's
scaffold outside its comfort zone:

- **Rust** — a runtime the template does not specialise yet;
- **no `.agents/context/`** — the scaffold must create the router config from
  scratch;
- **an existing domain skill and catalog** — the scaffold must merge, not
  clobber;
- **a flat legacy wiki** — `docs/wiki/operations.md` without the
  method/product layout. With no axis directory present the project has not
  adopted the layout, so the axis check leaves it alone rather than forcing
  a migration. Adoption is all-or-nothing: creating the first axis directory
  opts in, and every page must then move.

It is intentionally small, fun and visual — a very simple game — so the
scaffold can be tested without entangling any real project.
