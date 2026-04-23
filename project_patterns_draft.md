# Project Patterns — Working Draft

**Status:** Exploration, not canonical. Do not consume from `baseline/`.
**Started:** 2026-04-22
**Last revision:** 2026-04-22 — restructured around composable axes after architect critique; KB pattern promoted to first-class peer with its own four-stage interior.

This document captures an emerging taxonomy of project *shapes* across the
forge ecosystem. The taxonomy is composable: a project is described by its
position on a small number of axes, not by membership in a named type.
Pattern names exist only as shorthand for recurring combinations.

The goal is a per-project sub-pattern manifest declared at bootstrap, so the
baseline can tailor capabilities to the declared shape.

---

## Origin

Pulled out of a conversation contrasting four projects:

- `applied-math-ml` — KB / study notes
- `mill_ui` — declarative compiler with LLM-as-interface
- `relay` — declare-and-satisfy: spec is the verification target
- `image-forge` — declarative input + external probabilistic generator

The seed insight: mill_ui's IR is **load-bearing as a gate before
production**, while relay's spec is the **verification target after
production**. That asymmetry — verification position relative to
production — is the first axis worth naming, and it generalizes far
beyond those two projects.

---

## Axes

A project is fully described by where it sits on these six axes. Pattern
names are shorthand for recurring combinations of axis values; they are
never the primary description.

### 1. Intent-translation layer

Whether a formalized layer translates natural-language intent into the
declarative artifact, and what produces the artifact.

- **Absent** — humans hand-author the declarative artifact directly
- **Present, LLM-mediated** — conversation produces the artifact (mill_ui, relay)

The architectural commitment is whether intent translation is a *layer*
of the system, not whether humans ever speak natural language.

### 2. Declarative artifact

The structured, persisted, authoritative contract the rest of the system
acts on. Three sub-properties:

- **Format** — YAML, TOML, custom DSL, structured markdown, etc.
- **Authorship rule** — who can write into it (humans only, LLM through translation, both)
- **Mutability** — append-only, mutable-current, immutable-versioned, snapshotted

Authorship rule is a trust boundary. KB's commitment that "LLMs read but
do not write into the corpus" is an authorship-rule statement.

### 3. Production sub-pipeline

How the declarative artifact becomes the implementation or output.
Production is *not atomic*. It is a pipeline with its own internal
structure.

Each **stage** is classified along two dimensions:

- **Mechanism** — deterministic-internal / LLM-authored-code / external-probabilistic-call / LLM-judgment / deterministic-retrieval
- **Output** — code / data / output-artifact / context-frame

The pipeline as a whole has a **topology**:

