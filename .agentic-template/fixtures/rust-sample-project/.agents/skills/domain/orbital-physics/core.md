# Orbital Physics — Core

## Invariants

- `G` and `PLANET_MASS` define the game's feel; changing them is a
  high-risk change requiring an approved spec.
- Physics must be deterministic: no wall-clock time, no randomness, no
  platform-dependent floating-point surprises.
- The ship starts at `(10, 10)` with velocity `(0.4, 0.0)`; reset restores
  exactly this state.

## Integration

- One step per frame: compute gravity from the planet, update velocity, then
  position.
- Clamp the distance to avoid division by zero when the ship reaches the
  planet.
