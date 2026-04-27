---
layer: project
skill: close-out
kind: authoring-prompt
---

# close-out — project-layer authoring prompt

Run during bootstrap (or rebase) to produce project-specific content for the `close-out` skill. The output fills named placeholders in `skills/global/close-out.md`.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s) and declared language/toolchain.
- `skills/global/close-out.md` — read for placeholder names.
- Pattern contributions that apply (verification-checks is typically pattern-filled).

## Output

A markdown file. Most projects only need the posting-protocol slot; the verification-checks insertion is usually filled by the pattern layer. Include project-layer content only when it genuinely varies from pattern defaults.

---

## insert: verification-checks

Usually filled at the pattern layer (Python projects get pytest+ruff+pyright, etc.). Add a project-layer contribution only if this project has extra verification steps — e.g., a domain-specific simulation check, a reproducibility check that re-runs a reference evaluation.

Omit unless the project has verification beyond what the pattern provides.

## insert: posting-protocol

How this project handles posting the implementation summary. Defaults:

- If the project uses GitHub issues, include: `If associated with a GitHub issue, post the Implementation Summary (Phase 2) as a comment using \`gh issue comment <number> --body "..."\`.`
- If it uses a different tracker, adapt.
- If no tracker, omit the section entirely.

---

## Output shape

```markdown
---
layer: project
project: <project-name>
skill: close-out
---

# <project-name> — close-out contribution

## insert: verification-checks

<optional>

## insert: posting-protocol

<optional>
```

Sections with no content are omitted entirely.
