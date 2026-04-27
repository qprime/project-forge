---
layer: pattern
pattern: kb
skill: spec
---

# KB pattern — spec contribution

Fills placeholders in `skills/global/spec.md` for projects declaring the KB pattern.

---

## insert: design-extras

- **Stage touched**: state whether the change is in storage, retrieval, assembly, or synthesis. Cross-stage changes are topology changes — name them as such.

## insert: testing-strategy-extras

- **Retrieval determinism**: if the change touches retrieval, include a test that the same query yields the same entries across runs.
- **Grounding**: if the change touches synthesis, include a test that fails on output citing content assembly did not surface.
