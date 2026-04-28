---
layer: pattern
pattern: kb
skill: architect
---

# KB pattern — architect contribution

Fills placeholders in `skills/global/architect.md` for projects declaring the KB pattern. Sections below name the placeholder they fill.

---

## insert: context-discovery-extras

5. Corpus root — the structured artifact that retrieval dispatches against
6. Retrieval configuration — structural coordinates (persona, skill, topic, scope) and their mappings to entries

## insert: investigate-anchors

Four stages are the units of architectural reasoning — always ask which stage a concern lives in before proposing changes:

- **Storage** — corpus schema, authorship rules, revision policy
- **Retrieval** — deterministic dispatch, query coordinates, fallback behavior
- **Context Assembly** — frame construction, ordering, citation encoding
- **Guardrailed Synthesis** — grounding, citation compliance, refusal

Cross-stage proposals (e.g., "let synthesis trigger more retrieval") are topology changes, not local edits. Name them as such.
