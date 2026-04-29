---
layer: pattern
pattern: compiler
command: spec
---

# Compiler pattern — spec contribution

Fills placeholders in `commands/global/spec.md` for projects declaring the Compiler pattern.

---

## insert: design-extras

- **Layer touched**: state whether the change is in parsing/AST, in the IR, or in codegen. Changes crossing multiple layers must name each layer's change separately.

## insert: testing-strategy-extras

- **Purity check**: any generator change needs a test confirming same input produces same output across repeated calls.
- **IR snapshot**: changes that affect IR shape should include a test that pins the IR for a reference input.
