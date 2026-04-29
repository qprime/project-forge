# Markdown Conventions — KB Pattern

Additions and overrides to `conventions/global/markdown.md` for projects declaring the KB pattern. Read the global file first; only the deltas are listed here.

KB projects live or die on the discipline of their corpus. The conventions below exist because corpus rot is silent — entries drift, citations stop resolving, retrieval surfaces inconsistent shapes — and silent rot is the dominant failure mode for KBs.

---

## Entry shape

### Each corpus entry is a single self-contained file

A reader (human or LLM) should be able to load one entry and understand it without reading neighbors. Cross-references are explicit links. "Continued in the next file" or "see also without explanation" are smells; if two entries are inseparable, they are one entry.

**Failure mode:** retrieval returns one entry; the reader is missing context that lives in a neighboring file; the synthesized output is wrong because the retrieved entry was incomplete.

### Entry filenames are stable identifiers

Filenames participate in retrieval. Renaming an entry is a corpus-wide change: every citation that pointed to the old name breaks. Treat filenames the way code treats public API names — change them rarely and migrate consumers when you do.

**Failure mode:** citations rot silently; older synthesized outputs reference paths that no longer exist; readers lose trust in the corpus's stability.

---

## Recognition-cue framing

### Lead with "what does this look like in the wild"

KB entries answer recognition questions, not textbook questions. Open with the shape of the real problem, not the formal definition. Definitions belong further down; recognition cues belong at the top, where retrieval surfaces them.

```markdown
# Right
## Least-squares fitting

Looks like: you have measurements that don't agree, and you want
the line (or curve, or model) that minimizes total disagreement.
Recognition cue: "I want the best fit, accepting some error."

# Wrong
## Least-squares fitting

Definition: a method for solving overdetermined systems by
minimizing the sum of squared residuals.
```

**Failure mode:** retrieval surfaces the entry but the reader can't tell whether it's the right entry without working through the formal definition; the entry becomes a tutorial rather than a recognition aid.

---

## Citations

### Citation format is stable across the corpus

Pick one citation format (`[source-id]`, `[source-id:section]`, footnote-style, link-style) and apply it consistently. The format is part of the corpus's machine-readable surface — KB-2 (synthesis cites evidence) requires that citations parse, and inconsistent format breaks parsing.

**Failure mode:** citation-checker oracles fail in confusing ways; some entries' citations resolve and others don't; the discipline of KB-2 erodes silently.

### Cite the corpus first, external sources second

When a claim has been digested into a corpus entry, cite the entry. Cite external sources directly only when the corpus has not yet absorbed them. This makes the corpus the load-bearing layer and external sources its inputs, not a parallel system of authority.

**Failure mode:** the corpus becomes a thin wrapper around external citations; readers have to chase external links to verify anything; the work of digesting sources into recognition-cue prose was never done.

---

## Track and section structure

### A track's `README.md` is the index, not its first chapter

When the pattern uses tracks (parallel topic areas), each track's `README.md` is a navigable index — what's in this track, in what order, why. Substantive content lives in numbered or named sibling files.

```markdown
# Right
tracks/applied-math/
  README.md             # index: 10-family taxonomy + recommended order
  01-modeling.md        # actual content
  02-fitting.md         # actual content

# Wrong
tracks/applied-math/
  README.md             # index AND chapter on modeling AND chapter on fitting
```

**Failure mode:** the README balloons; navigability decays; readers can't find the entry they want because everything is in one file.

### Numbered prefixes order; suffixes do not

When entry order matters (a learning track, a layered exposition), use numeric prefixes (`01-`, `02-`) so directory listings reflect intent. Don't rely on alphabetical order of slugs — it's fragile and renaming for ordering reasons creates churn.

**Failure mode:** entries appear in arbitrary order in listings; readers miss the intended progression; new entries break the order when alphabetized.
