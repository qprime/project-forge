---
description: Check projects against their baseline version and report divergence. Use to find which projects are stale or have drifted from the capability baseline.
---

# /drift — Baseline Divergence Detection

Check baseline drift for: $ARGUMENTS

## Usage

```
/drift <project>     # check one project
/drift all           # check all projects in registry
/drift --summary     # quick overview of all projects' baseline versions
```

Examples:
```
/drift mill_ui
/drift all
/drift --summary
```

## Process

### Step 1: Load Baseline State

Read the current capability baseline from `baseline/capability_baseline.md`:
- Current baseline date
- All capabilities (always-on + conditional)
- Tag definitions
- Skill templates

### Step 2: Resolve Target(s)

From `registry/projects.yaml`, get:
- Project's `baseline_version`
- Project's `tags`
- Project's `path` (if local)

### Step 3: Compare

For each project:

1. **Version check:** Is `baseline_version` current? How old is it?

2. **Skill comparison:** Read project's `.claude/commands/*.md` and compare against baseline templates:
   - Missing skills (in baseline but not in project)
   - Extra skills (project-specific, expected)
   - Stale skills (template has been updated since project's baseline_version)

3. **Capability check:** Read project's `CLAUDE.md` and compare capabilities table:
   - Missing capabilities for the project's tags
   - Capabilities that reference removed/renamed baseline entries

4. **Tag validation:** Do the project's tags still match its codebase? (Quick heuristic check)

### Step 4: Report

```
## Drift Report: <project>

### Baseline Version
- Registry: <version>
- Current baseline: <date>
- Status: CURRENT / STALE (<N> days behind)

### Skill Drift
| Skill | Status | Detail |
|-------|--------|--------|
| /engineer | Current / Stale / Missing | Description of difference |

### Capability Drift
| Capability | Status | Detail |
|------------|--------|--------|
| Name | Current / Stale / Missing | Description |

### Tag Validity
- [x] [python] — confirmed (Python code found)
- [ ] [async] — not detected (no asyncio usage)

### Recommended Action
- `/rebase <project>` to sync with current baseline
- Or: specific items that need attention
```

### Summary Mode (`--summary`)

```
## Baseline Drift Summary

| Project | Version | Status | Days Behind | Skills | Capabilities |
|---------|---------|--------|-------------|--------|-------------|
| mill_ui | 2026-04-05 | CURRENT | 0 | 7/7 | 8/8 |
| homenet | 2026-03-15 | STALE | 21 | 5/7 | 6/8 |
```

## Rules

1. **Read-only** — never modify projects (FG-4)
2. **Registry is truth** — use `registry/projects.yaml` for project metadata (FG-1)
3. **Report broken references** — if a project path doesn't resolve, flag it (FG-6)
4. **Suggest, don't auto-fix** — recommend `/rebase` but don't run it
