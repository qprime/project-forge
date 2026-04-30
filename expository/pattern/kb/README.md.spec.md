---
artifact_class: expository
target: README.md
layer: pattern
pattern: kb
---

# README.md — KB Pattern Deltas

Additions to the global README.md spec (`expository/global/README.md.spec.md`) for projects declaring the KB pattern. Read the global spec first; only the deltas are listed here.

A KB project's README has a job the global spec doesn't fully cover: it must tell a reader (human or agent) *how the corpus is organized* and *how to read it*. A KB without that section reads like a pile of files rather than a navigable knowledge base — readers can't find what they need and can't tell what's in scope.

---

## Additional required concepts

### Corpus structure

Every KB project's README must describe how the corpus is organized: tracks (when present), the role of `shared/` or cross-cutting directories, the source index, and any structural commitments that affect navigation.

A directory tree alone is not enough. The reader needs to know *why* the directories are arranged the way they are — what question each directory answers. "tracks/applied-math/ — applied-math problem families taxonomy" carries more than "tracks/applied-math/ — directory."

Required content:

- The top-level corpus layout (tracks, shared resources, source index)
- The question each top-level directory answers
- Any cross-cutting artifacts that bind the corpus together (a diagnostic checklist, a glossary, a master index)

### Reading order

Every KB project's README must say where a new reader should start. Without this, the corpus has no entry point and readers either start arbitrarily or bounce off.

Required content:

- A recommended starting point (a track's README, a primer note, a reading order document)
- For multi-track corpora: how the tracks relate (parallel? sequential? one is foundational?)
- For projects with a synthesis pipeline: how the synthesized output relates to the corpus (the corpus is the source of truth; synthesis is a query-time view)

### Scope boundary

Every KB project's README must say what the corpus is *not*. KBs accrete; without an explicit scope statement they drift into being everything-and-the-kitchen-sink. Applied-math-ml's "What This Is Not" section is the canonical shape.

Required content:

- One or more "not" statements naming what's out of scope (e.g., "not a tutorial corpus," "not domain-specific to manufacturing," "not exhaustive")
- The rationale for each — why is the boundary there?

---

## Additional optional concepts

### Source index

When the corpus's claims trace to external sources (a study KB, a research-derived doc corpus), README should link the source index and briefly describe its structure. The KB pattern's citation discipline (KB-2) requires citations resolve; the README is where readers learn where citations point to.

### Stage map

When the KB has built stages (synthesis, retrieval, assembly), README should document which are built and what they produce. A purely notes-first KB doesn't need this section.

---

## Style deltas

- **Lead with the corpus's purpose, not its technology.** A KB README should say what the corpus *recognizes* or *covers* before it says what tools or formats are involved. The reader needs to know if this is the right corpus for their question before they need to know how it's stored.
- **Show one entry as an example.** A short example of a typical corpus entry (an inline excerpt or a link to a representative entry) helps readers calibrate what kind of content lives here. This replaces the "Quick Start" section's role for executable projects — for a KB, "how to use" is "how to read."
- **Tables for taxonomies, prose for relationships.** When the KB has a structural taxonomy (problem families, source types, methods), use a table. When the KB has relationships between entries (track A feeds track B, source X expands on source Y), use prose.
- **Don't duplicate the agent's CLAUDE.md content.** README's audience is a human reader plus the agent on first contact. Discipline rules (citation format, corpus accumulation rules, naming stability) belong in CLAUDE.md, not README. README explains the corpus; CLAUDE.md tells the agent how to operate on it.
