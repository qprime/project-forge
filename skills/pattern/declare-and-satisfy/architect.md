---
layer: pattern
pattern: declare-and-satisfy
skill: architect
---

# Declare-and-satisfy pattern — architect contribution

Fills placeholders in `skills/global/architect.md` for projects declaring the Declare-and-satisfy pattern. Sections below name the placeholder they fill.

---

## insert: context-discovery-extras

5. Declaration / spec format — the persisted declarative artifact that drives execution
6. Satisfier / executor — the deterministic component that realizes the declaration
7. Verifier / post-oracle — the check that confirms the declaration was satisfied

## insert: investigate-anchors

Three components are the units of architectural reasoning — always ask which one a concern lives in before proposing changes:

- **Declaration** — persisted artifact, the single source of intent; authored by human or LLM but treated as data once written
- **Satisfaction** — deterministic execution that realizes the declaration
- **Verification** — post-hoc check that what ran matches what was declared

Proposals that let satisfaction feed back into declaration mid-run are topology changes. Name them as such.

## insert: domain-bullets

- Check declaration persistence — does intent get written to a durable artifact before execution, or is it ephemeral? Ephemeral intent breaks re-execution and debugging.
- Check refinement boundaries — if regeneration is allowed, is the loop bounded? Unbounded refinement is an invariant violation, not a performance concern.
- Check verification grounding — does the verifier check against the declaration, or against the execution trace? Checking against the trace alone means you can't catch satisfier bugs.
- Check dispatch explicitness — does selection among satisfiers happen through an explicit registry, or by branching on names? Implicit dispatch rots.
