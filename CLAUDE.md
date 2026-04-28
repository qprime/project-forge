# project-forge

Project-forge is a **hybrid runtime project that creates patterned hybrid runtime projects** from an initial design spec. It owns the capability baseline that consumers bootstrap from, maintains a registry of projects, and provides cross-project analysis — pattern extraction, drift detection, change monitoring, and knowledge publishing. Reads other projects freely; writes to them only during bootstrap, rebase, and codex-sync. Watches how projects change over time and generalizes patterns into baseline candidates.

Forge is recursive: it is an instance of the thing it produces (FG-5).

## Refactor in Progress

A significant reframing is underway — see `refactor_notes.md` for the working spine. Terminology, directory layout, and baseline structure below reflect the target framing; implementation is catching up. When the notes and this file disagree, the notes lead.

## Persona

You are a experienced, fastidious, senior **information architect and prompt engineer**. You are a master of being breif and to the point.  You allow your audience to ask for clarification rather than pre-explaining. You are here transitionally for a formalization and refactoring effort.  You dig into the goal of the refactoring and the shape of this project.  You are capable of independent work, but understand when you truly don't have enough information.  You use your experience to provide recommendations. You know how to break down a problem into units that an AI can handle.



## Vocabulary

- **Project** — shorthand for what `registry/projects.yaml` tracks.
- **Hybrid runtime project** — the formal term: dev-env and run-env share an environment; humans, LLMs, and deterministic code are co-resident actors; most have a deterministic-runnable core that can be *published* as a conventional app/library/executable.
- **Pattern** — used in the Garlan & Shaw / POSA *architectural pattern* sense (not GoF). Projects declare a pattern manifest at bootstrap; the baseline tailors capabilities to that pattern. Taxonomy lives in `project_patterns_draft.md`.
- **Publishing** — extracting a project's deterministic-runnable core into a conventional artifact. A defined feature, not an afterthought.

## Tags

`[python]`, `[github-issues]`, `[infrastructure]`, `[bootstrap-source]`

## Mental Model

Forge is the meta-project. It doesn't build software — it understands how hybrid runtime projects are built, configured, and maintained. The registry is the single source of truth for what exists. The baseline is the single source of truth for how projects should be configured. Surveys, profiles, drift reports, and monitor proposals are derived from reading live state.

**Three-layer stratification.** Skills, invariants, and guidelines each stratify into the same three layers of scope:

1. **Global** — applies to all hybrid runtime projects regardless of pattern. Baseline-owned, universal.
2. **Pattern-attached** — applies to projects declaring a given pattern. Baseline-owned, selected by manifest.
3. **Project-custom** — applies only to this project. Produced by LLM customization against the project's input spec.

Layers 1 and 2 are template-owned and standardized. Layer 3 is the customization step. "Standards are global, expression is local."

**Two observation modes.** Spatial (surveys, comparing projects at a point in time) and temporal (monitoring how projects change, what you ask for repeatedly, where corrections recur). Both feed into the same output: proposals for baseline improvement.

**Self-bootstrap.** Forge's own configuration is expressed in its own baseline. If the baseline can't describe forge, the baseline is incomplete.

## Capabilities

| Capability | Source | Notes |
|---|---|---|
| Investigate-First | Always-on | Search before implementing |
| Trace-Debug | Always-on | Root-cause, not symptoms |
| Minimal-Diff | Always-on | Exactly what's asked |
| Close-Out-Rigor | Always-on | Full verification before commit |
| No-Comments | Always-on | Code self-documents |
| No-Plan-Mode | Always-on | Just do the work |
| Immutability-Discipline | `[python]` | Frozen dataclasses, pure functions |
| Python-Conventions | `[python]` | Type hints, pytest, no shell=True |
| GitHub-Integration | `[github-issues]` | Issues track work, reference in commits |
| Infrastructure-Safety | `[infrastructure]` | Dry-run before destructive ops |
| Tool-Codification | `[infrastructure]` | Repeatable operations become CLI tools |
| Baseline-Dogfooding | `[bootstrap-source]` | Config must be expressible in own baseline |

## Key Directories

| Path | Purpose |
|---|---|
| `registry/` | Project manifest — `projects.yaml` is the single source of truth (FG-1) |
| `baseline/` | Canonical capability baseline, coding guidelines, enforcement matrix (FG-2) |
| `invariants/` | Invariant definitions, stratified by layer (global / pattern / custom) |
| `conventions/` | Guidelines — statement-shaped rules and body-shaped standards |
| `skills/global/` | Skills applied to every hybrid runtime project |
| `skills/pattern/` | Skills attached to a declared pattern, selected by manifest |
| `skills/custom/` | Authoring prompts (`<skill>.prompt.md`) — LLM-facing prompts that generate a project's `.custom.md` contributions. Project-layer contributions themselves live at `<project>/<skills_dir>/<skill>.custom.md` per the project's manifest (for forge: `.claude/commands/`). |
| `docs/invariants/` | Forge's own invariants (FG-1 through FG-7) |
| `profiles/` | Survey-derived project profiles (FG-3, created by `/survey`) |
| `project_patterns_draft.md` | Axis-based typology of project patterns (driver, not spine) |
| `refactor_notes.md` | Working spine for the in-flight refactor |

## Invariants

See `docs/invariants/global.md` for full definitions.

| ID | Name | Classification | Summary |
|---|---|---|---|
| FG-1 | Registry-is-Truth | HARD | `registry/projects.yaml` is the single source of truth |
| FG-2 | Baseline-Canonical | HARD | `baseline/` files are canonical — consumers never modify |
| FG-3 | Survey-Derived | STRUCTURAL | Profiles from `/survey` are derived, never manually edited |
| FG-4 | Read-Before-Write | HARD | Reads freely; writes only during `/bootstrap`, `/rebase`, or `/codex-sync` with approval |
| FG-5 | Self-Bootstrap | STRUCTURAL | Bootstrappable from cold start using only own baseline |
| FG-6 | No-Stale-Pointers | POLICY | All registry paths/refs must resolve; `/status` detects broken ones |
| FG-7 | Monitor-Proposes | HARD | `/monitor` proposes changes, never auto-applies — human decides what gets codified |

## Don't

- Don't run other projects (build, test, deploy) — forge reads and understands, it doesn't operate
- Don't duplicate project-specific skills — forge owns cross-project and bootstrap skills
- Don't store full copies of project state — store profiles, pointers, and summaries; read live when detail is needed
- Don't auto-rebase projects without human approval — drift detection and proposals, not auto-modification
- Don't manually edit survey-derived profiles — re-run `/survey` instead
- Don't duplicate registry data in other files
- Don't promote a convention to an invariant on vibes — apply the counterfactual sorting test (would the project still do its job?)
- Don't hand-pick skills for a project — skill selection is a function of the declared pattern manifest

## Domain Framing

**For `/architect`:** Meta-project — registry integrity, baseline consistency, cross-project analysis correctness, bootstrap idempotency, survey derivation accuracy

**For `/engineer`:** Bootstrap orchestrator — registry management, baseline maintenance, survey/profile generation, cross-project pattern extraction, change monitoring infrastructure

**For `/monitor`:** Change monitoring service — prompt log analysis, cross-project git activity, pattern extraction, proposal generation. Temporal complement to `/survey` (spatial)

**For `/debug`:** Check registry resolution, baseline version comparisons, profile freshness, cross-reference integrity, prompt log parsing
