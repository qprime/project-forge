---
layer: pattern
pattern: bracketed-probabilistic
skill: spec
---

# Bracketed-probabilistic pattern — spec contribution

Fills placeholders in `skills/global/spec.md` for projects declaring the Bracketed-probabilistic pattern.

---

## insert: design-extras

- **Side of the interface**: state whether this change is on the probabilistic side, the deterministic side, or at the boundary. If at the boundary, specify the provenance that crosses it.

## insert: testing-strategy-extras

- **Reproducibility**: any test that exercises persisted or cached values must verify that provenance (git SHA, dataset ID, split seed, model version) is present and correct.
- **Split hygiene**: if the change touches data flow, include a test confirming train/cal/eval separation is preserved.

## insert: quality-checks-extras

- [ ] Any persisted value introduced by this change carries provenance sufficient to reproduce it
- [ ] No calibrator is applied outside the distribution it was fitted on
