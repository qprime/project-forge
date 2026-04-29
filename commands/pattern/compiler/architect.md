---
layer: pattern
pattern: compiler
command: architect
---

# Compiler pattern — architect contribution

Fills placeholders in `commands/global/architect.md` for projects declaring the Compiler pattern. Sections below name the placeholder they fill.

---

## insert: context-discovery-extras

5. IR definition — the intermediate representation all conversion passes through
6. Generator / codegen module — pure functions producing output from IR

## insert: investigate-anchors

Three layers are the units of architectural reasoning — always ask which layer a concern lives in before proposing changes:

- **Input / AST** — parsing, surface syntax, validation of the input language
- **IR** — the single intermediate form all downstream work operates on
- **Codegen** — pure generators producing the output artifact

Direct input-to-output conversion that bypasses the IR is a topology change, not a local edit. Name it as such.
