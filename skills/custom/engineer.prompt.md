---
layer: project
skill: engineer
kind: authoring-prompt
---

# engineer — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `engineer` skill. The output fills named placeholders in `skills/global/engineer.md`.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `skills/global/engineer.md` — read to see exact placeholders and surrounding prose.
- Any pattern contributions that apply — read them so you don't duplicate.

## Output

A markdown file. Include only sections with real content. Rule of thumb: if a cousin project on the same pattern would want the same text, it belongs in the pattern contribution.

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

- Good: `"Don't manually edit survey-derived profiles — re-run /survey instead"`
- Bad: `"Don't write bad code"`

Omit if the global bullets cover the project.

## insert: testing-extras

Project-specific testing guidance. Test framework conventions, fixture rules, coverage expectations that differ from the pattern defaults.

Omit if the project follows its pattern's testing conventions with no variation.

## insert: completion-protocol

How this project handles issue comments, PR protocol, or completion signaling. If the project uses GitHub issues, include the issue-comment template. If it uses a different tracker, adapt.

---

## Output shape

```markdown
---
layer: project
project: <project-name>
skill: engineer
---

# <project-name> — engineer contribution

## slot: PROJECT_DESCRIPTION

<phrase>

## slot: ENGINEER_UNDERSTANDING

<clause>

## insert: working-style-extras

<optional>

## insert: do-bullets

<optional bullets>

## insert: dont-bullets

<optional bullets>

## insert: testing-extras

<optional>

## insert: completion-protocol

<block, if applicable>
```

Sections with no content are omitted entirely.
