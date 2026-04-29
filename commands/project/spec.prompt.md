---
layer: project
command: spec
kind: authoring-prompt
---

# spec — project-layer authoring prompt

Run during create (or update) to produce project-specific content for the `spec` skill. The output is a YAML fragment that fills named placeholders in `commands/global/spec.md` via the project manifest's `project` block.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `commands/global/spec.md` — read for placeholder names and context.
- Pattern contributions that apply — read them so you don't duplicate.

## Output

A YAML fragment to merge under `project.spec:` in `<project>/.forge/manifest.yaml`. Include only keys with real content.

---

## slot: ISSUE_TRACKER

The target for the spec output. Typical values: `GitHub issue`, `Linear ticket`, `internal spec document`. Default: `GitHub issue`.

Paragraph-embedded slot — write a single-line phrase that fits in flow.

## slot: INVARIANT_READ_TARGETS

Names the invariant files step 1 of Process tells the spec author to read. Typical shape: `` `docs/invariants/global.md` plus any subsystem invariant file touched by the change ``. Default: `all invariant files that govern the affected code paths`.

Paragraph-embedded slot — write a single-line phrase. Use backticks for file paths.

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

A YAML fragment for `project.spec:` in `<project>/.forge/manifest.yaml`. Use plain scalars for one-line slot values and `|` block scalars for multi-line insert bodies.

```yaml
spec:
  slots:
    ISSUE_TRACKER: <value>
    INVARIANT_READ_TARGETS: <phrase>
  inserts:
    process-extras: |
      <prose>
    design-extras: |
      <prose>
    testing-strategy-extras: |
      <prose>
    quality-checks-extras: |
      <bullets>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `spec:` from `project`.
