---
artifact_class: expository
target: CLAUDE.md
layer: pattern
pattern: kb
---

# CLAUDE.md — KB Pattern Deltas

Additions to the global CLAUDE.md spec (`expository/global/CLAUDE.md.spec.md`) for projects declaring the KB pattern. Read the global spec first; only the deltas are listed here.

KB projects are corpora — accumulating bodies of authored content where the load-bearing discipline is at *content-authoring time*, not at runtime. The agent in a KB project is operating on the corpus surface (reading, drafting, revising notes) rather than on a runtime pipeline. The deltas below adjust CLAUDE.md so the agent has the right model of its job.

---

## Additional required concepts

### Citation discipline

Every KB project must tell the agent where citations live, what format they take, and what to do when adding new content. This implements `KB-2` (synthesis is bound to retrieved evidence) at the agent's authoring surface. Without this section the agent will produce ungrounded prose that *looks like* corpus content.

Required content:

- Where the source index lives (e.g., `sources/README.md`, `references.bib`)
- The expected citation format (e.g., `[source-id:section]`, footnote-style, link-style)
- The rule for new claims: cite the corpus first, external sources second; flag uncited claims as drafts

### Corpus discipline

Every KB project must tell the agent how the corpus accumulates. This implements `KB-3` (storage is accumulating, not mutating) at the agent's authoring surface.

Required content:

- The rule for revisions: revise an entry only when the underlying claim was wrong; new perspectives are new entries
- Where new entries land (which track, which directory)
- Whether the agent may rename entry filenames (default: no — filenames are stable identifiers)

### Stage awareness

Every KB project must tell the agent which of the four KB stages (storage, retrieval, assembly, synthesis) are *built* and which are *human-performed*. The agent's job changes depending on the answer.

Required content:

- A one-line statement of the stage map (e.g., "storage and retrieval are file-structure based; assembly and synthesis are humans-only")
- For human-performed stages: the agent's role is authoring corpus content for human readers, not generating synthesized output
- For built stages: pointers to the relevant code (`pipeline/retrieval.py`, etc.)

---

## Additional optional concepts

### Recognition-cue framing

When the project is a study or recognition-aid corpus (applied-math-ml is the canonical example, recipes-project is another), CLAUDE.md should briefly state the recognition-over-mastery framing so the agent doesn't drift into tutorial-writing mode. Skip this for KBs that aren't study-shaped (a doc corpus producing whitepapers does not need this).

---

## Style deltas

- **Persona is study-partner or corpus-curator shaped, not engineer-shaped.** Even when the KB has built code (a synthesis pipeline), the agent's CLAUDE.md persona reflects content discipline — the engineering is downstream of the authoring discipline that makes the corpus trustworthy.
- **Don'ts emphasize content traps.** Don't generate uncited claims. Don't expand a topic into a notebook. Don't mutate older entries to "improve" them. Don't pull in domain examples from other projects.
- **The how-to-run section names corpus operations, not build operations.** How to add an entry, how to find the source index, how to check citations resolve. Build/test sections are absent unless the KB has a built pipeline.
