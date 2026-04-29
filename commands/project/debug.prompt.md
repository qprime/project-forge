---
layer: project
command: debug
kind: authoring-prompt
---

# debug — project-layer authoring prompt

Run during create (or update) to produce project-specific content for the `debug` skill. The output is a YAML fragment that fills named placeholders in `commands/global/debug.md` via the project manifest's `project` block.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `commands/global/debug.md` — read for placeholder names and context.
- Pattern contributions that apply — read them so you don't duplicate.

## Output

A YAML fragment to merge under `project.debug:` in `<project>/.forge/manifest.yaml`. Include only keys with real content.

---

## insert: working-style-extras

Optional additional debugging-style rules specific to this project's common failure modes.

Omit if none apply.

## insert: do-bullets

Project-specific "do" bullets for debugging. Each should name a project-specific place to look or tactic that's uniquely useful here.

- Good: `"Check registry resolution — do all paths in registry/projects.yaml resolve?"`
- Bad: `"Read the stack trace"` (generic)

Omit if pattern contributions cover it.

## insert: dont-bullets

Project-specific anti-patterns when debugging this codebase. Traps that bite newcomers.

Omit if none apply.

## insert: domain-debugging

A dedicated section for project-specific debugging heuristics. Use a heading like `## <Project-Name>-Specific Debugging` followed by a bulleted list of common-failure-mode entry points.

Example shape:

```
## <Project>-Specific Debugging

When debugging <project> issues, check:
- **Subsystem X** — common failure mode Y, entry point Z
- **Subsystem A** — known trap B, verification step C
```

Omit if the project is small enough that the global section suffices.

## insert: invariant-files-extras

Additional invariant files or boundary-contract documents the debugger should consult. List files with a one-line purpose each.

Omit if `docs/invariants/` covers everything.

---

## Output shape

A YAML fragment for `project.debug:` in `<project>/.forge/manifest.yaml`. Use `|` block scalars for multi-line insert bodies.

```yaml
debug:
  inserts:
    working-style-extras: |
      <prose>
    do-bullets: |
      <bullets>
    dont-bullets: |
      <bullets>
    domain-debugging: |
      <section, may include H2 and fenced code>
    invariant-files-extras: |
      <lines>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `debug:` from `project`.
