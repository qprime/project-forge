---
layer: project
skill: review
kind: authoring-prompt
---

# review — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `review` skill. The output is a YAML fragment that fills named placeholders in `skills/global/review.md` via the project manifest's `customizations` block.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `skills/global/review.md` — read for placeholder names and context.
- Pattern contributions that apply — read them so you don't duplicate.
- The project's issue tracker and any conventions for posting review summaries.

## Output

A YAML fragment to merge under `customizations.review:` in `<project>/.forge/manifest.yaml`. Include only keys with real content.

---

## insert: startup-extras

Additional startup steps specific to this project. Typical case: a posting step tied to the project's issue tracker (e.g., "post summary to GitHub issue when the review is tied to an issue").

Example:

```
7. Post summary to the associated issue when the review is tied to one — post even when clean. The comment is durable project history.
```

Omit if the project has no issue tracker or the default six steps suffice.

## insert: code-review-extras

Additional bullets for code review specific to this project. Use sparingly — most code-review concerns are global or pattern-level.

Omit if pattern contributions cover it.

## insert: architectural-review-extras

Additional bullets for architectural review specific to this project. Project-specific concerns that aren't pattern-shaped.

Omit if pattern contributions cover it.

## insert: posting-slot-code

The posting slot in the code-review report template. Typical case: a GitHub Issue Comment slot.

Example:

```
## GitHub Issue Comment
[If tied to an issue, post the summary via `gh issue comment N --body ...` and paste the returned URL here. A review tied to an issue is **incomplete** until this slot contains a real URL.]
```

Omit if the project has no issue tracker.

## insert: posting-slot-spec

Same as posting-slot-code, but for the spec-review report template. Usually identical.

Omit if the project has no issue tracker.

## insert: posting-protocol

Project-specific posting protocol section. Typical case: a GitHub issue comment protocol.

Example:

```
## GitHub Issue Comment `[github-issues]`

When the review is tied to an issue, the report is incomplete until the GitHub Issue Comment section contains a real `gh issue comment` URL. Clean verdicts included — the comment is durable project history; terminal output is not.

1. Draft a summary capturing verdict, key findings, and any issue-update recommendations.
2. Post with `gh issue comment N --body "..."` (heredoc for multi-line).
3. Paste the returned URL into the report's GitHub Issue Comment slot and into your final response.
```

Omit if the project has no issue tracker.

---

## Output shape

A YAML fragment for `customizations.review:` in `<project>/.forge/manifest.yaml`. Use `|` block scalars for multi-line insert bodies (markdown content survives verbatim, including embedded H2 headers and fenced code blocks).

```yaml
review:
  inserts:
    startup-extras: |
      <prose or numbered line>
    code-review-extras: |
      <bullets>
    architectural-review-extras: |
      <bullets>
    posting-slot-code: |
      <block>
    posting-slot-spec: |
      <block>
    posting-protocol: |
      <section>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `review:` from `customizations`.
