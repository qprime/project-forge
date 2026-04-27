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

## insert: domain-bullets

- Check retrieval discipline — is retrieval deterministic dispatch against structured coordinates, or has it drifted toward similarity search? Embedding-based retrieval is out of scope.
- Check authorship boundary — does the proposal preserve "LLMs read but do not write into the corpus"? Authorship violations are invariant-level, not stylistic.
- Check grounding contract — does synthesis remain bounded by what assembly produced? Ungrounded generation is a structural violation, not a quality issue.
- Check stage boundaries — retrieval produces entries, assembly produces the frame, synthesis produces prose. Collapsing two stages into one is a structural change worth naming.
