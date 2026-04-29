# project-forge

A system that creates and updates **hybrid runtime projects** — projects in which deterministic code, LLMs, and humans are co-resident actors. Forge takes a description (or an existing codebase) and produces a project; later, given that project's manifest, forge re-applies the baseline.

Forge standardizes the *structure and content* of three artifact types — **commands**, **invariants**, **conventions** — across **three layers** — **global**, **pattern**, **project** — for a small set of project types.

## What forge is for

A hybrid runtime project carries three things every developer (human or AI) needs to read before working in it:

- **Commands** — agent personas invoked by `/<name>` (e.g. `/architect`, `/review`, `/spec`). They define how the agent behaves for a given task.
- **Invariants** — load-bearing rules. Violating them breaks the system.
- **Conventions** — guidelines for consistency. Violating them doesn't break the system; the project still works, but readers and reviewers diverge.

Without forge, every project authors all three from scratch. They drift. The same persona looks different across projects. The same "no silent drops" invariant gets re-stated five different ways. Reviewers and AI agents can't carry skills across projects because the surface keeps changing.

Forge fixes that by **owning the standard parts and letting projects customize only what's actually project-specific.**

## The three-layer model

Each artifact type is composed from three layers:

| Layer | Scope | Authored where | Authored by |
|---|---|---|---|
| **Global** | All projects | `commands/global/`, `invariants/global.md`, `conventions/global/<lang>.md` | Human, in this repo |
| **Pattern** | Projects declaring a given pattern | `commands/pattern/<name>/`, `invariants/pattern/<name>.md`, `conventions/pattern/<name>/<lang>.md` | Human, in this repo |
| **Project** | One specific project | The project's `.forge/manifest.yaml` | LLM, against the project's description |

**Standards are global, expression is local.** Layers 1 and 2 are stable, baseline-owned, and standardized. Layer 3 is the customization step — the LLM reads the project's description and fills in slots and inserts that adapt the standardized scaffold to the specific project.

This is what makes the system creatable from prose. The LLM is not generating a whole project from scratch; it is *customizing* a known scaffold against a description. The scaffold carries everything project-independent.

## Patterns

A **pattern** is a reusable project shape (Compiler, KB, Bracketed-probabilistic, etc., per Garlan & Shaw / POSA, not GoF). A project declares its primary pattern in its manifest. The pattern selects which layer-2 content applies.

Patterns are how forge serves "a few project types" without collapsing to either "one universal template" or "every project is bespoke." Taxonomy lives in `project_patterns_draft.md`.

## The two operations

### `forge create <project>`

Inputs: a description of the project, or an existing codebase to analyze. Optionally, an explicit pattern declaration.

Process:
1. The LLM reads the description (or codebase) and proposes a pattern, language, domains, and a manifest skeleton.
2. The LLM authors the project layer — fills the slots and inserts the global and pattern layers expose.
3. Forge validates the manifest against the schema.
4. Forge composes layered output for commands, invariants, and conventions.
5. Forge writes the composed output into the project tree (with user approval).

Output: a project containing `.forge/manifest.yaml` plus composed `commands/`, `invariants/`, and `conventions/` files at the paths the manifest declares.

### `forge update <project>`

Inputs: an existing project with a `.forge/manifest.yaml`.

Process:
1. The LLM re-evaluates the project layer against current state — the description may have evolved, new code may exist, the global or pattern layers may have changed.
2. Forge re-composes layered output.
3. Forge diffs against what's already on disk and presents the changes (with user approval).

Output: the project's commands, invariants, and conventions re-aligned with current baseline + current project state.

Create and update share the same composition mechanism. The only difference is whether the manifest exists going in.

## What's in this repo

