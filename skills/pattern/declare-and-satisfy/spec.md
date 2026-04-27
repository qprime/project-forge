---
layer: pattern
pattern: declare-and-satisfy
skill: spec
---

# Declare-and-satisfy pattern — spec contribution

Fills placeholders in `skills/global/spec.md` for projects declaring the Declare-and-satisfy pattern.

---

## insert: design-extras

- **Component touched**: state whether the change is in the declaration, the satisfier, or the verifier. Cross-component changes are topology changes — name them as such and explain why.

## insert: testing-strategy-extras

- **Declaration round-trip**: if the change touches declaration format, include a test that writes a declaration and re-reads it without loss.
- **Refinement bounds**: if regeneration is involved, include a test that fails if the loop exceeds its declared budget.
