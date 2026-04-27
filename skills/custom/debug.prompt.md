---
layer: project
skill: debug
kind: authoring-prompt
---

# debug — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `debug` skill. The output fills named placeholders in `skills/global/debug.md`.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s).
- `skills/global/debug.md` — read for placeholder names and context.
- Pattern contributions that apply — read them so you don't duplicate.

## Output

A markdown file. Include only sections with real content.

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

```markdown
---
layer: project
project: <project-name>
skill: debug
---

# <project-name> — debug contribution

## insert: working-style-extras

<optional>

## insert: do-bullets

<optional bullets>

## insert: dont-bullets

<optional bullets>

## insert: domain-debugging

<optional section>

## insert: invariant-files-extras

<optional lines>
```

Sections with no content are omitted entirely.
