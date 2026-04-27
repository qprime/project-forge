---
layer: pattern
pattern: bracketed-probabilistic
skill: debug
---

# Bracketed-probabilistic pattern — debug contribution

Fills placeholders in `skills/global/debug.md` for projects declaring the Bracketed-probabilistic pattern.

---

## insert: do-bullets

- Check provenance first — many "bugs" are actually stale cached values from a different model version, dataset, or split seed
- Isolate the side — is the bug on the probabilistic side (different output per run), the deterministic side (reproducible but wrong), or at the interface (provenance mismatch)?
- Re-run with a fixed seed before assuming a bug is deterministic; probabilistic failures often look like logic errors until seeded
- Check split membership — confirm the failing case is in the set you think it's in; leakage and mislabeling masquerade as method failures
