---
artifact_class: expository
target: README.md
kind: authoring-prompt
---

# README.md — authoring prompt

Run during `forge create` (and `forge update` when the description or the spec has changed) to author the project's `README.md` at the project root.

This is not a slot-fill prompt. The output is the **whole file**, written against the concept checklist and the project's prose description. There is no manifest project layer for README.md and no separate pattern-layer spec — pattern-conditional concepts live inline in the spec and are followed when the project's `patterns.primary` matches.

---

## Inputs

Read all of these before writing. Do not skip any input.

1. **The project's prose description** — for new projects, the user-supplied description; for legacy projects, the description distilled by the legacy-migration prompt.
2. **The manifest** at `<project>/.forge/manifest.yaml` — already populated by the manifest-skeleton prompt. You need `patterns.primary` to know which conditional concepts apply, `project_context` for the substantive description, `domains`, `language`, and `commands` to anchor sections accurately.
3. **The expository spec** at `expository/README.md.spec.md` — the concept checklist and style guide every README must follow, including pattern-conditional sections.
4. **The reference exemplar** — forge's own `README.md` at the repo root. Not a template to copy; an example of the shape, voice, and how concepts compose.
5. **The existing on-disk file** at `<project>/README.md`, if it exists — read it. During `forge update` this is the prior version you reconcile against; during `forge create` for a legacy project, the migration prompt has already turned it into the description in input 1.
6. **The project's filesystem layout** — read the top-level directory tree at the project root. The "Structure" section requires accurate path-and-role information; do not invent directories.

If any of inputs 1, 3, 4, or 6 is missing, stop and report the gap.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the README must cover. Required come from the spec's "Required concepts" (what it is, why, substance, structure, quick start) **plus** any "Pattern-conditional concepts" sections matching the manifest's `patterns.primary` (for KB: corpus structure, reading order, scope boundary). Optional concepts only when the project benefits.

### Step 2 — Substance budget

The "what it does" section is README's load-bearing center. Decide how much it carries:

- For complex projects (mill_ui's pipeline + features + assembly + nesting + domains/generators), the substance section is the bulk of the README.
- For simple or notes-first projects (applied-math-ml's four tracks + diagnostic checklist), the substance section is shorter but still the center.
- For libraries with one job, the substance is one diagram or one example.

Do not pad. A short substance section is fine when the project genuinely is small.

### Step 3 — Author the file

Write in one pass, in the project's voice. Public-facing — assume the reader does not have the project's context yet. Apply pattern-conditional style guidance from the spec (e.g., for KB: lead with corpus purpose over technology, show one entry as an example).

For each section:

- **Opening** — one sentence naming the project as a noun. Then one to three sentences elaborating what it produces, what its primary input is, and what shape of work it does. The opening is what GitHub previews show.
- **Why** — what problem it solves or what alternative it replaces. Honest framing; "I wanted to learn X" beats marketing voice.
- **What it does (substance)** — pipeline diagram, feature list, structural overview, examples. This is the section that scales with project complexity.
- **Structure** — directory tree or path-and-role table grounded in the actual filesystem (input 6). Name the load-bearing subsystems, where canonical examples live, where entry points live.
- **Quick start / How to use** — minimum a reader needs to actually run or read the project. Tied to a real example in the repo. For a corpus, replace with "how to read" — where to start, in what order.
- **Pattern-conditional concepts** — author each required conditional concept that applies (e.g., for KB: corpus structure with rationale per directory, reading order, scope boundary). Corpus structure typically merges with or replaces the generic Structure section; reading order replaces the Quick start section for a corpus; scope boundary is its own section.
- **Optional sections** — vocabulary, further reading, building specifics, principles, source index, stage map. Add only when they earn their place.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the spec, including all matching pattern-conditional concepts, appears somewhere in the file.
- The opening is a one-sentence noun-phrase, not "this project does X."
- The structure section reflects what is actually on disk, not an idealized layout.
- Quick start (or its corpus-equivalent) is copy-pasteable and references a real example in the repo.
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
