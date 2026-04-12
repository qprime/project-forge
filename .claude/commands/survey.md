---
description: Read a project and build/update its intelligence profile. Use to gather information about a project's architecture, patterns, current state, and configuration.
---

# /survey — Project Intelligence Gathering

Survey and build a profile for: $ARGUMENTS

**Invariant check:** This is a read-only operation (FG-4). Forge reads the project freely. Output is stored as a derived profile (FG-3 — never manually edit profiles, re-survey to update).

## Usage

```
/survey <target>
```

Target: local path, git remote URL, or registry project name.

Examples:
```
/survey ~/Code/mill_ui
/survey mill_ui
/survey all           # survey all projects with paths in registry
```

## Process

### Step 1: Resolve Target

Look up project in `registry/projects.yaml`. Resolve to local path or clone.

### Step 2: Read Project State

Gather information from the project:

1. **Configuration:**
   - `CLAUDE.md` — persona, capabilities, invariants, conventions
   - `.claude/commands/*.md` — skills and their descriptions
   - `docs/invariants/` — invariant definitions

2. **Structure:**
   - Top-level directory layout
   - Key source directories and their purpose
   - Entry points, main modules

3. **Git State:**
   - Recent commits (last 20) — what's been worked on
   - Active branches
   - Open issues (via `gh issue list` if accessible)

4. **Patterns:**
   - Architecture style (pipeline, MVC, event-driven, etc.)
   - Data model approach (dataclasses, ORM, etc.)
   - Testing patterns (pytest, what's covered)
   - Domain-specific patterns

5. **Baseline Status:**
   - Current `baseline_version` from registry
   - Actual baseline date from project's config (if detectable)
   - Drift indicators (skills that don't match current baseline templates)

### Step 3: Build Profile

Generate a structured profile at `profiles/<project-name>.yaml`:

```yaml
project: <name>
surveyed_at: <ISO date>
surveyed_commit: <hash>

configuration:
  has_claude_md: true/false
  has_invariants: true/false
  skills: [list of skill names]
  tags: [inferred tags]

structure:
  language: Python 3.x / TypeScript / etc.
  entry_points: [list]
  key_directories:
    - path: src/
      purpose: Main source
  test_coverage: description of test setup

architecture:
  style: pipeline / event-driven / CRUD / etc.
  patterns: [list of observed patterns]
  key_abstractions: [list of central types/classes]

current_state:
  recent_focus: description of recent work (from git log)
  open_issues: N
  active_branches: [list]

baseline_status:
  registry_version: "2026-04-05"
  detected_drift: [list of drift indicators]

notes: |
  Free-form observations about the project that don't fit
  the structured fields above.
```

### Step 4: Present Results

Show the profile to the user. Highlight:
- Key architectural patterns
- Baseline drift (if any)
- Anything surprising or noteworthy

### Step 5: Save

Write profile to `profiles/<project-name>.yaml`. Update `registry/projects.yaml` if new information was discovered (e.g., missing tags, updated description).

## Rules

1. **Read-only** — never modify the surveyed project (FG-4)
2. **Profiles are derived** — never manually edit them (FG-3). Re-run `/survey` to update
3. **Registry stays canonical** — profile supplements registry, doesn't replace it (FG-1)
4. **Note staleness** — if project path doesn't resolve, report it (FG-6)
