---
layer: project
project: project-forge
skill: engineer
---

# project-forge — engineer contribution

## slot: PROJECT_DESCRIPTION

project-forge — a cross-project intelligence system and bootstrap orchestrator that owns the capability baseline, project registry, drift detection, and change monitoring

## slot: ENGINEER_UNDERSTANDING

registry management, baseline maintenance, three-layer skill/invariant/convention composition, and how the resolver deterministically assembles per-project artifacts from layered templates

## insert: do-bullets

- Respect FG-1 (Registry-is-Truth) — never duplicate `registry/projects.yaml` data in other files
- Respect FG-4 (Read-Before-Write) — read other projects freely, write only during `/bootstrap`, `/rebase`, or `/codex-sync` with user approval
- Respect FG-7 (Monitor-Proposes) — `/monitor` produces proposals, never auto-applies; preserve that boundary in any monitoring code
- Read `docs/invariants/global.md` before modifying registry, baseline, or cross-project logic

## insert: dont-bullets

- Don't manually edit survey-derived profiles (FG-3) — re-run `/survey` instead
- Don't store full copies of project state — store profiles, pointers, and summaries; read live when detail is needed
- Don't auto-rebase projects — drift detection and proposals only, human decides
- Don't promote a convention to an invariant on vibes — apply the counterfactual sorting test from `CLAUDE.md`

## insert: completion-protocol

After completing implementation associated with a GitHub issue, post a summary comment using `gh issue comment <number> --body "..."` with this shape:

```
## Implementation Summary

<1-2 sentence description>

### Changes

| File | Change |
|------|--------|
| `path/to/file.py` | Description |

### Notes
- Key decisions (omit if none)
```
