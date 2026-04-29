---
layer: pattern
pattern: kb
---

# KB Pattern Invariants

Invariants for projects declaring the KB (knowledge-base) pattern. KB projects organize an accumulating corpus into four stages — storage, retrieval, assembly, synthesis — though not all four are necessarily built; some may be performed by humans reading the corpus directly.

KB projects carry GL-2 (non-deterministic output carries provenance) from the global layer; it is the load-bearing global invariant for a corpus where every claim must trace to a source. Other code-side globals (GL-1, GL-3, GL-4, GL-5, GL-6) are carried only when the KB has built stages with code; the default KB profile assumes notes-first authoring and omits them. Projects with built synthesis or retrieval pipelines add the relevant globals back at the manifest layer.

Each invariant has:
- **Rule** — the constraint
- **Failure mode** — what breaks when it's violated
- **Type** — `code-side` (checkable by tests or static analysis), `llm-side` (enforced by pipeline structure: gates, guardrails, post-oracles), `bridge` (LLM output must pass a deterministic check before proceeding), or `authoring-side` (enforced at content-authoring time, by humans or LLMs writing into the corpus)

---

## KB-1 — Retrieval is deterministic

Retrieval over the corpus produces the same result set for the same query, against the same corpus state. Probabilistic retrieval (vector similarity over learned embeddings without a deterministic top-k cutoff and tiebreaker, fuzzy matching without explicit ordering, LLM-as-retriever) is not retrieval in this pattern — it is synthesis with retrieval-shaped framing.

**Failure mode:** the same question returns different evidence on different runs; downstream synthesis cannot be reproduced; the corpus stops behaving like a knowledge base and starts behaving like a generator.
**Type:** code-side (when retrieval is built); authoring-side (when retrieval is humans navigating file structure — the structure must be navigable by deterministic rules, not by aesthetic browsing)

---

## KB-2 — Synthesis is bound to retrieved evidence

Synthesized output cites the retrieved entries it draws from. A claim that does not trace to a retrieved entry is not a synthesis output; it is a hallucination wearing synthesis clothes. The binding is enforced by an oracle (post-check that citations resolve, that cited content supports the claim) or by the synthesis prompt's structural constraints, not by hope.

**Failure mode:** the corpus appears to ground LLM output but actually launders ungrounded generation through citation-shaped formatting; users trust output that has no provenance.
**Type:** llm-side (synthesis prompt structure); bridge (post-oracle citation check); authoring-side (when synthesis is humans reading and writing — the human is the oracle, but the discipline must be explicit)

---

## KB-3 — Storage is accumulating, not mutating

The corpus grows by addition. Existing entries are revised in place only when the underlying claim was wrong; a *new perspective* on an existing topic is a new entry, not an edit. Mutating-current updates collapse the corpus's history of understanding into a single point-in-time view, which makes "what did we think about X six months ago" unanswerable.

**Failure mode:** the corpus loses its temporal dimension; older retrieved entries silently change meaning; review and audit become impossible.
**Type:** authoring-side (enforced by the act of authoring; no code can prevent a destructive overwrite, but the discipline is part of how the project treats its corpus)

---

## KB-4 — Stage boundaries do not leak

When stages are built (any of retrieval, assembly, synthesis exist as code), each stage owns its inputs and outputs. Synthesis does not reach back into raw storage; retrieval does not call out to synthesis; assembly does not mutate stored entries. The four-stage decomposition is what lets a KB be reasoned about — collapsing the boundaries collapses the pattern.

**Failure mode:** a stage's behavior depends on side effects from another stage's internals; changing one stage breaks another in non-obvious ways; the project becomes one large stage with four labels.
**Type:** code-side (when stages are built); not applicable (when all stages are humans-only — humans inherently re-enter, but the failure mode applies when stages are partially built)

---

## Notes for project layer

Projects declaring the KB pattern should consider, at the manifest layer:

- **Which stages are built vs. human-only.** A `notes-first` KB has none built; a typical RAG-replacement has retrieval and synthesis built, assembly minimal. The set affects which globals re-enter (a synthesis-built KB carries GL-3, GL-4, GL-5).
- **Citation format.** KB-2 requires citations resolve; the project layer specifies the format (e.g., `[source-id:section]`, link to entry path) so downstream tooling can check.
- **What counts as a corpus entry.** A markdown file? A YAML frontmatter block? A row in a structured store? The pattern is agnostic; the project layer commits.
