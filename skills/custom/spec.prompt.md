---
layer: project
skill: spec
kind: authoring-prompt
---

# spec — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `spec` skill. The output fills named placeholders in `skills/global/spec.md`.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `skills/global/spec.md` — read for placeholder names and context.
- Pattern contributions that apply — read them so you don't duplicate.

## Output

A markdown file. Include only sections with real content.

---

## slot: ISSUE_TRACKER

The target for the spec output. Typical values: `GitHub issue`, `Linear ticket`, `internal spec document`. Default: `GitHub issue`.

## insert: process-extras

Additional process steps specific to this project. For example, projects with a research-heavy front-end may require a literature check; projects with strict data-gate rules may require a gate-check step.

Omit if the five default steps cover the project.

## insert: design-extras

Additional required content in the Design section. For example: a pattern-specific diagram, a required callout of which component of the pattern is changing, a risk-classification field.

Omit if the defaults cover the project.

## insert: testing-strategy-extras

Additional required content in the Testing Strategy section. For example: a required reproducibility check, a named set of test fixtures the project always uses, or split-aware testing rules.

Omit if the defaults cover the project.

## insert: quality-checks-extras

Additional checklist items specific to this project. Add items that catch project-specific failure modes — not generic ones.

Omit if none apply.

---

## Output shape

```markdown
---
layer: project
project: <project-name>
skill: spec
---

# <project-name> — spec contribution

## slot: ISSUE_TRACKER

<value>

## insert: process-extras

<optional>

## insert: design-extras

<optional>

## insert: testing-strategy-extras

<optional>

## insert: quality-checks-extras

<optional bullets>
```

Sections with no content are omitted entirely.
