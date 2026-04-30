---
artifact_class: expository
target: CLAUDE.md
kind: authoring-prompt
---

# CLAUDE.md — authoring prompt

Run during `forge create` (and `forge update` when the description or the spec has changed) to author the project's `CLAUDE.md` at the project root.

This is not a slot-fill prompt. The output is the **whole file**, written against the concept checklist and the project's prose description. There is no manifest project layer for CLAUDE.md and no separate pattern-layer spec — pattern-conditional concepts live inline in the spec and are followed when the project's `patterns.primary` matches.

---

## Inputs

Read all of these before writing. Do not skip any input.

1. **The project's prose description** — for new projects, the user-supplied description; for legacy projects, the description distilled by the legacy-migration prompt.
2. **The manifest** at `<project>/.forge/manifest.yaml` — already populated by the manifest-skeleton prompt. You need `patterns.primary` to know which conditional concepts in the spec apply, `commands` to know what's resolvable, `project_context` for description and vocabulary.
3. **The expository spec** at `expository/CLAUDE.md.spec.md` — the concept checklist and style guide every CLAUDE.md must follow, including pattern-conditional sections.
4. **The reference exemplar** — forge's own `CLAUDE.md` at the repo root. Not a template to copy; an example of the target shape, length, and voice.
5. **The existing on-disk file** at `<project>/CLAUDE.md`, if it exists — read it. During `forge update` this is the prior version that you reconcile against; during `forge create` for a legacy project, the migration prompt has already turned it into the description in input 1.

If any of inputs 1, 3, or 4 is missing, stop and report the gap. Do not write a CLAUDE.md without the spec and an exemplar to anchor against.

---

## Process

### Step 1 — Concept inventory

List the required and optional concepts the file must cover. Required concepts come from the spec's "Required concepts" section (persona, look-up map, how to run/verify, don'ts) **plus** any "Pattern-conditional concepts" sections matching the manifest's `patterns.primary` (for KB: citation discipline, corpus discipline, stage awareness). Optional concepts are added only when the project benefits — do not force optional sections.

### Step 2 — Concept-to-section mapping

For each required concept, decide what section it lives in. Some concepts may share a section (a project's persona and modes might be one "Persona" section); some may need their own (don'ts are usually their own section). Do not create a section per concept mechanically — section structure should follow the project's natural shape.

### Step 3 — Author the file

Write the whole file in one pass, in the project's voice. Length target: forge's own ~34 lines is a *short* end of the range; ~60 lines is acceptable for a more complex project; over 100 lines is a smell that operational content is leaking in instead of being pushed into commands/invariants.

For each section:

- **Persona** — name who the agent is in this project. One line plus, when needed, a short paragraph naming what makes this persona distinct. Apply pattern-conditional style guidance from the spec (e.g., for KB, persona is study-partner or curator-shaped, not engineer-shaped).
- **Look-up map** — point to README, the invariants directory, the active commands, and any load-bearing project artifacts. Inline references or a short table. Do not duplicate content; refer.
- **How to run / verify** — project-specific operational instructions. Wrapper scripts, validation invocations, corpus operations. If the project has no executable surface, replace with how authoring/review/posting work.
- **Don'ts** — project-specific traps, *not* generic agent defaults. Pull from the project's description, its existing CLAUDE.md if any, and any pattern-conditional don't-style guidance from the spec.
- **Pattern-conditional concepts** — author each required conditional concept that applies (e.g., for KB: citation discipline, corpus discipline, stage awareness). These can be their own sections or folded into existing ones (citation discipline often lives near don'ts; stage awareness near how-to-run).
- **Optional concepts** — only when the project genuinely benefits. Do not include modes, agent constraints, when-stuck, or recognition-cue framing unless the project has explicit material for them.

### Step 4 — Self-check against the spec

Before returning, verify:

- Every required concept from the spec, including all matching pattern-conditional concepts, appears somewhere in the file.
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
