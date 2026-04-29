---
layer: project
command: close-out
kind: authoring-prompt
---

# close-out — project-layer authoring prompt

Run during create (or update) to produce project-specific content for the `close-out` skill. The output is a YAML fragment that fills named placeholders in `commands/global/close-out.md` via the project manifest's `project` block.

---

## Inputs

- The target project's spec / guidance document.
- The project's declared pattern(s) and declared language/toolchain.
- `commands/global/close-out.md` — read for placeholder names.
- Pattern contributions that apply (verification-checks is typically pattern-filled).

## Output

A YAML fragment to merge under `project.close-out:` in `<project>/.forge/manifest.yaml`. Most projects only need the `posting-protocol` insert; the `verification-checks` insert is usually filled by the pattern layer. Include project-layer content only when it genuinely varies from pattern defaults.

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

A YAML fragment for `project.close-out:` in `<project>/.forge/manifest.yaml`. Use `|` block scalars for multi-line insert bodies.

```yaml
close-out:
  inserts:
    verification-checks: |
      <bullets or steps>
    posting-protocol: |
      <prose>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `close-out:` from `project`.
