---
artifact_class: expository
target: README.md
layer: global
---

# README.md — Concept Checklist and Style Guide

This is the global spec for `README.md` files in projects created by forge. It is not a template with slots — it is a checklist of concepts every project's README must cover, plus a style guide describing how those concepts should be expressed. The LLM authoring prompt reads this spec and produces the whole file.

For an exemplar of the target shape, read forge's own `README.md` at the repo root.

---

## What README.md is

README.md is the context for *understanding* the project — why it exists, what it does, how it is used. The audience is any reader: the agent on first contact with the project, a human browsing on GitHub, a future maintainer. README carries the substance of the project; CLAUDE.md refers back to it for context.

A README can be long when the project is complex. Mill_ui's is ~250 lines and earns it. Forge's is ~130 and earns it. Length is not a virtue; coverage of the required concepts is. If the project has no compelling structure to describe, the README is short and that's fine.

---

## Required concepts

Every README must cover these:

### 1. What it is

A one-sentence opening that names the project as a noun, not as an activity. "CAM system that turns declarative panel layouts into G-code" — not "this project does X." The opening sentence is what GitHub previews show; it is what an LLM grepping repos sees first.

Followed by a short paragraph (one to three sentences) elaborating: what it produces, what its primary input is, what shape of work it does.

### 2. Why it exists

What problem the project solves, or what alternative it replaces. Not marketing copy — a load-bearing reason. Mill_ui's "most CAM workflows require manual toolpath setup in GUI software" is a why. Forge's "every project authors all three from scratch; they drift" is a why.

If the project's why is "I wanted to learn X" or "personal study notes," say that — honest framing beats generic framing.

### 3. What it does (substance)

The substantive description: pipeline diagram, feature list, structural overview, examples. This is the section that grows or shrinks with the project's complexity. Forge has a three-layer model section + symmetry + two operations. Mill_ui has pipeline + features + assembly + nesting + domains/generators. Applied-math-ml would have the four-tracks structure.

This is README's *load-bearing* section. CLAUDE.md will defer to it for project context; the section must be structured well enough that pointing at it is sufficient.

### 4. Structure

Where things live in the project tree. A directory tree or a path-and-role table. Not exhaustive — the load-bearing subsystems, where to find canonical examples, where to find the entry points.

This section is where structural commitments are documented. If a project has a "registry is single source of truth" rule, the registry's location appears here.

### 5. How to use / Quick start

The minimum a reader needs to actually run or interact with the project. For executable projects: install + run a representative command. For corpus projects: where to start reading, how to add an entry. For libraries: an import + minimal example.

Quick start is for the literal reader — keep it copy-pasteable and tied to a real example in the repo (a recipe, a fixture, a sample entry).

---

## Optional concepts

Add these when they earn their place:

### Vocabulary / glossary

When the project has load-bearing terms that newcomers will misread (forge has "pattern," "domain," "slot," "insert"; mill_ui has "PML," "RemovalIntent," "interface"). A short defined-terms list at the bottom prevents downstream confusion.

### Further reading

A pointer table to deeper docs (syntax specs, design docs, recipes, dev docs). Use when the project has substantial documentation that doesn't belong in the README itself but is referenced often.

### Building / installation specifics

Native backend builds, optional dependencies, platform notes. Use when there's a real reason to (a C++ extension, a non-trivial install). Skip otherwise.

### Project-specific principles

Sometimes a project has a load-bearing principle that fits more naturally in README than in invariants ("forge is not a consumer of itself"). Use sparingly; if a principle is enforceable, it likely belongs in invariants.

---

## Style

- **Public-facing voice.** README is read by people who don't have the project's context yet. Define jargon when first used; link to deeper material rather than dumping it.
- **Concrete first, abstract second.** Show the example before explaining the theory. Forge's README opens with the three-layer model after stating what forge does; mill_ui shows the PML example before explaining the pipeline.
- **Prose for explanation; tables for enumeration.** Same rule as `conventions/global/markdown.md`. Don't use prose where a table is clearer; don't use a table where the items aren't peers.
- **Cite where to look, not what to think.** README points at recipes, examples, deeper docs. It doesn't try to teach the reader the whole project — it teaches them how to navigate it.
- **No agent-direction content.** Voice and tone target a human reader. Anything that says "you, the agent, should..." belongs in CLAUDE.md.

## Anti-patterns

- **Bullet lists as a substitute for structure.** A README that is mostly bullets and headers, with no paragraphs, usually has not yet been thought through. Sections need at least one paragraph saying what the section is doing.
- **Marketing voice.** "Powerful, scalable, robust X" — drop. State what the project does and let the reader decide.
- **Restating CLAUDE.md content.** README does not list agent personas, agent don'ts, or how-to-run-the-agent. README is project context; CLAUDE.md is agent direction.
- **Status updates and changelogs.** "Recently added: feature Y" rots fast. README is target-state, not historical.
- **Trying to be a complete tutorial.** A README is an entry point. Tutorials live in `docs/`, in recipes, or in linked external materials.
