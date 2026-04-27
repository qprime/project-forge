---
layer: pattern
pattern: compiler
skill: architect
---

# Compiler pattern — architect contribution

Fills placeholders in `skills/global/architect.md` for projects declaring the Compiler pattern. Sections below name the placeholder they fill.

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

## insert: domain-bullets

- Check the IR path — does this proposal add a conversion route that skips the IR? If yes, it's a structural change, not an optimization.
- Check generator purity — same input, same output, no hidden state. Memoization and caching must preserve this contract or declare themselves.
- Check layer leaks — computed output-shape state belongs in codegen, not on semantic dataclasses. If planner-layer fields appear on the IR, flag it.
- Check input validation placement — validation that belongs at the AST boundary should not migrate into the IR or codegen.
