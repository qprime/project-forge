---
layer: project
command: engineer
kind: authoring-prompt
---

# engineer — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `engineer` skill. The output is a YAML fragment that fills named placeholders in `commands/global/engineer.md` via the project manifest's `customizations` block.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `commands/global/engineer.md` — read to see exact placeholders and surrounding prose.
- Any pattern contributions that apply — read them so you don't duplicate.

## Output

A YAML fragment to merge under `customizations.engineer:` in `<project>/.forge/manifest.yaml`. Include only keys with real content. Rule of thumb: if a cousin project on the same pattern would want the same text, it belongs in the pattern contribution.

---

## slot: PROJECT_DESCRIPTION

A short phrase naming what the project is. Match the description in the project registry if one exists.

- Good: `"an intent-driven PLC simulation framework"`
- Bad: `"a software project"`

## slot: ENGINEER_UNDERSTANDING

A clause describing what this engineer grasps about the project that a generic engineer wouldn't. Pull from load-bearing subsystems, core abstractions, or invariants the engineer must hold in mind while coding.

- Good: `"how structured-text generation composes with post-oracle verification, and why the refinement loop must remain bounded"`
- Bad: `"software engineering best practices"`

## insert: working-style-extras

Optional additional working-style rules specific to this project. Use sparingly — most working style is global. Add only rules that come from project-specific workflow constraints.

Omit if none apply.

## insert: do-bullets

Project-specific "do" bullets. Each must reference a project invariant, convention, or structural constraint — not a generic best practice.

- Good: `"Respect registry-is-truth — never duplicate project metadata outside registry/projects.yaml"`
- Bad: `"Write clean code"` (generic)

Omit if the global bullets cover the project.

## insert: dont-bullets

Project-specific "don't" bullets. Same bar — each must name a specific trap this project has.

- Good: `"Don't hand-edit composed output — re-run forge update instead"`
- Bad: `"Don't write bad code"`

Omit if the global bullets cover the project.

## insert: testing-extras

Project-specific testing guidance. Test framework conventions, fixture rules, coverage expectations that differ from the pattern defaults.

Omit if the project follows its pattern's testing conventions with no variation.

## insert: completion-protocol

How this project handles issue comments, PR protocol, or completion signaling. If the project uses GitHub issues, include the issue-comment template. If it uses a different tracker, adapt.

---

## Output shape

A YAML fragment for `customizations.engineer:` in `<project>/.forge/manifest.yaml`. Use plain scalars for one-line slot values and `|` block scalars for multi-line insert bodies (markdown content survives verbatim, including embedded H2 headers and fenced code blocks).

```yaml
engineer:
  slots:
    PROJECT_DESCRIPTION: <phrase>
    ENGINEER_UNDERSTANDING: <clause>
  inserts:
    working-style-extras: |
      <prose>
    do-bullets: |
      <bullets>
    dont-bullets: |
      <bullets>
    testing-extras: |
      <prose>
    completion-protocol: |
      <block>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `engineer:` from `customizations`.
