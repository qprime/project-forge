# Markdown Authoring Guidelines

Rules for AI agents writing markdown in projects created from this baseline.

Markdown here is a content-bearing artifact, not formatted prose. Notes, specs, READMEs, and CLAUDE files are read by humans *and* parsed by other agents — so the structure has to behave as a structure, not just look like one.

Each rule has: the rule (imperative), a right/wrong example, and the failure mode if violated. Cross-references to invariants in `invariants/global.md` (GL-N) are noted where applicable.

How to use: when about to make a decision listed below, look up the rule. If a rule blocks correct work, raise it; do not work around it locally.

---

## Headings

### One H1 per file, equal to the file's purpose

The H1 names what the file *is*; everything below it elaborates. Do not use H1 as a section divider — H2 is the section level.

```markdown
# Right
# KB Pattern Invariants

## KB-1 — Retrieval is deterministic
...

# Wrong (multiple H1s for sections)
# Invariants
# Conventions
# Notes
```

**Failure mode:** TOC generators and outline tools can't distinguish "this file's subject" from "a section within the file"; readers landing mid-document have no anchor.

### Heading depth tracks structure, not emphasis

Don't use H4/H5 to mean "this is more important." Use them when there is genuinely a fourth or fifth level of nesting. If a document needs more than three levels often, the document is two documents.

**Failure mode:** depth becomes decorative; outlines collapse into a wall of indented bullets that don't parse as hierarchy.

---

## Lists vs. prose

### Use prose for explanation, lists for enumeration

A list is a claim that the items are peers and the order is either irrelevant or sequential. If items have dependencies, qualifications, or different weights, write prose.

```markdown
# Right (list — peer items)
The pattern carries four invariants: KB-1, KB-2, KB-3, KB-4.

# Right (prose — items are not peers)
KB-2 is the load-bearing rule; the others support it. KB-1 makes
retrieval reproducible so that KB-2's citation check has stable
referents. KB-3 keeps the corpus auditable across time. KB-4 holds
only when stages are built.

# Wrong (list of items that aren't peers)
- KB-1 — retrieval determinism
- KB-2 — load-bearing; everything else exists to support this
- KB-3 — auditing
- KB-4 — only relevant if stages are built
```

**Failure mode:** the reader can't tell which items are central; structure implies equality where the content doesn't have it.

### Keep lists shallow

One level of nesting is fine. Two is a smell. Three almost always means the structure is wrong — convert to a section, a table, or prose.

**Failure mode:** deeply nested lists hide hierarchy that should be a heading; readers lose the parent context by the time they reach a leaf.

---

## Code, paths, and inline refs

### Backtick anything that should be parsed as a token, not read as a word

File paths, function names, command-line invocations, type names, schema fields — all in backticks. The rule is mechanical: if a typo in this token would break something, backtick it.

```markdown
# Right
The resolver reads `forge/manifest.schema.json` and writes to
`commands_dir`. Run `forge update <project>` to apply.

# Wrong
The resolver reads forge/manifest.schema.json and writes to
commands_dir. Run forge update <project> to apply.
```

**Failure mode:** prose-rendering pipelines (link extractors, search indexers) treat code-shaped strings as words; copy-paste from rendered output silently mangles the token.

### Link to files with relative paths from the document

When referencing a file in the same repo, link it relative to the current file. Do not link to fully-qualified URLs unless the reference is genuinely external.

```markdown
# Right
See [the global invariants](../global.md) and [GL-2](../global.md#gl-2).

# Wrong
See https://github.com/qprime/project-forge/blob/main/invariants/global.md
```

**Failure mode:** absolute URLs rot when the repo moves, the branch renames, or the file moves; relative paths follow the file.

---

## Frontmatter

### Use YAML frontmatter for machine-readable metadata; only when something reads it

Frontmatter is for fields a tool consumes (`layer:`, `pattern:`, `status:`, `id:`). Don't add frontmatter that no code or downstream agent reads — that's documentation pretending to be data.

```markdown
# Right (consumed by the resolver)
---
layer: pattern
pattern: kb
---

# Wrong (consumed by nothing)
---
title: KB Invariants
created: 2026-04-29
last_edited: 2026-04-29
mood: thoughtful
---
```

**Failure mode:** ornamental frontmatter accumulates, drifts out of date, and trains readers to ignore the block — which then misses the fields that *are* load-bearing.

### Frontmatter keys are stable identifiers, not labels

Use `kebab-case` for keys; never reword a key without migrating consumers. Frontmatter is a schema, even when it's small.

**Failure mode:** silent rename breaks every tool that read the old key; failures surface far from the rename.

---

## Tables

### Use tables when columns are labels and rows are records

If you find yourself writing a two-column table where the left column is a heading and the right column is a paragraph, you wanted prose with bold headings, not a table. Tables are for grids.

**Failure mode:** prose-disguised-as-table renders correctly but breaks every tool that treats tables as structured data.

### Keep cells short; link out for detail

A table cell longer than a sentence is a sign the table is the wrong shape. Use a short cell with a link to a fuller treatment elsewhere.

**Failure mode:** wide tables with multi-paragraph cells are unreadable in narrow renderings (terminals, mobile, narrow IDE panes).

---

## Citations and provenance

### Cite sources for any claim that isn't self-evident from the surrounding text

Implements GL-2 (non-deterministic output carries provenance). When the markdown is itself the LLM-or-human authored artifact whose claims need to be auditable, every claim of fact traces to where it came from — a file, an entry, an external source listed in `sources/`.

```markdown
# Right
The KB pattern's stage decomposition follows the four-stage model
described in `project_patterns_draft.md:280`.

# Wrong
The KB pattern has four stages.
```

**Failure mode:** assertions accumulate without traceability; readers can't tell what is established vs. inferred vs. invented; the corpus drifts from being a knowledge base to being plausible-sounding text.

### When uncertain, say so explicitly

"I think," "probably," "uncertain whether" — these are content, not weakness. Confident prose about uncertain things is a worse failure than hedged prose about uncertain things.

**Failure mode:** false certainty propagates; downstream readers (humans and LLMs) treat unverified claims as established.

---

## Voice

### Write target-state, not conversation

The artifact should read as if it has always been this way. Don't include "I changed this from X" or "previously this said Y" — that belongs in commit messages.

**Failure mode:** files turn into changelogs; readers can't tell what is *currently true* without reading the history of edits.

### Be terse; cut anything that doesn't earn its place

A sentence that restates the previous sentence is dead weight. A bullet that says what the heading already says is dead weight. Markdown gets longer over time by accretion; counter that by trimming on every edit.

**Failure mode:** documents become unread because they are too long to read; the load-bearing parts get buried under restated obvious parts.
