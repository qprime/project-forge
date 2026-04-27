---
layer: pattern
pattern: compiler
skill: engineer
---

# Compiler pattern — engineer contribution

Fills placeholders in `skills/global/engineer.md` for projects declaring the Compiler pattern.

---

## insert: do-bullets

- Keep conversions going through the IR — do not add direct input-to-output paths, even "just this once"
- Keep generators pure — same input, same output, no hidden state
- Put validation at the boundary it belongs to (AST boundary vs IR boundary vs output boundary); don't migrate it across layers

## insert: dont-bullets

- Don't add computed output-shape state to semantic dataclasses — it belongs in the generator, not the IR
- Don't introduce a second IR alongside the canonical one without explicit architectural decision