- **Linear** — stages chain end-to-end (mill_ui's compiler stages)
- **Branching** — alternative paths chosen at runtime (penumbra-poc's router)
- **Feedback-loop** — generate → assess → adjust → regenerate (the **refinement loop** primitive; relay's spec-fail-then-retry, image-forge's planned LLM-judge enhancement)
- **Query-driven** — production runs per-request rather than build-time (KB)

Topology is an architectural commitment, not an implementation detail.
Choosing query-driven means the project is interactive; choosing
feedback-loop means the project tolerates iteration latency.

### 4. Verification

Two independent sub-properties: where verification sits relative to
production, and what failing verification does.

**Position:**

- **Pre-gate** — artifact must be valid before next stage runs
- **Post-oracle** — implementation runs, evaluator checks against declaration
- **In-loop** — verification feeds back into a refinement loop
- **Human-review** — output is judged by a human looking at it
- **None** — no verification in the pipeline

**Consequence:**

- **Block** — pipeline stops, error surfaces
- **Regenerate** — failure triggers another production attempt
- **Flag** — failure annotates output but does not stop it
- **Log** — failure is recorded for later analysis

Position and consequence are independent. Post-oracle + block (relay
test fails, exits nonzero) is different from post-oracle + regenerate
(relay in iterative mode), and both are different from post-oracle +
flag (CI annotation).

### 5. State

What the project carries across invocations:

- **None** — pure transformation, no persistence between runs
- **Mutable-current** — single current state that evolves (image-forge's `image.png`)
- **Monotonic-append** — append-only history (image-forge's `history/`)
- **Snapshotted** — periodic captures of current state
- **Immutable-versioned** — every change is a new version, old versions persist
- **Accumulating-corpus** — domain-structured collection that grows (KB's storage)

Most projects have multiple state kinds in different subsystems
(image-forge: mutable-current for the consumer-facing path, monotonic-
append for history). State is a per-subsystem property, but the project
declares its dominant kind.

### 6. Downstream contract surface

What this project exposes to other projects or to humans downstream:

- **Formal-binary** — bit-precise binary format (image-forge's 16-bit grayscale PNG)
- **Formal-text** — bit-precise text format (mill_ui's G-code)
- **Structured-data** — schema'd data with stable field semantics
- **Informal-prose** — synthesized natural language (KB query responses)
- **None** — the project is consumed by humans only, no machine downstream

The contract surface determines what changes are breaking and how
verification has to be designed to protect downstream consumers.

---

## Patterns as combinations

These are shorthand labels for recurring axis combinations. The axes are
the primary description; the names are convenience.

### Compiler

Intent-translation typically present. Declarative artifact human- or
LLM-authored. Production is a linear sub-pipeline of deterministic-
internal stages producing code. Verification is pre-gate with block
consequence at IR boundaries. State is mutable-current per project.
Contract is formal (text or binary).

Example: mill_ui (PML → RemovalIntent → G-code).

### Declare-and-satisfy

Intent-translation present. Declarative artifact doubles as the
verification predicate — the spec *is* what you check against.
Production is LLM-authored-code. Verification is post-oracle (the
implementation is run and checked). Consequence is block or regenerate
depending on mode. Implementation is disposable: regenerable from the
spec, never edited by humans. Contract surface is the verified behavior
itself.

Example: relay (NL → task spec → ST function blocks → simulated trace
→ assertion check).

### Bracketed probabilistic

Intent-translation often absent — humans author the spec directly.
Production sub-pipeline brackets an external-probabilistic-call with
deterministic-internal stages on either side (preprocess and post-
process). Verification is human-review on the output. State is mutable-
current plus monotonic-append for reproducibility. Contract surface is
formal-binary or formal-text for downstream consumption.

This pattern naturally evolves toward a refinement-loop topology as the
post-processing pipeline grows and gains LLM-judgment stages.

Example: image-forge (image.yml → GPT Image 2 → enhancement chain →
heightmap PNG).

### KB

A first-class pattern with its own four-stage interior. See next
section.

---

## The KB pattern

A KB project is built around a four-stage cycle that runs per-request:

```
Storage  ──▶  Retrieval  ──▶  Context Assembly  ──▶  Guardrailed Synthesis
  ▲                                                          │
  └──────────── (humans author entries) ────────────────────┘
```

KB is not RAG. RAG retrieves by embedding similarity and stuffs top-k
chunks into context, hoping the LLM grounds. KB rejects that. Retrieval
is **deterministic dispatch against a structured corpus**. The corpus
is queryable as a structured artifact, not searchable as a blob. The
probabilistic step is *only* the synthesis at the end, and even that is
bounded by what the deterministic stages produced.

The closer prior art is expert systems and structured knowledge bases
(MYCIN, CYC) and faceted classification from library science, not RAG.

### Stage 1 — Storage

The corpus is a structured artifact. Authoring an entry is a commitment:
where in the structure it lives, which personas or skills it serves,
what other entries it cites, what scope it covers.

The storage stage is a declarative artifact (axis 2) with state kind
accumulating-corpus (axis 5) and an authorship rule that excludes LLMs
from writing.

Open development areas:
- Authoring rules — what schema must an entry satisfy on write
- Revision policy — when entries can change, who approves, how citing entries are notified
- Structural taxonomy — the dimensions an entry must declare itself along (persona, skill, topic, scope)

### Stage 2 — Retrieval

Deterministic dispatch. Given a query that includes structural
coordinates (persona, skill, context), retrieval produces a set of
corpus entries by explicit mapping — not similarity. Fuzzy matching, if
present at all, is a fallback after the deterministic dispatch returns
nothing, and it is logged as a degraded retrieval path.

In axis terms, retrieval is a production stage with mechanism
deterministic-retrieval and output context-frame contributors.

Open development areas:
- Query shape — what coordinates are mandatory vs optional
- Composition rules when multiple mappings hit
- Failure semantics when no mapping hits (degrade or refuse)

### Stage 3 — Context Assembly

A first-class stage, distinct from retrieval. Retrieval produces
*entries*; assembly produces the *frame* the synthesis stage receives.
This is where ordering, summarization, prioritization, and slot-filling
happen.

Mechanism is typically deterministic-internal (templates, fixed slots)
but can include LLM-judgment stages (e.g., an LLM ranking which of N
retrieved entries best fit the question).

Open development areas:
- Template-based vs flexible assembly
- Whether assembly itself can refuse (entries retrieved but assembly
  cannot produce a coherent frame)
- How citations are encoded into the frame so synthesis can preserve them

### Stage 4 — Guardrailed Synthesis

The only probabilistic stage. Constrained by what assembly produced and
by explicit rules about citation, grounding, scope, and refusal.

In axis terms, synthesis is a production stage with mechanism LLM-
authored-code (where the "code" is prose) and verification position
post-oracle: the synthesis output is checked against the assembled
frame for grounding and citation compliance.

Open development areas:
- What "guardrailed" means concretely — prompt-level constraints,
  post-generation validation, response shape contracts, refusal
  behaviors, or some composition
- How ungrounded claims are detected and handled (block, flag,
  regenerate)
- Whether synthesis can ask for additional retrieval mid-generation
  (would change topology from linear-per-request to feedback-loop)

### KB on the axes

| Axis | KB position |
|---|---|
| Intent-translation | Present — query is NL, translated to structural coordinates |
| Declarative artifact | The corpus itself; structured markdown or similar; authored by humans only; mutability is accumulating-corpus |
| Production sub-pipeline | Query-driven topology, four stages: deterministic-retrieval → deterministic-internal assembly → LLM-authored synthesis |
| Verification | Post-oracle on synthesis (citation/grounding check); consequence depends on policy |
| State | Accumulating-corpus for storage; none for per-request execution |
| Downstream contract surface | Informal-prose (the synthesized response) |

KB is a peer pattern, not a special case. The reason it looked
mismatched in earlier drafts was the assumption that production must
be build-time and atomic. Once production is allowed to be a sub-
pipeline with query-driven topology, KB fits naturally.

### KB instances

- `applied-math-ml` — single-persona, deterministic-first via file
  structure, synthesis stage not yet built (humans read directly).
  Storage and retrieval committed; assembly and synthesis are open.
- `tennecnc_llc` — `[doc-corpus, multi-persona]`, multi-persona
  retrieval is the load-bearing distinction
- *recipes project (planned)* — multi-persona, skills-based
  deterministic dispatch, full four-stage pipeline

---

## Project mappings

| Project | Pattern | Intent-trans. | Production topology | Verification | State (dominant) | Contract |
|---|---|---|---|---|---|---|
| `applied-math-ml` | KB | absent (notes mode) | query-driven (partial) | none yet | accumulating-corpus | none / human-read |
| `mill_ui` | Compiler | present | linear | pre-gate, block | mutable-current | formal-text (G-code) |
| `relay` | Declare-and-satisfy | present | linear, refinement-loop in iterative mode | post-oracle, block or regenerate | mutable-current (specs) | informal (PLC behavior) |
| `image-forge` | Bracketed probabilistic | absent | linear, evolving toward refinement-loop | human-review | mutable-current + monotonic-append | formal-binary (16-bit PNG) |

---

## Prior art

**Direct ancestors with substantive overlap:**

- **Garlan & Shaw architectural styles** (1996) — pipe-and-filter ≈ Compiler topology; blackboard architectures ≈ KB synthesis structure
- **Refinement calculus** (Back, Morgan, late 80s/90s) — Declare-and-satisfy is a refinement calculus where the LLM is the refinement engine. Provides the vocabulary (specification, refinement, derived implementation) that the pattern needs.
- **Program synthesis / CEGIS** (counterexample-guided inductive synthesis) — the refinement-loop primitive is CEGIS. Generate → check → counterexample → regenerate.
- **Model-driven engineering / OMG MDA** (early 2000s) — declarative artifact + production-as-transformation. PML → G-code is a model transformation in MDA terms.
- **Generative programming** (Czarnecki & Eisenecker 2000) — declarative configuration → generated code via templates. Same shape as Declare-and-satisfy with a different production mechanism.
- **Expert systems and structured knowledge bases** (MYCIN, CYC, 1970s–80s) — KB pattern's deterministic-dispatch retrieval is the expert-systems lineage, not the RAG lineage. The "guardrailed synthesis" stage is what's new; the disciplined retrieval is older than RAG by 30+ years.
- **Faceted classification** (library science, Ranganathan onward) — KB's structural commitment that an entry declares itself along multiple dimensions is faceted classification.
- **Software product lines and feature models** (SEI, Clements & Northrop) — the per-project sub-pattern manifest declared at bootstrap is feature modeling. This is the closest direct ancestor of the meta-move.
- **Feature-Oriented Software Development** — composable features defining product variants; same structural idea applied to AI-collaborative project shapes.

**Not RAG.** The KB pattern is sometimes mistaken for RAG. RAG retrieves
probabilistically and hopes the LLM grounds. KB retrieves
deterministically and binds the LLM to what was retrieved. These are
opposite architectural stances.

---

## What's genuinely new

Whole-application patterns are not new. Architectural styles, reference
architectures, and DDD all classify whole applications. What's new here
is the *axis of classification*:

1. **Verification position relative to production, under LLM authorship.**
   Pre-LLM, this distinction had no architectural weight — production
   was always deterministic, so verification was always "tests after the
   fact." Once production becomes probabilistic, pre-gate vs post-oracle
   vs in-loop vs human-review become real architectural commitments with
   different operational consequences.

2. **Disposable implementation as operational reality.** Refinement
   calculus had this as theory: programs derived from specs are
   throwaway in principle. Until LLMs, regeneration cost made it false
   in practice. Now it is a real design choice — relay commits to
   humans never reading the ST.

3. **Intent-translation as a recurring architectural primitive.**
   Natural-language interfaces existed as a specialty (NL databases,
   conversational UIs). What's new is intent translation as a *layer*
   that recurs across project shapes, with the same structural
   commitments each time: ephemeral NL in, persisted declarative
   artifact out.

4. **Per-project sub-pattern manifest at bootstrap.** Feature models
   for AI-collaborative project shapes. The user-facing payoff: declare
   the manifest and the baseline tailors capabilities, invariants, and
   agent behaviors to the declared shape. This is the move that justifies
   the rest of the taxonomy.

---

## Open questions

- **Hybrid projects.** `penumbra-poc` reads Compiler-shaped (declarative
  TOML, deterministic pipeline) but its routing/confidence thesis is
  closer to Declare-and-satisfy at the model level. Likely answer: the
  patterns are per-subsystem, not per-project, and a project's manifest
  declares the dominant pattern plus per-subsystem exceptions.

- **Bootstrap manifest schema.** What does a per-project sub-pattern
  manifest actually look like? YAML in `registry/projects.yaml`?
  A separate file? How does the baseline consume it to tailor
  capabilities?

- **KB stage interiors.** Each of the four KB stages has open
  development areas (see KB section). The user is actively expanding
  these; expect this section to grow.

- **Refinement loop as a shared primitive.** It appears in Declare-and-
  satisfy (relay) and in the evolved Bracketed-probabilistic (image-
  forge with LLM-judge). It may also appear in KB if synthesis can ask
  for additional retrieval mid-generation. Worth tracking whether it
  becomes a first-class topology label or stays a recurring shape.
