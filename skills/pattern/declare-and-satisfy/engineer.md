---
layer: pattern
pattern: declare-and-satisfy
skill: engineer
---

# Declare-and-satisfy pattern — engineer contribution

Fills placeholders in `skills/global/engineer.md` for projects declaring the Declare-and-satisfy pattern.

---

## insert: do-bullets

- Persist the declaration before satisfying it — intent must be durable, not ephemeral
- Keep satisfier selection explicit — dispatch through a registry, not by branching on names
- Honor refinement budgets — if regeneration is allowed, the bound is a hard limit, not a suggestion

## insert: dont-bullets

- Don't let the satisfier mutate the declaration mid-run — declarations are inputs, not working state
- Don't skip verification when tests are green — verification checks the declaration-to-trace match, not just code correctness