| Path | Role |
|---|---|
| `forge/` | The resolver and CLI. Reads a manifest, composes layered artifacts, writes them to the project tree. |
| `commands/global/` | Layer-1 command templates. One file per command — the standardized persona, with `{{slots}}` and `<!-- insert: name -->` markers for project-specific content. |
| `commands/pattern/<pattern>/` | Layer-2 contributions per pattern. Slot fills and insert bodies that apply when a project declares this pattern. |
| `commands/project/` | LLM-facing prompts (`<command>.prompt.md`) that generate the project layer for each command. Read by the LLM at create-time. |
| `invariants/global.md` | Layer-1 universal invariants (GL-*). |
| `invariants/pattern/<pattern>.md` | Layer-2 invariants per pattern. |
| `invariants/domain/<domain>.md` | Cross-cutting invariants attached to a domain (e.g. CAD/CAM). |
| `conventions/global/<lang>.md` | Layer-1 universal coding conventions per language. |
| `conventions/pattern/<pattern>/<lang>.md` | Layer-2 conventions per pattern + language. |
| `conventions/domain/<domain>/<lang>.md` | Cross-cutting domain conventions. |
| `registry/projects.yaml` | The list of projects forge knows about. Single source of truth for project metadata (FG-1). |
| `docs/invariants/` | Forge's own invariants (FG-*) — the rules that govern how forge itself operates. |
| `tests/` | Resolver and CLI tests, including a synthetic compiler-pattern fixture under `tests/fixtures/sample_project/`. |
| `.claude/commands/` | Forge's own tooling — hand-authored commands for working on this codebase. Not part of the layered system. See "Forge's own tooling" below. |

A project's `.forge/manifest.yaml` declares:

- **Patterns** — primary (and optionally secondary, scoped to subtrees).
- **Domains** — cross-cutting concerns the project has.
- **Language** — for selecting which conventions files apply.
- **Resolution** — where the composed output should be written in the project tree.
- **Project layer** — slots and inserts the LLM authored against the description, keyed by command name.

## Forge's own invariants

| ID | Name | Rule |
|---|---|---|
| FG-1 | Registry-is-Truth | `registry/projects.yaml` is the single source of truth for what projects exist. |
| FG-2 | Baseline-Canonical | The baseline trees are canonical. Projects receive composed copies; they never modify the baseline directly. Project-specific content lives in the project's manifest. |
| FG-4 | Read-Before-Write | Create and update read the target thoroughly before any write; explicit human approval before applying. |

(Numbering preserved across deletions; gaps are honest signals that retired invariants existed.)

## Forge is not a consumer of itself

Forge produces hybrid runtime projects but does not consume its own pipeline. Commands, invariants, and conventions for forge are authored directly in this repo, not generated by forge from its own baseline. The canonical end-to-end test is the synthetic compiler-pattern fixture at `tests/fixtures/sample_project/`, plus external consumers as they're created.

## Forge's own tooling

Forge maintains its own `.claude/commands/` for working on this codebase — `/spec`, etc. These are hand-authored, not generated, and live outside the layered global/pattern/project system. New tooling commands can be added here as needed.

This carve-out is permanent by design: forge is the infrastructure that creates other projects; it shouldn't be exemplary of itself.

## Vocabulary

- **Project** — what `registry/projects.yaml` tracks.
- **Hybrid runtime project** — dev-env and run-env share an environment; humans, LLMs, and deterministic code are co-resident actors; most have a deterministic-runnable core that can be *published* as a conventional app/library/executable.
- **Pattern** — architectural shape (Compiler, KB, Declare-and-satisfy, Bracketed-probabilistic, ...). A project declares its primary pattern; layer-2 content keys off this.
- **Domain** — a cross-cutting concern that isn't pattern-shaped (CAD/CAM, ML, infrastructure). Projects declare domains independently of their pattern.
- **Create** — produce a manifest and project artifacts from a description or existing codebase.
- **Update** — re-apply the baseline to a previously created project, given its manifest.
- **Slot** — single-value placeholder in a layer-1 template (`{{NAME}}` or `{{NAME=default}}`); filled by layer 2 or layer 3.
- **Insert** — list/block placeholder in a layer-1 template (`<!-- insert: NAME -->`); contributions from layers 2 and 3 stack.
- **Publishing** — extracting a project's deterministic-runnable core into a conventional artifact. A defined feature, not an afterthought.
