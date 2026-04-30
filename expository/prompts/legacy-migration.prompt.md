---
artifact_class: expository
target: project-description
kind: migration-prompt
status: transitional
---

# Legacy migration — distill prose description from existing project files

One-time prep step that runs **before** `forge create` against a project that already exists outside forge. Reads the project's existing files (`CLAUDE.md`, `README.md`, hand-authored invariants, top-level layout) and distills them into the prose description that `manifest-skeleton`, the per-command authoring prompts, and the expository authoring prompts all consume as their primary input.

This prompt is **transitional**. It exists to migrate the bounded set of pre-forge projects in `registry/projects.yaml` (entries marked `manifest: none`). Once those projects are migrated, this prompt should be retired. Do not extend it into a general-purpose ingestion tool.

---

## When to use

- A project exists at `<path>` with hand-authored `CLAUDE.md`, `README.md`, or both, but no `.forge/manifest.yaml`.
- The user wants to bring the project under forge management (`forge create` against an existing tree).
- The project's current files are the best source of truth for what the project is — there is no separate prose description.

If the user has supplied a fresh prose description and is creating from scratch (no existing files to reconcile), skip this prompt and run `manifest-skeleton` directly. If the project already has a `.forge/manifest.yaml`, use `forge update` instead — this prompt is for the pre-forge state.

---

## Inputs

Read all of these. The migration is only as good as the inputs it absorbs.

1. **`<path>/CLAUDE.md`** if present — the agent-instruction file.
2. **`<path>/README.md`** if present — the project context.
3. **Hand-authored invariants** at `<path>/docs/invariants/*.md` or wherever the project keeps them, if any.
4. **The top-level filesystem layout** at `<path>` — the directory tree, two levels deep. Used to ground the description in what's actually on disk.
5. **The registry entry** for this project in `registry/projects.yaml`, if one exists. The `description`, `tags`, and `domains` fields there were authored manually and may carry framing the file content does not.

If both `CLAUDE.md` and `README.md` are missing, stop and report. There is nothing to migrate from. The user should either author a description from scratch or restore one of the files first.

---

## Process

### Step 1 — Read and characterize

Read every input above. Build a mental model of:

- What the project *is* (a noun-phrase).
- What it *produces* or *contains* (the load-bearing output or content).
- Why it exists (the problem it solves or the alternative it replaces).
- Its structure on disk (top-level directories and their roles).
- Its load-bearing rules (the hand-authored invariants, the project-specific don'ts in CLAUDE.md).
- Its operational shape (build/test/run commands, or for corpus projects, the authoring/review surface).
- Its persona — how the existing CLAUDE.md frames the agent.
- Its mode of work (notes-first, code-first, hybrid, etc.).
- Its declared or implied pattern shape — read against the four known patterns (`compiler`, `kb`, `declare-and-satisfy`, `bracketed-probabilistic`). Do not finalize a pattern selection here; that is the manifest-skeleton prompt's job. But note the candidate so you can flag mismatches.

### Step 2 — Identify duplications and split-failures

Legacy CLAUDE.md and README.md typically duplicate substantial content. Note where they overlap. Specifically:

- "What this is" sections that appear in both — README owns this concept; CLAUDE.md should refer to it.
- Pipeline or structure diagrams in both — README owns substance.
- Capability tables, command lists, quick-start blocks duplicated — most of this belongs in commands or in README; CLAUDE.md should not inline it.
- Invariant or rule statements buried in CLAUDE.md prose — these belong in `invariants/`.

Capture the duplications as notes for the description; the downstream authoring prompts will use them to factor content correctly.

### Step 3 — Distill the description

Produce a single prose description, in markdown, that the downstream prompts will consume. The description is **not** a draft README or CLAUDE.md. It is a *source document* the prompts read.

Required sections in the description (use these exact H2 headings so downstream prompts can locate content predictably):

- **Identity** — one to three sentences naming what the project is, what it produces or contains, and the noun-phrase that anchors its name.
- **Why it exists** — the problem it solves or the alternative it replaces. Honest framing; preserve the original voice if the existing files have one.
- **Substance** — the substantive description: pipeline, features, structure, content tracks, examples. Pull from README. Note any sections that should live in README versus get factored elsewhere.
- **Operational shape** — build/test/run commands and wrapper scripts (for code projects), or corpus authoring/review surface (for notes projects). Pull from CLAUDE.md's how-to-run section.
- **Persona and modes** — how the agent should think and behave. Pull from CLAUDE.md.
- **Don'ts** — project-specific traps and constraints. Pull from CLAUDE.md.
- **Existing invariants** — the hand-authored invariants found in input 3, with their current text. Note for each: whether it looks like a globally-relevant rule (carried up to forge's global layer is unlikely; usually they belong as project-layer invariants) or a project-specific one.
- **Candidate pattern** — your best-guess pattern from the four known set, plus a one-paragraph rationale. Mark explicitly: "Final selection deferred to manifest-skeleton."
- **Filesystem ground truth** — the top-level directory layout (input 4), with one-line role notes per directory. The downstream README authoring prompt requires this to avoid inventing directories.
- **Migration notes** — anything the downstream prompts should know that doesn't fit a section above. Especially: duplications between CLAUDE.md and README.md (so they can factor cleanly), content in CLAUDE.md that should be pushed into commands or invariants rather than re-entering CLAUDE.md, ambiguities the description preserves rather than resolves.

### Step 4 — Self-check

Before returning, verify:

- The description does not invent content. Every claim traces to one of the inputs.
- The Identity section opens with the project as a noun, not as an activity.
- The Filesystem section reflects what is actually on disk.
- The Existing invariants section quotes the original text verbatim where possible.
- The Migration notes section flags content that should move out of CLAUDE.md (into commands or invariants) so the downstream CLAUDE.md authoring prompt does not just regenerate a fat CLAUDE.md.
- Nothing in the description prescribes the future shape of CLAUDE.md or README.md — those are the downstream authoring prompts' job. The description is *source material*, not a target.

If the existing files contradict each other (CLAUDE.md says one thing about the project, README.md says another), capture both in the relevant section and flag the contradiction in Migration notes.

---

## Output

A single markdown document — the distilled description — written to a working location agreed with the user (e.g., `<path>/.forge/migration-description.md` or stdout). Downstream prompts read this as their primary input.

The document is intermediate. After `manifest-skeleton`, the per-command authoring prompts, and the expository authoring prompts have run, the migration description has served its purpose and can be deleted. Do not commit it as a permanent project artifact unless the user wants to keep it as a record of the migration.

---

## What this prompt does *not* do

- It does not write `<project>/.forge/manifest.yaml`. That is `manifest-skeleton`'s job.
- It does not write the new `CLAUDE.md` or `README.md`. Those are the expository authoring prompts' jobs.
- It does not modify any file at `<path>` other than (optionally) writing the migration description to a working location.
- It does not select the pattern definitively. It proposes a candidate; manifest-skeleton makes the call.
- It does not run for greenfield projects. If there are no existing files, the user supplies a description directly.
