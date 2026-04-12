---
description: Review system-level Claude Code permission log and allowlist. Shows what commands triggered permission prompts, suggests allowlist updates.
---

# Permission Review

You are reviewing the system-level Claude Code permission audit log and allowlist configuration.

## Files

- **Log:** `~/.claude/permission-log.jsonl` — JSONL, one entry per non-allowlisted Bash command
- **Settings:** `~/.claude/settings.json` — `permissions.allow` is the allowlist, `hooks.PreToolUse` wires the hook
- **Hook:** `~/.claude/hooks/log-permission-prompts.sh` — the script that does the logging

## Workflow

1. **Read the log** — `~/.claude/permission-log.jsonl`
2. **Summarize** — group entries by command prefix and project, show counts and recency
3. **Identify candidates** — commands that appear frequently and look safe to allowlist
4. **Check sync** — verify the hook's `ALLOWED_PREFIXES` array matches `permissions.allow` in settings.json
5. **Present findings** — show the summary table and recommendations
6. **If user approves changes** — update both `~/.claude/settings.json` and `~/.claude/hooks/log-permission-prompts.sh` to stay in sync

## Output Format

### Permission Log Summary
Period: [earliest timestamp] to [latest timestamp]
Total entries: N

| Prefix | Count | Projects | Example Command |
|--------|-------|----------|-----------------|
| cd     | 5     | forge, penumbra | `cd /path && ...` |

### Allowlist Sync Check
Whether the hook's ALLOWED_PREFIXES and settings.json permissions.allow are in sync.

### Recommendations
Commands that appear frequently and could be added to the allowlist, with reasoning.

## Rules

- **Read-only by default** — present findings and wait for approval before modifying settings
- **Always update both files** — if adding to the allowlist, update settings.json AND the hook script
- If the log is empty, say so and confirm the hook is wired correctly
