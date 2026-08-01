# Orbit — Operating Contract

## Session startup

Read `AGENTS.md` from disk before substantive answers or tool calls.

## Project identity

A tiny 2D orbital physics sandbox written in Rust. Primary consumer: a
developer learning orbital mechanics through a visual toy.

## Hard boundaries

- Never commit directly to `main`.
- Never change the physics constants (`G`, `PLANET_MASS`) without an approved
  change spec — they define the game's feel.
- Keep the game dependency-free; adding a crate needs a recorded reason.

## Local gotchas

- The game is a single file (`src/main.rs`); keep it that way.
- Physics must stay deterministic — no wall-clock time in the simulation.
