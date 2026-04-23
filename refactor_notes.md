# Forge Refactor — Working Notes

**Status:** Exploration. Not canonical.
**Started:** 2026-04-23

Notes toward a significant refactor of project-forge. Fleshed out as we go.

---

## What project-forge is

**Project-forge is a hybrid runtime project that creates patterned hybrid runtime projects based on an initial design spec.**

Recursive: forge is an instance of the thing it produces. FG-5 (self-bootstrap) is this property restated.

### Vocabulary

- **Project** (shorthand) — what `registry/projects.yaml` tracks
- **Hybrid runtime project** (formal) — dev-env and run-env share an environment; humans, LLMs, and deterministic code are co-resident actors; most have a deterministic-runnable core that can be published as a conventional app/library/executable
- **Pattern / patterns / patterned** — global term. Used in the Garlan & Shaw / POSA *architectural pattern* sense, not the GoF *design pattern* sense. "Architectural pattern" when full formality is needed; "pattern" everywhere else. `project_patterns_draft.md` owns the taxonomy.

### Publishing

Most hybrid runtime projects have a deterministic-runnable core. **Publishing** = the operation that extracts that core into a conventional app/library/executable/service. Not every project publishes; some are pure hybrid runtimes (forge itself, arguably). Publishing is a defined feature of the refactor, not an afterthought.

Open: is publishing one operation or several (extract-to-executable, extract-to-library, extract-to-service)?

---

## Scope

Top-level areas the refactor needs to address. Filled in as we go.

1. **Skills**
2. **Invariants**
3. **Guidelines** — could be code, writing rules, and possibly other types TBD
4. **Patterns** — axis-based typology of project patterns; per-project manifest declared at bootstrap drives tailoring
5. **Deployment, updates, and feedback** — bundled for now; may split into three
6. *(more to come)*

---

## Cross-cutting: the three layers

Skills, Invariants, and Guidelines all stratify into the same three layers of scope:

1. **Global** — applies to all hybrid runtime projects, regardless of pattern. Baseline-owned, universal.
2. **Pattern-attached** — applies to all projects declaring a given pattern. Baseline-owned, selected by the project's pattern manifest. "Retrieval is deterministic dispatch" → every KB project.
3. **Project-custom** — applies only to this project. Typically produced by LLM customization against the project's input spec / guidance doc. Not reusable across projects.

Layers 1 and 2 are template-owned and standardized. Layer 3 is the customization step.

**Empirical work to do:** audit existing skills, invariants, and guidelines and classify which layer each belongs in. Some will feel global but turn out to be pattern-attached; some will feel pattern-attached but are actually project-custom. This classification is how the template/customize split gets sharpened.

## Skills

**Skill** — a reusable prompt that triggers a consistent behavior from Claude. Every skill is produced by customizing a baseline-owned template against a specific project's declared pattern and context. The template enforces global standards; the customization layer adapts the skill to project specifics. A project carries only the skills appropriate to it.

Commitments:
- **Standards are global, expression is local.** Template owns what's non-negotiable; customization layer owns what bends per project.
- **Pattern-driven selection.** Which skills a project gets is a function of its declared pattern, not a hand-picked list.
- **Dogfooded.** Forge's own skills come from the same mechanism — no skill exists outside template + customize.

Skills stratify into the three layers (Global / Pattern-attached / Project-custom). See *Cross-cutting: the three layers*.

Sub-concerns:
- Local vs distributed — which skills live in the project vs in baseline/consumers
- Granularity of the standard/custom seam — may be section-level, may be statement-level; TBD

---

## Invariants

**Invariant** — a statement that must hold for the project to still be the project. Violation breaks the system — identity, correctness, or structural integrity. Logical and defensible, not preference-driven. "Registry is the single source of truth." "LLMs don't write into the KB corpus."

Invariants are the guardrails that define the project as a hybrid runtime project. They're load-bearing claims — the system is designed *around* them.

