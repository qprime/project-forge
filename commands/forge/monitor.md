---
description: Analyze prompt logs and project changes to find recurring patterns, candidate skills, and generalizable rules. Use to discover what should become baseline capabilities.
---

# /monitor — Change Pattern Analysis

Analyze changes for: $ARGUMENTS

**Invariant check:** Read-only operation (FG-4). Reads prompt logs, git history, and project state. Outputs proposals, never auto-applies them.

## Usage

```
/monitor prompts              # analyze prompt log for recurring patterns
/monitor changes              # analyze recent git activity across projects
/monitor all                  # both prompts and changes
/monitor prompts --since 7d   # last 7 days of prompts
/monitor changes --project mill_ui  # one project's changes
```

## Data Sources

### Prompt Log
- `~/.claude/prompt-log.jsonl` — every user prompt, timestamped, tagged by project
- Logged by `UserPromptSubmit` hook in `~/.claude/hooks/log-prompts.sh`

### Git Activity
- Recent commits across all registry projects with local paths
- Commit messages, changed files, and diff summaries

### Permission Log
- `~/.claude/permission-log.jsonl` — commands that triggered permission prompts
- Indicates tooling gaps or missing allowlist entries

## Process

### Step 1: Gather Data

**For `prompts`:**
1. Read `~/.claude/prompt-log.jsonl`
2. Parse entries, group by project
3. Apply `--since` filter if provided (default: last 30 days)

**For `changes`:**
1. Read `registry/projects.yaml` for project paths
2. For each project with a local path, run `git log --oneline --since=<period>` 
3. Optionally read `~/.claude/permission-log.jsonl` for tooling patterns

### Step 2: Pattern Extraction

Look for these pattern categories:

#### Repeated Workflows (→ candidate skills)
- Same sequence of actions requested across multiple prompts
- Prompts that start with similar intent ("review the...", "check if...", "add a...")
- Multi-step processes that could be codified into a single skill

#### Repeated Corrections (→ candidate CLAUDE.md rules or feedback memories)
- "No, don't..." / "Stop doing..." / "Actually..." patterns
- Same correction appearing in multiple conversations
- Workarounds for behavior that should be default

#### Cross-Project Patterns (→ candidate baseline capabilities)
- Similar changes made across 2+ projects (same kind of refactor, same new pattern)
- Similar commit message patterns indicating shared workflow
- Permission log entries suggesting common tooling needs

#### Domain Knowledge (→ candidate invariants or glossary)
- Repeated explanations of the same concept
- Questions about the same architectural decision
- Clarifications that shouldn't need repeating

### Step 3: Score and Rank

For each detected pattern, assess:

| Dimension | Question |
|---|---|
| Frequency | How many times has this appeared? |
| Breadth | How many projects does it span? |
| Cost | How much effort does it cost to not have this codified? |
| Specificity | Is it specific enough to codify, or too vague? |

Only surface patterns scoring well on at least 2 dimensions.

### Step 4: Generate Proposals

For each qualifying pattern, produce a structured proposal:

```
## Proposal: <title>

**Type:** skill / rule / capability / invariant / allowlist-entry
**Source:** <N> occurrences across <projects> in <time period>
**Evidence:**
- [timestamp] prompt/commit excerpt
- [timestamp] prompt/commit excerpt

**Proposed action:**
- For skills: draft skill description and trigger condition
- For rules: draft CLAUDE.md entry or feedback memory
- For capabilities: draft baseline capability entry
- For invariants: draft invariant with classification
- For allowlist: draft settings.json addition

**Confidence:** high / medium / low
```

### Step 5: Report

```
## Monitor Report — <date>

### Data Summary
- Prompts analyzed: N (across M projects, last K days)
- Commits analyzed: N (across M projects)
- Permission events: N

### Proposals
[Ranked list of proposals from Step 4]

### Observations
[Patterns noticed but not strong enough to propose — watch list]

### Recommended Actions
- `/rebase <project>` if proposals affect the baseline
- Create GitHub issue for complex proposals
- Update `~/.claude/settings.json` for allowlist proposals
```

## Rules

1. **Read-only** — never modify projects, baseline, or settings (FG-4)
2. **Proposals, not actions** — surface patterns and recommend; human decides what gets codified
3. **Evidence-based** — every proposal must cite specific prompts, commits, or events
4. **Registry is truth** — use `registry/projects.yaml` for project discovery (FG-1)
5. **Privacy-aware** — prompt logs may contain sensitive content; summarize patterns, don't dump raw prompts in reports unless directly relevant
6. **Threshold over noise** — better to miss a weak pattern than flood with false positives
