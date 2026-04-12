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
4. Proposes updates — preserving project-specific content and documented overrides
5. Presents diffs for approval before writing
6. Commits and optionally pushes

## What This Does NOT Do

- Does not auto-apply changes without confirmation
- Does not delete project-specific invariants or domain knowledge
- Does not remove documented overrides (presents them for review)
- Does not modify baseline files (FG-2)

## After Rebase

Updates `registry/projects.yaml` with the new `baseline_version` for the project.

See `/bootstrap` for the full rebase workflow details.
