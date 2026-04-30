---
artifact_class: expository
target: project-description
kind: migration-prompt
status: transitional
---

# Legacy migration — distill prose description from existing project files

One-time prep step that runs before `forge create` against a project that already exists outside forge. Reads the project's existing files and distills them into the prose description that `manifest-skeleton`, the per-command authoring prompts, and the expository authoring prompts consume as their primary input.

This prompt is transitional. It exists to migrate the bounded set of pre-forge entries in `registry/projects.yaml` (those marked `manifest: none`). After they are migrated, the prompt retires.

---

## When to use

- A project exists at `<path>` with hand-authored `CLAUDE.md`, `README.md`, or both, but no `.forge/manifest.yaml`.
- The user wants to bring the project under forge management.
- The project's current files are the best source of truth for what the project is — no separate prose description has been supplied.

If the user supplied a fresh prose description and is creating from scratch, skip this prompt and run `manifest-skeleton` directly. If the project already has a `.forge/manifest.yaml`, use `forge update` instead.

---

## Inputs

Read all of these.

1. **`<path>/CLAUDE.md`** if present.
2. **`<path>/README.md`** if present.
3. **Hand-authored invariants** at `<path>/docs/invariants/*.md` or wherever the project keeps them, if any.
4. **The top-level filesystem layout** at `<path>` — the directory tree, two levels deep.
5. **The registry entry** for this project in `registry/projects.yaml`, if one exists. The `description`, `tags`, and `domains` fields there were authored manually and may carry framing the file content does not.

If both `CLAUDE.md` and `README.md` are missing, stop and report. There is nothing to migrate from.

---

## Process

### Step 1 — Read and characterize

Read every input. Build a mental model of:

- What the project is (a noun-phrase).
- What it produces or contains.
- Why it exists (the problem it solves or the alternative it replaces).
- Its structure on disk.
- Its load-bearing rules (hand-authored invariants and project-specific don'ts).
- Its operational shape (executable surface for code projects, authoring/review surface for corpus projects).
- The persona the existing CLAUDE.md frames.
- Its mode of work (notes-first, code-first, hybrid).
- Its declared or implied pattern, read against the four known patterns (`compiler`, `kb`, `declare-and-satisfy`, `bracketed-probabilistic`). Do not finalize the pattern selection — that belongs to `manifest-skeleton` — but note the candidate.

### Step 2 — Identify duplications and split failures

Existing CLAUDE.md and README.md typically duplicate substantial content. Note where they overlap. Specifically:

- "What this is" sections that appear in both — README owns this concept; CLAUDE.md should refer to it.
- Pipeline or structure diagrams in both — README owns substance.
- Capability tables, command lists, or quick-start blocks duplicated across both — most of this belongs in commands or in README; CLAUDE.md should not inline it.
- Invariant or rule statements buried in CLAUDE.md prose — these belong in the invariants directory.

Capture the duplications as notes; the downstream authoring prompts use them to factor content correctly.

### Step 3 — Distill the description

Produce a single prose description, in markdown, that the downstream prompts consume. The description is a source document for those prompts, not a draft of any output file.

Use these exact H2 headings so downstream prompts can locate content predictably:

- **Identity** — one to three sentences naming what the project is, what it produces or contains, and the noun-phrase that anchors its name.
- **Why it exists** — the problem it solves or the alternative it replaces. Preserve the original voice when the existing files have one.
- **Substance** — the substantive description: pipeline, features, structure, content tracks, examples. Pull from README.
- **Operational shape** — executable surface for code projects, or authoring/review surface for corpus projects. Pull from CLAUDE.md.
- **Persona and modes** — how the agent should think and behave. Pull from CLAUDE.md.
- **Don'ts** — project-specific traps and constraints. Pull from CLAUDE.md.
- **Existing invariants** — the hand-authored invariants from input 3, with their current text quoted verbatim where possible. Note whether each looks like a project-specific rule or one that might generalize.
- **Candidate pattern** — best-guess pattern from the four known set, plus a one-paragraph rationale. Mark explicitly: "Final selection deferred to manifest-skeleton."
- **Filesystem ground truth** — the top-level directory layout from input 4, with one-line role notes per directory. The downstream README authoring prompt depends on this to avoid inventing directories.
- **Migration notes** — anything the downstream prompts should know that doesn't fit a section above. Especially: duplications between CLAUDE.md and README.md, content in CLAUDE.md that should be pushed into commands or invariants, ambiguities the description preserves rather than resolves.

### Step 4 — Self-check

Before returning, verify:

- The description does not invent content. Every claim traces to one of the inputs.
- The Identity section opens with a noun, not an activity.
- The Filesystem section reflects what is actually on disk.
- The Existing invariants section quotes original text verbatim where possible.
- The Migration notes section flags content that should move out of CLAUDE.md, so the downstream CLAUDE.md authoring prompt does not regenerate a fat CLAUDE.md.
- Nothing in the description prescribes the future shape of CLAUDE.md or README.md — those are the downstream authoring prompts' job.

If the existing files contradict each other, capture both versions in the relevant section and flag the contradiction in Migration notes.

---

## Output

A single markdown document — the distilled description — written to a working location (typically `<path>/.forge/migration-description.md`). Downstream prompts read it as their primary input.

The document is intermediate. After the downstream prompts have run, it has served its purpose and can be deleted unless the user wants it kept as a record.

---

## Out of scope

This prompt does not:

- Write `<project>/.forge/manifest.yaml`. That belongs to `manifest-skeleton`.
- Write the new CLAUDE.md or README.md. Those belong to the expository authoring prompts.
- Modify any file at `<path>` other than the migration description at the working location.
- Select the pattern definitively. It proposes a candidate; `manifest-skeleton` makes the call.
- Run for greenfield projects. If no existing files are present, the user supplies a description directly.
