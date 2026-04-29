---
layer: pattern
pattern: bracketed-probabilistic
command: engineer
---

# Bracketed-probabilistic pattern — engineer contribution

Fills placeholders in `commands/global/engineer.md` for projects declaring the Bracketed-probabilistic pattern.

---

## insert: do-bullets

- Carry provenance across the probabilistic/deterministic boundary — git SHA, dataset ID, split seed, model version — sufficient to reproduce any persisted value
- Respect split discipline — train, calibration, and evaluation sets stay separated by the declared partitioning rule
- Treat calibrators as fitted artifacts — fit once on train, apply elsewhere; no per-run refits

## insert: dont-bullets

- Don't weaken the deterministic check to make probabilistic output easier to use — the check is load-bearing
- Don't merge train and calibration sets for "more data" — it reintroduces leakage the split rule exists to prevent
- Don't mutate an input distribution to make it match a calibrator's fit range — raise instead