**Sorting test (counterfactual):** if this were violated, does the project still do its job?
- Yes, just messier → convention (lives in Guidelines)
- No, something essential is broken → invariant

Strength of feeling is not the test. A firmly-held preference is a convention, not an invariant. Don't promote on vibes.

### Two layers (first cut; more may emerge)

1. **Probabilistic-side invariants** — govern the LLM (and more broadly ML-driven) portions of the project. "LLMs don't write into the corpus." "Intent translation produces a persisted declarative artifact, not ephemeral state." "Synthesis must be grounded in what retrieval produced." These constrain how the non-deterministic layer is allowed to participate.

2. **Deterministic-side invariants** — govern the conventional code portions. "Registry is the single source of truth." "Dry-run before destructive operations." "No `shell=True`." Classical software invariants.

The two fail differently:
- Deterministic-side invariants are checkable by static analysis, tests, type systems.
- Probabilistic-side invariants are mostly enforced by pipeline structure (gates, guardrails, post-oracles) because the code that executes them isn't deterministic.

The most interesting invariants bridge the two — e.g., "LLM output must pass a deterministic check before proceeding." That bridge is where hybrid runtime projects are architecturally distinct from either classical apps or pure ML systems.

### Layering

Invariants stratify into the three layers (Global / Pattern-attached / Project-custom). See *Cross-cutting: the three layers*.

---

## Guidelines

**Convention / Guideline** — firm rules that make the project *ours*. Violation does not break the system; the project still works. Conventions are what give a codebase a single voice, consistent style, legible structure. They can be firm without being logically defensible as necessities — "because we agreed" is a valid reason, just a different kind of reason than an invariant has.

Guidelines are the space where conventions live.

### Two shapes

- **Statement-shaped convention** — expressible as a rule. "Commit messages start with a verb." Lives alongside invariants in form, differs in force.
- **Body-shaped standard** — a body of rules, examples, and worked-through complexity that can't collapse to a single statement. "Python coding standard." Used when we want examples, or when the subject is too complex to state cleanly.

A body-shaped standard can *contain* or *cite* invariants (e.g., a Python standard might embed "no `shell=True`"), but the standard itself is the scaffolding around rules, not the rules alone.

### Types (so far)

- Code guidelines — per-language or per-pattern conventions
- Writing rules — prose, doc, commit-message style
- *(more to come)*

### Layering

Guidelines stratify into the three layers (Global / Pattern-attached / Project-custom). See *Cross-cutting: the three layers*.

---

## Patterns

Substrate lives in `project_patterns_draft.md`. Axis-based typology: a project is described by its position on a small number of composable axes, with named patterns (Compiler, Declare-and-satisfy, KB, Bracketed-probabilistic) as shorthand for recurring combinations.

Role in the refactor: a per-project sub-pattern manifest declared at bootstrap, so the baseline tailors capabilities, invariants, guidelines, and skills to the declared pattern.

*(To be filled in — how the manifest is expressed, how it drives tailoring, per-subsystem patterns for hybrid projects.)*

---

## Deployment, rebase, and feedback

*(To be filled in. Bundled provisionally; may split into three sections. Rough framing: deployment is the initial materialization of a project from forge; rebases are how an existing project picks up baseline changes; feedback is how observations from projects flow back to inform baseline evolution.)*

---

## Related inputs (not the spine)

- `project_patterns_draft.md` — axis-based typology of project patterns. A driver, but not the organizing backbone of the refactor. Important and driving, but one piece of the puzzle.

---

## Open questions

- Publishing: one operation or several?
- Harness sorting edge cases and precedence rules
- Whether skill templating and bootstrap should share one mechanism
- How input-spec fidelity is handled (clarify vs infer)

---

## Next

Work outward from the definition — likely next: what "patterned" means operationally (how the design spec determines the pattern), and what "creates" entails (bootstrap pipeline structure).
