---
layer: pattern
pattern: kb
command: engineer
---

# KB pattern — engineer contribution

Fills placeholders in `commands/global/engineer.md` for projects declaring the KB pattern.

---

## insert: do-bullets

- Keep retrieval deterministic — dispatch against structured coordinates, not similarity scores
- Keep stage boundaries clean — retrieval returns entries, assembly builds the frame, synthesis produces prose
- Ground synthesis in what assembly produced — ungrounded generation is a structural error, not a quality issue

## insert: dont-bullets

- Don't let LLMs write into the corpus — the authorship boundary is invariant-level
- Don't collapse retrieval and synthesis into one step for convenience — stage separation is the point
