---
description: Sync an existing project's configuration with the current capability baseline. Use when the baseline has been updated and a project needs to catch up.
---

# /rebase — Baseline Sync

Sync project configuration with the current capability baseline for: $ARGUMENTS

This is a convenience alias for `/bootstrap rebase <target>`. It runs the rebase workflow from the bootstrap skill.

**Invariant check:** This writes to other projects — FG-4 (Read-Before-Write) requires explicit user approval.

## Usage

```
/rebase <target>
```

Target: local path, git remote URL, or registry project name.

Examples:
```
/rebase ~/Code/mill_ui
/rebase mill_ui
/rebase git@github.com:qprime/homenet.git
```

## What This Does

1. Reads the project's current CLAUDE.md, skills, and invariants
2. Infers current tags from existing configuration
3. Compares current skills against the current capability baseline
4. **Prompt-quality drift analysis** — for each project-specific skill section preserved during rebase, scan for the same prompting anti-patterns the baseline has been cleaned of: vague verbs ("relevant", "appropriate", "if configured"), mitigation scaffolding ("make sure", "don't forget", "double-check", "remember to"), and conditional work that 4.7-class models interpret narrowly ("when uncertain", "if tests exist"). Report each hit with file:line and propose a concrete replacement. Present as a separate section in the rebase diff so the user can accept the baseline sync and the drift fixes independently.
5. Proposes updates — preserving project-specific content and documented overrides
6. Presents diffs for approval before writing
7. Commits and optionally pushes

## What This Does NOT Do

- Does not auto-apply changes without confirmation
- Does not delete project-specific invariants or domain knowledge
- Does not remove documented overrides (presents them for review)
- Does not modify baseline files (FG-2)

## After Rebase

Updates `registry/projects.yaml` with the new `baseline_version` for the project. If the project's `targets` include `codex`, remind the user to run `/codex-sync <project>` to regenerate Codex files.

See `/bootstrap` for the full rebase workflow details.
