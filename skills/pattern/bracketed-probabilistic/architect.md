---
layer: pattern
pattern: bracketed-probabilistic
skill: architect
---

# Bracketed-probabilistic pattern — architect contribution

Fills placeholders in `skills/global/architect.md` for projects declaring the Bracketed-probabilistic pattern. Sections below name the placeholder they fill.

---

## insert: context-discovery-extras

5. Probabilistic component — model, inference, or estimator producing non-deterministic output
6. Deterministic check — the verifier, calibrator, or gate that wraps the probabilistic output
7. Evaluation harness — split definitions, metrics, provenance rules

## insert: investigate-anchors

Every proposal touches one of two sides — always name which:

- **Probabilistic side** — inference, estimation, generation; outputs carry uncertainty
- **Deterministic side** — checks, calibrators, gates, evaluation; outputs are reproducible from inputs

The interface between the two is load-bearing. Anything crossing from the probabilistic side to the deterministic side must carry provenance (input hash, model version, data split, seed) sufficient to reproduce the value.
