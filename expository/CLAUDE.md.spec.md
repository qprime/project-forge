---
artifact_class: expository
target: CLAUDE.md
---

# CLAUDE.md — Concept Checklist and Style Guide

This file lists the concepts every project's `CLAUDE.md` must cover, with a style guide describing how those concepts are expressed. The authoring prompt reads this spec and produces the file.

Concepts that apply only when the project declares a particular pattern are called out as conditional sections ("when pattern is X, also cover Y"). The authoring prompt reads `patterns.primary` from the manifest and follows the matching branches.

---

## What CLAUDE.md is

CLAUDE.md drives the agent. It tells the agent who it is in this project, where to look for what, how to operate, and what to avoid. It does not restate what the project is or why it exists — that is README's job. When the agent needs project context, it reads README.

CLAUDE.md is short. A long CLAUDE.md is usually project-specific operational content that should have moved into commands, invariants, or conventions.

---

## Required concepts

Every CLAUDE.md must cover these:

### 1. Persona

Who the agent is in this project. Specific to the project's domain and shape, not a generic engineering persona. One-line declaration; when needed, a short paragraph naming what makes this project's persona distinct.

### 2. Look-up map

Pointers to where the agent should read for what. Pointers, not duplicated content. At minimum:

- README — for project context and "what this is"
- The invariants directory — for load-bearing rules
- The active commands — for task-specific personas
- Any other load-bearing project artifacts

Format as inline references or a short table. Keep it scannable.

### 3. How to operate

Project-specific operational instructions: how to invoke build/test/lint, which wrapper scripts to use, what command-line conventions matter. If the project has no executable surface, this section names the equivalent: how authoring, review, and posting work.

### 4. Don'ts

Project-specific traps. Deltas from generic agent defaults. List things specific to *this* project's shape, not things that apply to any project.

---

## Pattern-conditional concepts

Cover these only when the project's `patterns.primary` matches.

### When pattern is `kb`

KB projects are corpora — accumulating bodies of authored content where the load-bearing discipline is at content-authoring time. The agent operates on the corpus surface (reading, drafting, revising entries) rather than on a runtime pipeline.

Required additional concepts:

- **Citation discipline** — where the source index lives, the expected citation format, and the rule for new claims (cite the corpus first, external sources second; flag uncited claims as drafts). Implements `KB-2` at the agent's authoring surface.
- **Corpus discipline** — the rule for revisions (revise an entry only when the underlying claim was wrong; new perspectives are new entries), where new entries land, whether the agent may rename entry filenames (default: no — filenames are stable identifiers). Implements `KB-3`.
- **Stage awareness** — a one-line statement of which of the four KB stages (storage, retrieval, assembly, synthesis) are built and which are human-performed. For human-performed stages, name the agent's role as authoring corpus content for human readers, not generating synthesized output. For built stages, point to the relevant code.

Style adjustments:

- Persona is curator-shaped or study-partner-shaped, not engineer-shaped, even when the KB has built code.
- Don'ts emphasize content traps (uncited claims, expanding entries past their scope, mutating older entries to "improve" them).
- The how-to-operate section names corpus operations, not build operations, unless the KB has a built pipeline.

---

## Optional concepts

Add these only when the project genuinely benefits.

### Modes

When the project has distinct working modes that change agent behavior. A mode is a named behavioral overlay. If modes differ only by listing different don'ts, the modes probably want to be different commands instead.

### Agent constraints

Tool restrictions or harness-level rules. Only when the project has them.

### When stuck

A short pointer-table for common confusion points. Optional because not every project has predictable stuck-points worth pre-answering.

### Recognition-cue framing (KB only)

When the project is a study or recognition-aid corpus, briefly state the recognition-over-mastery framing so the agent doesn't drift into tutorial-writing mode. Skip for KBs that aren't study-shaped.

---

## Style

- **Terse.** Every section earns its place. Cut anything that restates README content. Cut anything that restates the agent's defaults.
- **Imperative voice for instructions, declarative voice for facts.**
- **Refer outward, don't restate.** Link README for project context, the invariant for a rule, the command for an operation.
- **No conversation residue.** No "previously this said," no "after the refactor." That belongs in commit messages.
- **No ornamental headers.** A section with one bullet is not a section.

## Anti-patterns

- Restating "what this project is" at the top. That's README's job. A brief shape-anchor is allowed only as setup for the persona.
- Inlining capability tables, command lists, or operational reference material. Those go in commands or in README; CLAUDE.md points at them.
- Don't lists with generic items. If a Don't would apply to any project, drop it.
- Public-facing prose. CLAUDE.md is for the agent — denser, more imperative, more assumed-knowledge than README.
