---
layer: pattern
pattern: bracketed-probabilistic
skill: review
---

# Bracketed-probabilistic pattern — review contribution

Fills placeholders in `skills/global/review.md` for projects declaring the Bracketed-probabilistic pattern.

---

## insert: architectural-review-extras

- **Boundary provenance** — any persisted or cached value crossing from the probabilistic side must carry reproducibility identifiers (git SHA, dataset ID, split seed, model version). Missing provenance is a defect, not a debt item.
- **Deterministic-side integrity** — flag any change that weakens the deterministic check to make probabilistic output easier to use
- **Split discipline** — flag any code path that can mix train, calibration, and evaluation data
- **Calibrator handling** — flag per-run refits, or calibrators applied outside their fit distribution
