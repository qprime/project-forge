---
description: Cross-project pattern analysis — compare how projects solve similar problems, find shared patterns, and identify divergences. Use for cross-project learning and pattern extraction.
---

# /compare — Cross-Project Analysis

Compare projects for: $ARGUMENTS

**Invariant check:** Read-only operation (FG-4). Reads multiple projects to analyze patterns.

## Usage

```
/compare <project1> <project2> [topic]
/compare <project> --patterns
/compare all --pattern <pattern-name>
```

Examples:
```
/compare mill_ui homenet validation      # how do they handle validation?
/compare mill_ui --patterns              # what patterns does mill_ui use?
/compare all --pattern frozen-dataclass  # who uses frozen dataclasses?
```

## Process

### Step 1: Resolve Projects

Look up projects in `registry/projects.yaml`. Check for existing profiles in `profiles/`.

If profiles are stale or missing, suggest running `/survey` first.

### Step 2: Read Relevant Code

Based on the comparison topic:
- Read both projects' CLAUDE.md for capabilities and conventions
- Read relevant source files in both projects
- Check invariant files for related rules
- Read profiles for cached architectural information

### Step 3: Analyze

Compare the projects across dimensions relevant to the topic:

- **Approach:** How does each project solve the problem?
- **Patterns:** What patterns are shared? What's different?
- **Maturity:** Is one implementation more evolved?
- **Applicability:** Could one project's approach benefit the other?

### Step 4: Report

```
## Comparison: <project1> vs <project2> — <topic>

### <project1> Approach
- How it works, key files, patterns used

### <project2> Approach
- How it works, key files, patterns used

### Shared Patterns
- Patterns both projects use

### Divergences
- Where approaches differ and why

### Opportunities
- Could one approach benefit the other?
- Is there a generalizable pattern for the baseline?

### Baseline Candidates
- Patterns observed in 3+ projects that could become capabilities
```

## Rules

1. **Read-only** — never modify compared projects (FG-4)
2. **Use profiles when available** — don't re-survey what's already profiled
3. **Be specific** — reference actual files, functions, patterns — not abstractions
4. **Baseline awareness** — flag patterns that could become new baseline capabilities
