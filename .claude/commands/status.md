---
description: Dashboard showing all projects, baseline versions, drift status, and recent activity. Use for a quick overview of the project ecosystem.
---

# /status — Project Dashboard

Show project ecosystem status for: $ARGUMENTS

## Usage

```
/status              # full dashboard
/status <project>    # single project detail
/status --health     # health checks only (FG-6 validation)
```

## Process

### Full Dashboard (no args)

1. **Load registry** from `registry/projects.yaml`
2. **Check each project:**
   - Path resolution (does the path exist?) — FG-6
   - Baseline version vs current baseline date
   - Profile freshness (if `profiles/<name>.yaml` exists)
3. **Load profiles** for projects that have them
4. **Present dashboard**

### Output: Full Dashboard

```
## Project Ecosystem Status

**Registry:** <N> projects | **Baseline:** <date> | **Profiles:** <N>/<total>

### Projects

| Project | Path | Baseline | Profile | Status |
|---------|------|----------|---------|--------|
| mill_ui | ~/Code/mill_ui | 2026-04-05 | Fresh | OK |
| homenet | ~/Code/homenet | — | None | NO BASELINE |
| turnstile | (no path) | — | None | REMOTE ONLY |

### Health (FG-6)
- OK: <N> projects with valid paths
- WARN: <N> projects with no local path (remote only)
- ERROR: <N> projects with broken paths

### Baseline Coverage
- Current (<date>): <N> projects
- Stale: <N> projects
- Never bootstrapped: <N> projects

### Recent Activity (from profiles)
- mill_ui: <recent focus from profile>
- ...
```

### Single Project Detail

```
## Status: <project>

**Registry entry:**
- repo: <repo>
- path: <path> (exists: yes/no)
- tags: [list]
- baseline_version: <version>
- description: <description>
- domains: [list]

**Profile:** <exists/missing/stale>
- Last surveyed: <date>
- Architecture: <style>
- Recent focus: <from profile>

**Baseline drift:** CURRENT / STALE / UNKNOWN
- Skills: <N>/<expected>
- Capabilities: <N>/<expected>

**Recommended actions:**
- /survey <project> — update profile
- /drift <project> — check baseline divergence
- /rebase <project> — sync with baseline
```

### Health Check Mode (`--health`)

Validates FG-6 (No-Stale-Pointers):

```
## Health Check

| Project | Path | Repo | Status |
|---------|------|------|--------|
| mill_ui | ~/Code/mill_ui | qprime/mill_ui | OK |
| turnstile | (none) | qprime/turnstile | WARN: no local path |
| broken | ~/Code/gone | qprime/broken | ERROR: path not found |

Errors: <N> | Warnings: <N> | OK: <N>
```

## Rules

1. **Read-only** — status is observational (FG-4)
2. **Registry is truth** — all data from `registry/projects.yaml` (FG-1)
3. **Report broken references** — core purpose of health check (FG-6)
4. **Don't guess** — if no profile exists, say "None", don't infer
