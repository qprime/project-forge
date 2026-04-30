---
artifact_class: expository
target: README.md
kind: authoring-prompt
---

# README.md — authoring prompt

Run during `forge create` and during `forge update` when the description or the spec has changed. Produces the project's `README.md` at the project root as a whole-file output.

---

## Inputs

Read all of these before writing.

1. **The project's prose description** — for new projects, the user-supplied description; for projects coming from the legacy migration prompt, the description it produced.
2. **The manifest** at `<project>/.forge/manifest.yaml`. Read `patterns.primary` to determine which conditional concepts apply, `project_context` for the substantive description, `domains`, `language`, and `commands` to anchor sections accurately.
3. **The expository spec** at `expository/README.md.spec.md` — the concept checklist and style guide, including pattern-conditional sections.
4. **The reference exemplar** — the `README.md` at the root of the project-forge repository. Used as a calibration of shape, voice, and how concepts compose. Not a template to copy.
5. **The existing on-disk file** at `<project>/README.md`, if it exists. During `forge update`, this is the prior version; during `forge create` against a legacy project, the migration prompt has already absorbed it into input 1.
6. **The project's filesystem layout** — the top-level directory tree at the project root, two levels deep. Required to ground the Structure section in what exists on disk rather than an idealized layout.

If any of inputs 1, 3, 4, or 6 is missing, stop and report the gap.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the README must cover. Required concepts come from the spec's "Required concepts" section, plus any "Pattern-conditional concepts" matching the manifest's `patterns.primary`. Add optional concepts only when they earn their place.

### Step 2 — Substance budget

The "what it does" section is README's load-bearing center. Decide how much it carries based on the project's complexity. A simple project gets a short substance section; a complex one gets a long one. Match length to content; do not pad.

### Step 3 — Author the file

Write in one pass, in the project's voice. Public-facing — assume the reader does not have the project's context. Apply pattern-conditional style guidance from the spec.

For each section:

- **Opening** — one sentence naming the project as a noun. Then a short paragraph (one to three sentences) elaborating what the project produces, what its primary input is, and what shape of work it does.
- **Why** — what problem the project solves or what alternative it replaces. Honest framing.
- **What it does (substance)** — pipeline, feature list, structural overview, examples. Scales with project complexity.
- **Structure** — directory tree or path-and-role table grounded in input 6. Name load-bearing subsystems, where canonical examples live, where entry points live.
- **How to use** — how a reader engages the project. For these AI-centric projects, that typically means which agent personas exist, how to invoke them, and where to start a typical session, with a literal example a new reader can follow. For projects with executable surfaces beyond AI invocation, include the minimum needed to run them, tied to a real example.
- **Pattern-conditional concepts** — author each required conditional concept that applies. Some replace generic sections (corpus structure may replace Structure for a KB; reading order may replace How to use).
- **Optional sections** — add only when they earn their place.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the spec, including all matching pattern-conditional concepts, appears in the file.
- The opening is a one-sentence noun-phrase, not "this project does X."
- The Structure section reflects what is actually on disk.
- The How-to-use section (or its corpus equivalent) is grounded in a real example in the repo.
- No agent-direction content has crept in. Anything addressing the agent belongs in CLAUDE.md.
- No marketing voice. No status updates or changelogs.
- Tables for enumerations, prose for relationships and explanation. No bullets-as-substitute-for-structure.

If any required concept is missing or any anti-pattern is present, revise before returning.

---

## Output

The full content of `<project>/README.md`, ready to write at the project root. Markdown only — no YAML wrapper, no slot block, no frontmatter.

Begin the file with `# <project name>`. Use H2 for top-level sections, H3 for sub-sections. Follow `conventions/global/markdown.md`.
