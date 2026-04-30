---
artifact_class: expository
target: CLAUDE.md
kind: authoring-prompt
---

# CLAUDE.md — authoring prompt

Run during `forge create` (and `forge update` when the description, the global spec, or the pattern delta has changed) to author the project's `CLAUDE.md` at the project root.

This is not a slot-fill prompt. The output is the **whole file**, written against the global concept checklist, the pattern's deltas, and the project's prose description. There is no manifest project layer for CLAUDE.md.

---

## Inputs

Read all of these before writing. Do not skip any input.

1. **The project's prose description** — for new projects, the user-supplied description; for legacy projects, the description distilled by the legacy-migration prompt.
2. **The manifest** at `<project>/.forge/manifest.yaml` — already populated by the manifest-skeleton prompt. You need `patterns.primary` to know which pattern delta applies, `commands` to know what's resolvable, `project_context` for description and vocabulary.
3. **The global expository spec** at `expository/global/CLAUDE.md.spec.md` — the concept checklist and style guide every CLAUDE.md must follow.
4. **The pattern delta** (if any) at `expository/pattern/<patterns.primary>/CLAUDE.md.spec.md` — additional required/optional concepts and style deltas for this pattern.
5. **The reference exemplar** — forge's own `CLAUDE.md` at the repo root. Not a template to copy; an example of the target shape, length, and voice.
6. **The existing on-disk file** at `<project>/CLAUDE.md`, if it exists — read it. During `forge update` this is the prior version that you reconcile against; during `forge create` for a legacy project, the migration prompt has already turned it into the description in input 1.

If any of inputs 1, 3, or 5 is missing, stop and report the gap. Do not write a CLAUDE.md without the spec and an exemplar to anchor against.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the file must cover. Required concepts come from the global spec (persona, look-up map, how to run/verify, don'ts) plus pattern-delta required concepts (for KB: citation discipline, corpus discipline, stage awareness). Optional concepts are added only when the project benefits — do not force optional sections.

### Step 2 — Concept-to-section mapping

For each required concept, decide what section it lives in. Some concepts may share a section (a project's persona and modes might be one "Persona" section); some may need their own (don'ts are usually their own section). Do not create a section per concept mechanically — section structure should follow the project's natural shape.

### Step 3 — Author the file

Write the whole file in one pass, in the project's voice. Length target: forge's own ~34 lines is a *short* end of the range; ~60 lines is acceptable for a more complex project; over 100 lines is a smell that operational content is leaking in instead of being pushed into commands/invariants.

For each section:

- **Persona** — name who the agent is in this project. One line plus, when needed, a short paragraph naming what makes this persona distinct.
- **Look-up map** — point to README, the invariants directory, the active commands, and any load-bearing project artifacts. Inline references or a short table. Do not duplicate content; refer.
- **How to run / verify** — project-specific operational instructions. Wrapper scripts, validation invocations, corpus operations. If the project has no executable surface, replace with how authoring/review/posting work.
- **Don'ts** — project-specific traps, *not* generic agent defaults. Pull from the project's description, its existing CLAUDE.md if any, and the pattern delta's "Don'ts emphasize..." style guidance.
- **Optional concepts** — only when the project genuinely benefits. Do not include modes, agent constraints, or when-stuck unless the project has explicit material for them.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the global spec and pattern delta appears somewhere in the file.
- The file does not restate "what this project is" — that's README's job. A brief shape-anchor ("a CAM compiler pipeline," "a study workspace") is allowed only as setup for the persona.
- The file refers outward (to README, invariants, commands) rather than inlining their content.
- The voice is imperative for instructions, declarative for facts, and free of conversation residue.
- No ornamental sections (a section with one bullet is not a section).

If any required concept is missing or any anti-pattern is present, revise before returning.

---

## Output

The whole content of `<project>/CLAUDE.md`, ready to write at the project root. No YAML wrapper, no slot block — just the markdown file.

Begin the file with `# CLAUDE.md — <project name>`. Use H2 for sections. Follow the markdown conventions in `conventions/global/markdown.md` (one H1 per file, terse prose, citations and references where appropriate).

Do not include a frontmatter block on the output file unless the project specifically reads CLAUDE.md frontmatter (almost no project does).
