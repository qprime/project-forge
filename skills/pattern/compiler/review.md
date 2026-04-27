---
layer: pattern
pattern: compiler
skill: review
---

# Compiler pattern — review contribution

Fills placeholders in `skills/global/review.md` for projects declaring the Compiler pattern.

---

## insert: architectural-review-extras

- **IR discipline** — any conversion path that bypasses the IR is a structural violation, flag it as a defect
- **Generator purity** — flag hidden state in generators (globals, caches without explicit keys, I/O in the generation path)
- **Layer leakage** — computed output-shape state appearing on semantic dataclasses is an AI hazard, not a refactor suggestion
