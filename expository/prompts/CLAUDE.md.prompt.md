---
artifact_class: expository
target: CLAUDE.md
kind: authoring-prompt
---

# CLAUDE.md — authoring prompt

Run during `forge create` and during `forge update` when the description or the spec has changed. Produces the project's `CLAUDE.md` at the project root as a whole-file output.

---

## Inputs

Read all of these before writing.

1. **The project's prose description** — for new projects, the user-supplied description; for projects coming from the legacy migration prompt, the description it produced.
2. **The manifest** at `<project>/.forge/manifest.yaml`. Read `patterns.primary` to determine which conditional concepts in the spec apply, `commands` to know which agent personas resolve, and `project_context` for description and vocabulary.
3. **The expository spec** at `expository/CLAUDE.md.spec.md` — the concept checklist and style guide, including pattern-conditional sections.
4. **The reference exemplar** — the `CLAUDE.md` at the root of the project-forge repository. Used as a calibration of target shape, length, and voice. Not a template to copy.
5. **The existing on-disk file** at `<project>/CLAUDE.md`, if it exists. During `forge update`, this is the prior version; during `forge create` against a legacy project, the migration prompt has already absorbed it into input 1.

If any of inputs 1, 3, or 4 is missing, stop and report the gap.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the file must cover. Required concepts come from the spec's "Required concepts" section, plus any "Pattern-conditional concepts" matching the manifest's `patterns.primary`. Add optional concepts only when the project has explicit material for them.

### Step 2 — Concept-to-section mapping

Decide what section each concept lives in. Some concepts share a section; some need their own. Section structure follows the project's natural shape, not a one-section-per-concept template.

### Step 3 — Author the file

Write the whole file in one pass, in the project's voice. Match length to the project's complexity, but stay terse — operational reference content belongs in commands, invariants, or conventions rather than inlined here.

For each section:

- **Persona** — name who the agent is in this project. One line plus, when needed, a short paragraph naming what makes this persona distinct. Apply pattern-conditional style guidance from the spec.
- **Look-up map** — point to README, the invariants directory, the active commands, and any load-bearing project artifacts. Refer; do not duplicate.
- **How to operate** — project-specific operational instructions. For projects with executable surfaces, name wrapper scripts and conventions; for corpus projects, name the authoring, review, and posting surface.
- **Don'ts** — project-specific traps. Pull from the project description, the existing CLAUDE.md if any, and any pattern-conditional don't-style guidance.
- **Pattern-conditional concepts** — author each required conditional concept that applies. These can be their own sections or folded into adjacent sections (citation discipline often sits with don'ts; stage awareness with how-to-operate).
- **Optional concepts** — only when the project has explicit material.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the spec, including all matching pattern-conditional concepts, appears in the file.
- The file does not restate "what this project is" — that's README's job. A brief shape-anchor is allowed only as setup for the persona.
- The file refers outward (to README, invariants, commands) rather than inlining their content.
- The voice is imperative for instructions, declarative for facts. No conversation residue.
- Sections with one bullet are not sections.

If any required concept is missing or any anti-pattern is present, revise before returning.

---

## Output

The full content of `<project>/CLAUDE.md`, ready to write at the project root. Markdown only — no YAML wrapper, no slot block, no frontmatter unless the project specifically reads CLAUDE.md frontmatter.

Begin the file with `# CLAUDE.md — <project name>`. Use H2 for sections. Follow `conventions/global/markdown.md`.
