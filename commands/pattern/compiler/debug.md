---
layer: pattern
pattern: compiler
command: debug
---

# Compiler pattern — debug contribution

Fills placeholders in `commands/global/debug.md` for projects declaring the Compiler pattern.

---

## insert: do-bullets

- Bisect by layer — is the bug in parsing, in the IR, or in codegen? Work top-down or bottom-up, but name the layer before fixing
- Check generator purity — if output varies for the same input, the bug is a hidden-state leak, not a logic error
- Check IR shape at the boundary — dump the IR for the failing case and compare against a working case
