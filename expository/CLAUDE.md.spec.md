---
artifact_class: expository
target: CLAUDE.md
---

# CLAUDE.md — Concept Checklist and Style Guide

This is the spec for `CLAUDE.md` files in projects created by forge. It is not a template with slots — it is a checklist of concepts every project's CLAUDE.md must cover, plus a style guide describing how those concepts should be expressed. The LLM authoring prompt reads this spec and produces the whole file.

For an exemplar of the target shape, read forge's own `CLAUDE.md` at the repo root.

This spec is not layered. Concepts that apply only when the project declares a particular pattern are called out inline as "if pattern is X, also cover Y" rather than living in a separate file. The authoring prompt reads `patterns.primary` from the manifest and follows the relevant conditional sections.

---

## What CLAUDE.md is

CLAUDE.md drives the agent. It tells the agent who it is in this project, where to look for what, how to run itself, and what to avoid. It does **not** restate what the project is or why it exists — that is README's job. When the agent needs project context, it reads README.

A CLAUDE.md should be short. Forge's own is ~34 lines. A long CLAUDE.md is usually project-specific operational content that should have moved into the structural system (commands, invariants, conventions) instead.

---

## Required concepts

Every CLAUDE.md must cover these:

### 1. Persona

Who the agent is in this project. Specific to the project's domain and shape — not "a senior software engineer" generic. Forge's persona is "experienced, fastidious senior information architect and prompt engineer." mill_ui's is engineering-shaped. applied-math-ml's would be study-partner-shaped.

The persona is a one-line declaration plus, when needed, a short paragraph naming what makes this project's persona distinct (e.g., "match register to artifact without losing voice across them," "default to prose over code in this notes-first context").

### 2. Look-up map

Pointers to where the agent should read for what. Not duplicated content — pointers. At minimum:

- README — for project context, structure, and "what this is"
- The invariants directory — for load-bearing rules
- The active commands — for task-specific personas
- Any other load-bearing project artifacts (a glossary, a checklist, a recipe index)

Format as inline references or a short table. Keep it scannable.

### 3. How to run / verify

Project-specific operational instructions: how to invoke the build/test/lint, which wrapper scripts to use, what command-line conventions matter. If the project has no executable surface (a notes-only KB, a documentation corpus), this section is replaced with how authoring/review/posting work.

For projects with code: name the wrappers explicitly so the agent doesn't reach for raw `pytest`/`ruff`/`mypy`. For projects without code: name the equivalent (where notes are reviewed, how the corpus is updated).

### 4. Don'ts

The traps. What the agent will be tempted to do that breaks this project specifically. These are deltas from generic agent defaults — don't list "don't write bad code"; do list things like "don't bypass the IR layer," "don't add proof-heavy material," "don't create new files when editing existing ones works."

The Don't list is project-specific by definition. Generic don'ts belong in the agent's defaults, not CLAUDE.md.

---

## Pattern-conditional concepts

Cover these only when the project's `patterns.primary` matches.

### When pattern is `kb`

KB projects are corpora — accumulating bodies of authored content where the load-bearing discipline is at *content-authoring time*, not at runtime. The agent in a KB project is operating on the corpus surface (reading, drafting, revising notes) rather than on a runtime pipeline. CLAUDE.md must additionally cover:

- **Citation discipline** — where the source index lives (`sources/README.md`, `references.bib`, etc.), the expected citation format (`[source-id:section]`, footnote-style, link-style), and the rule for new claims (cite the corpus first, external sources second; flag uncited claims as drafts). Implements `KB-2` at the agent's authoring surface.
- **Corpus discipline** — the rule for revisions (revise an entry only when the underlying claim was wrong; new perspectives are new entries), where new entries land (which track, which directory), whether the agent may rename entry filenames (default: no — filenames are stable identifiers). Implements `KB-3`.
- **Stage awareness** — a one-line statement of which of the four KB stages (storage, retrieval, assembly, synthesis) are *built* and which are *human-performed* (e.g., "storage and retrieval are file-structure based; assembly and synthesis are humans-only"). For human-performed stages, name the agent's role as authoring corpus content for human readers, not generating synthesized output. For built stages, point to the relevant code.

KB style adjustments:

- **Persona is study-partner or corpus-curator shaped, not engineer-shaped.** Even when the KB has built code, the persona reflects content discipline; engineering is downstream of the authoring discipline that makes the corpus trustworthy.
- **Don'ts emphasize content traps.** Don't generate uncited claims. Don't expand a topic into a notebook. Don't mutate older entries to "improve" them. Don't pull in domain examples from other projects.
- **The how-to-run section names corpus operations, not build operations.** How to add an entry, how to find the source index, how to check citations resolve. Build/test sections are absent unless the KB has a built pipeline.

(Other patterns — `compiler`, `declare-and-satisfy`, `bracketed-probabilistic` — currently have no CLAUDE.md-specific conditional concepts. Add them here when a pattern develops needs that the global concepts don't cover.)

---

## Optional concepts

Add these only when the project genuinely benefits:

### Modes

When the project has distinct working modes that change agent behavior (forge has Architect / Reviewer / Engineer modes; mill_ui doesn't have explicit modes). A mode is a *named behavioral overlay* — if you find yourself describing modes by listing different don'ts per mode, you probably want different commands instead.

### Agent constraints

Tool restrictions or harness-level rules ("don't use EnterPlanMode," "don't run other projects' build/test/deploy"). Only when the project has them; most projects don't.

### When stuck

A short pointer-table for common confusion points. Optional because not every project has predictable stuck-points worth pre-answering.

### Recognition-cue framing (KB only)

When the project is a study or recognition-aid corpus (applied-math-ml is the canonical example), CLAUDE.md should briefly state the recognition-over-mastery framing so the agent doesn't drift into tutorial-writing mode. Skip this for KBs that aren't study-shaped (a doc corpus producing whitepapers does not need this).

---

## Style

- **Terse.** Every section earns its place. Cut anything that restates README content. Cut anything that restates the agent's defaults.
- **Imperative voice for instructions** ("Read X before Y," "Don't Z"). Declarative for facts ("This is a one-person/one-AI project").
- **No conversation residue.** Don't include "Note: previously this said..." or "After the refactor..." That belongs in commit messages.
- **Refer outward, don't restate.** When CLAUDE.md needs to invoke project context, it links README. When it needs to invoke a rule, it links the invariant. When it needs to invoke an operation, it links the command.
- **No ornamental headers.** If a section has one bullet, it's not a section.

## Anti-patterns

- **Restating "what this project is" at the top.** That's README's job. CLAUDE.md may briefly name the project's shape ("a CAM compiler pipeline," "a study workspace") only to anchor the persona, not to describe the project.
- **Inlining capability tables, command lists, or operational reference material.** Those go in commands or in README. CLAUDE.md points at them.
- **Long Don't lists with generic items.** If a Don't would apply to any project, drop it.
- **Voice creep into public-facing prose.** CLAUDE.md is for the agent, not for a casual reader. It can be denser, more imperative, more assumed-knowledge than README.
