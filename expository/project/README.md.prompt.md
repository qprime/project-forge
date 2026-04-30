---
artifact_class: expository
target: README.md
kind: authoring-prompt
---

# README.md — authoring prompt

Run during `forge create` (and `forge update` when the description, the global spec, or the pattern delta has changed) to author the project's `README.md` at the project root.

This is not a slot-fill prompt. The output is the **whole file**, written against the global concept checklist, the pattern's deltas, and the project's prose description. There is no manifest project layer for README.md.

---

## Inputs

Read all of these before writing. Do not skip any input.

1. **The project's prose description** — for new projects, the user-supplied description; for legacy projects, the description distilled by the legacy-migration prompt.
2. **The manifest** at `<project>/.forge/manifest.yaml` — already populated by the manifest-skeleton prompt. You need `patterns.primary` for the pattern delta, `project_context` for the substantive description, `domains`, `language`, and `commands` to anchor sections accurately.
3. **The global expository spec** at `expository/global/README.md.spec.md` — the concept checklist and style guide every README must follow.
4. **The pattern delta** (if any) at `expository/pattern/<patterns.primary>/README.md.spec.md` — additional required/optional concepts and style deltas.
5. **The reference exemplar** — forge's own `README.md` at the repo root. Not a template to copy; an example of the shape, voice, and how concepts compose.
6. **The existing on-disk file** at `<project>/README.md`, if it exists — read it. During `forge update` this is the prior version you reconcile against; during `forge create` for a legacy project, the migration prompt has already turned it into the description in input 1.
7. **The project's filesystem layout** — read the top-level directory tree at the project root. The "Structure" section requires accurate path-and-role information; do not invent directories.

If any of inputs 1, 3, 5, or 7 is missing, stop and report the gap.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the README must cover. Required: what it is, why, what it does (substance), structure, quick start. Pattern-delta required (for KB: corpus structure, reading order, scope boundary). Optional concepts only when the project benefits.

### Step 2 — Substance budget

The "what it does" section is README's load-bearing center. Decide how much it carries:

- For complex projects (mill_ui's pipeline + features + assembly + nesting + domains/generators), the substance section is the bulk of the README.
- For simple or notes-first projects (applied-math-ml's four tracks + diagnostic checklist), the substance section is shorter but still the center.
- For libraries with one job, the substance is one diagram or one example.

Do not pad. A short substance section is fine when the project genuinely is small.

### Step 3 — Author the file

Write in one pass, in the project's voice. Public-facing — assume the reader does not have the project's context yet.

For each section:

- **Opening** — one sentence naming the project as a noun. Then one to three sentences elaborating what it produces, what its primary input is, and what shape of work it does. The opening is what GitHub previews show.
- **Why** — what problem it solves or what alternative it replaces. Honest framing; "I wanted to learn X" beats marketing voice.
- **What it does (substance)** — pipeline diagram, feature list, structural overview, examples. This is the section that scales with project complexity.
- **Structure** — directory tree or path-and-role table grounded in the actual filesystem (input 7). Name the load-bearing subsystems, where canonical examples live, where entry points live.
- **Quick start / How to use** — minimum a reader needs to actually run or read the project. Tied to a real example in the repo. For a corpus, replace with "how to read" — where to start, in what order.
- **Optional sections** — vocabulary, further reading, building specifics, principles. Add only when they earn their place.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the global spec and pattern delta appears somewhere in the file.
- The opening is a one-sentence noun-phrase, not "this project does X."
- The structure section reflects what is actually on disk, not an idealized layout.
- Quick start is copy-pasteable and references a real example in the repo.
- No agent-direction content has crept in ("you, the agent, should..." belongs in CLAUDE.md).
- No marketing voice ("powerful, scalable, robust").
- No status updates or recently-added changelogs.
- Tables for enumerations, prose for relationships and explanation; not bullets-as-substitute-for-structure.

If any required concept is missing or any anti-pattern is present, revise before returning.

---

## Output

The whole content of `<project>/README.md`, ready to write at the project root. No YAML wrapper, no slot block — just the markdown file.

Begin the file with `# <project name>`. Use H2 for top-level sections, H3 for sub-sections. Follow the markdown conventions in `conventions/global/markdown.md` (one H1, terse prose, link with relative paths, backtick code-shaped tokens).

Do not include a frontmatter block.
