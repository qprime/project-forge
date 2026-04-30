---
artifact_class: expository
target: README.md
---

# README.md — Concept Checklist and Style Guide

This file lists the concepts every project's `README.md` must cover, with a style guide describing how those concepts are expressed. The authoring prompt reads this spec and produces the file.

Concepts that apply only when the project declares a particular pattern are called out as conditional sections ("when pattern is X, also cover Y"). The authoring prompt reads `patterns.primary` from the manifest and follows the matching branches.

---

## What README.md is

README is the context for understanding the project — why it exists, what it does, how it is used. The audience is any reader: the agent on first contact with the project, a human browsing on GitHub, a future maintainer. README carries the substance of the project; CLAUDE.md refers back to it for context.

README's length scales with the project. A simple project gets a short README; a complex one earns a longer README. Length is not a virtue; concept coverage is.

These are AI-centric projects, intended to be explored and used with an AI copilot. The reader picking up the README is typically launching an AI agent inside the project tree, not invoking a binary by hand. That framing shapes what "how to use" means in the required concepts below.

---

## Required concepts

Every README must cover these:

### 1. What it is

A one-sentence opening that names the project as a noun, not as an activity. The opening is what GitHub previews show and what an agent reads first.

Followed by a short paragraph (one to three sentences) elaborating: what the project produces, what its primary input is, what shape of work it does.

### 2. Why it exists

What problem the project solves, or what alternative it replaces. A load-bearing reason, not marketing copy. Honest framing — "personal study notes" or "I wanted to learn X" beats generic framing when that's what's true.

### 3. What it does (substance)

The substantive description: pipeline, features, structural overview, examples. This section grows or shrinks with the project's complexity.

This is README's load-bearing section. CLAUDE.md will defer to it for project context, so the section must be structured well enough that pointing at it is sufficient.

### 4. Structure

Where things live in the project tree. A directory tree or a path-and-role table. Not exhaustive — the load-bearing subsystems, where canonical examples live, where entry points live.

This is also where structural commitments are documented (a registry path, a single-source-of-truth declaration, etc.).

### 5. How to use

How a reader engages the project. For these AI-centric projects, that typically means: which agent personas are available (the project's `commands/`), how to invoke them, and where to start a typical session. Include a literal example — open the project in an AI environment, invoke a command, read a representative file — that a new reader can follow without prior context.

For projects with executable surfaces beyond AI invocation (a CLI, an importable library), include the minimum needed to actually run them, tied to a real example in the repo.

---

## Pattern-conditional concepts

Cover these only when the project's `patterns.primary` matches.

### When pattern is `kb`

A KB project's README must tell a reader how the corpus is organized and how to read it. Without that section, the corpus reads as a pile of files rather than a navigable knowledge base.

Required additional concepts:

- **Corpus structure** — how the corpus is organized: tracks (when present), the role of cross-cutting directories, the source index, and any structural commitments that affect navigation. A directory tree alone is not enough; the reader needs to know why the directories are arranged the way they are. Cover the top-level layout, the question each top-level directory answers, and any cross-cutting artifacts that bind the corpus together.
- **Reading order** — where a new reader should start. A recommended starting point. For multi-track corpora, how the tracks relate (parallel, sequential, one foundational). For projects with a synthesis pipeline, how the synthesized output relates to the corpus (the corpus is the source of truth; synthesis is a query-time view).
- **Scope boundary** — what the corpus is *not*. KBs accrete; without an explicit scope statement they drift toward including everything. One or more "not" statements naming what's out of scope, with rationale per "not."

Style adjustments:

- Lead with the corpus's purpose, not its technology. Say what the corpus recognizes or covers before saying what tools or formats are involved.
- Show one entry as an example. A short excerpt of a typical corpus entry helps readers calibrate the kind of content here. For a KB, "how to use" is "how to read."
- Tables for taxonomies, prose for relationships.
- Don't duplicate CLAUDE.md content. Discipline rules (citation format, corpus accumulation, naming stability) belong in CLAUDE.md; README explains the corpus.

---

## Optional concepts

Add these when they earn their place.

### Vocabulary / glossary

When the project has load-bearing terms a newcomer will misread, a short defined-terms list at the bottom prevents downstream confusion. (A separate glossary artifact is planned; until that exists, vocabulary lives here.)

### Further reading

A pointer table to deeper docs. Use when the project has substantial documentation that doesn't belong in the README itself but is referenced often.

### Building / installation specifics

Use when there's a real reason to (a native extension, a non-trivial install). Skip otherwise.

### Project-specific principles

A load-bearing principle that fits in README rather than invariants. Use sparingly; if a principle is enforceable, it likely belongs in invariants.

### Source index (KB only)

When the corpus's claims trace to external sources, README links the source index and briefly describes its structure.

### Stage map (KB only)

When the KB has built stages, README documents which are built and what they produce. A purely notes-first KB doesn't need this section.

---

## Style

- **Public-facing voice.** README is read by people who don't have the project's context yet. Define jargon at first use; link to deeper material rather than dumping it.
- **Concrete first, abstract second.** Show before explain.
- **Prose for explanation, tables for enumeration.** See `conventions/global/markdown.md`.
- **Cite where to look, not what to think.** README points at examples and deeper docs. It doesn't try to teach the whole project — it teaches the reader how to navigate it.
- **No agent-direction content.** Anything that addresses the agent ("you, the agent, should...") belongs in CLAUDE.md.

## Anti-patterns

- Bullet lists as a substitute for structure. Sections need at least one paragraph saying what the section is doing.
- Marketing voice ("powerful, scalable, robust").
- Restating CLAUDE.md content. README does not list agent personas, agent don'ts, or how-to-run-the-agent.
- Status updates and changelogs. README is target-state, not historical.
- Trying to be a complete tutorial. README is an entry point; tutorials live in deeper docs.
