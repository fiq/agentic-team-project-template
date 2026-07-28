# Pricing Rules — Core

- Rules compose in a fixed order: base price, then discount, then tax, then rounding.
- A discount never applies to a tax-inclusive price; tax is always computed last before
  rounding.
- Rounding is always half-up to the currency's minor unit.
- A price rule change without an approved spec is blocked at the review gate.
