---
layer: pattern
pattern: declare-and-satisfy
skill: debug
---

# Declare-and-satisfy pattern — debug contribution

Fills placeholders in `skills/global/debug.md` for projects declaring the Declare-and-satisfy pattern.

---

## insert: do-bullets

- Bisect by component — is the bug in the declaration, in satisfaction, or in verification? A verification failure with a correct declaration and satisfier means the verifier is wrong
- Dump the declaration alongside the execution trace — discrepancies between what was declared and what ran are the primary failure mode
- Check refinement-loop state — if regeneration is involved, log each iteration's inputs and outputs; unbounded loops hide inside "close enough" termination conditions
