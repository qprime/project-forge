---
description: Generate Codex CLI configuration from Claude source of truth. Use when setting up dual-deployment (Claude + Codex) for a project.
---

# /codex-sync — Generate Codex Config from Claude Sources

Generate Codex configuration for: $ARGUMENTS

**Invariant check:** This operation writes to other projects — FG-4 (Read-Before-Write) requires explicit user approval before any write.

## Usage

```
/codex-sync <target>          # Generate Codex files for a project
/codex-sync <target> --clean  # Remove generated Codex files
/codex-sync all               # Sync all registry projects with targets: [codex]
```

Target: local path, git remote URL, or registry project name.

Examples:
```
/codex-sync mill_ui
/codex-sync ~/Code/penumbra-poc
/codex-sync all
/codex-sync mill_ui --clean
```

## Source of Truth

Claude files are canonical. Codex files are generated artifacts:

| Claude (source) | Codex (generated) | Translation |
|---|---|---|
| `CLAUDE.md` | `AGENTS.md` | Section-mapped content adaptation |
| `.claude/commands/*.md` | `.codex/skills/*/SKILL.md` | Add YAML frontmatter, preserve body |
| `.claude/settings.json` hooks | `.codex/config.toml` | Hook intents → exec policy rules |

## Target Resolution

Same rules as `/bootstrap`:

### Local Path
If target starts with `/`, `~`, or `.`: verify directory exists, use directly.

### Git Remote URL
If target contains `:` or ends with `.git`:
1. Clone to `/tmp/codex-sync_<project-name>`
2. If directory already exists, `git pull` instead
3. After work is committed, prompt: "Push changes to remote? (y/n)"

### Registry Name
If target matches a project key in `registry/projects.yaml`, resolve to its `path` field (if present) or `repo` field as a GitHub URL.

### `all` Target
Iterate all projects in `registry/projects.yaml` where `targets` includes `codex`. Skip projects without local paths (report them).

---

## Process: Generate

### Step 1: Read Claude Sources

From the target project, read:
1. `CLAUDE.md` — project instructions
2. `.claude/commands/*.md` — all skill files
3. `.claude/settings.json` — hooks and permissions

If `CLAUDE.md` doesn't exist, abort with error — project must have Claude config to sync from.

### Step 2: Generate AGENTS.md

Translate `CLAUDE.md` → `AGENTS.md` using the section mapping:

| CLAUDE.md Section | AGENTS.md Treatment |
|---|---|
| Tags | Preserve |
| Mental Model | Preserve |
| Capabilities table | Preserve |
| Key Directories | Preserve — update paths if Codex uses different structure |
| Invariants table | Preserve |
| Don't | Preserve |
| Domain Framing | Rewrite: replace `/skill` references with Codex skill equivalents |
| Quick Commands | Rewrite or drop: tool-specific |
| Code Style | Preserve |

Sections not listed are preserved by default. Only rewrite content containing explicit Claude tool references (`/engineer`, `.claude/commands/`, `$ARGUMENTS`).

**Rewriting rules for Domain Framing:**
- `/engineer` → `engineer skill`
- `/debug` → `debug skill`
- `/architect` → `architect skill`
- `/review` → `review skill`
- `/monitor` → `monitor skill`
- `/survey` → `survey skill`
- `/bootstrap` → `bootstrap skill`
- `/rebase` → `rebase skill`
- `/codex-sync` → `codex-sync skill`
- `.claude/commands/` → `.codex/skills/`

**Provenance header:** First line of `AGENTS.md` (no frontmatter in this file):
```
<!-- Generated from Claude config by project-forge. Do not edit directly. -->
```

### Step 3: Generate Skill Files

For each `.claude/commands/<name>.md`:

1. Parse the Claude skill format:
   ```markdown
   ---
   description: <description text>
   ---
   
   # <title>
   
   <body>
   ```

2. Generate `.codex/skills/<name>/SKILL.md`:
   ```markdown
   ---
   name: <name>
   description: <description text>
   version: "1.0"
   ---
   <!-- Generated from Claude config by project-forge. Do not edit directly. -->
   
   # <title>
   
   <body with minimal rewriting>
   ```

   **Provenance header:** Placed on the line immediately after the closing `---` of YAML frontmatter, before the body.

3. **Body rewriting (minimal):**
   - `$ARGUMENTS` → remove or replace with Codex equivalent if one exists
   - `/engineer` → `engineer skill` (when used as invocation references, not as section headers)
   - `.claude/commands/` → `.codex/skills/`
   - Preserve all domain logic, invariant references, behavioral rules, and section structure

### Step 4: Generate Config (settings.json → config.toml)

If `.claude/settings.json` exists in the target project, translate to `.codex/config.toml`:

**Hook translation:**

| Claude hook type | Codex equivalent |
|---|---|
| `PreToolUse` | `[exec_policy]` rule with `on = "before_tool"` |
| `PostToolUse` | `[exec_policy]` rule with `on = "after_tool"` |
| `UserPromptSubmit` | `[exec_policy]` rule with `on = "prompt_submit"` |
| Custom event hooks | Comment block documenting intent — no direct Codex equivalent |

For each hook entry in `settings.json`:
1. Extract the hook type, matcher (if any), and command
2. Map to a `[[exec_policy.rules]]` entry in TOML
3. If no direct mapping exists, add a TOML comment explaining the Claude hook intent

**Permission allowlist translation:**

| Claude permission | Codex equivalent |
|---|---|
| `allow` entries (Bash commands) | `sandbox = "permissive"` or specific `[[exec_policy.rules]]` with `action = "allow"` |
| `deny` entries | `[[exec_policy.rules]]` with `action = "deny"` |

**Provenance header:** First line of `.codex/config.toml`:
```toml
# Generated from Claude config by project-forge. Do not edit directly.
```

If `.claude/settings.json` doesn't exist, skip this step.

### Step 5: Present Changes

Before writing, show the user:
1. Files to be created/updated
2. Summary of translations applied
3. Any sections that required rewriting (flag for review)
4. Any hooks that had no direct Codex mapping (documented as comments)

Wait for user approval before writing.

### Step 6: Write Files

After approval:
1. Create `.codex/skills/` directory structure
2. Write `AGENTS.md` to project root
3. Write each `SKILL.md` to `.codex/skills/<name>/SKILL.md`
4. Write `.codex/config.toml` (if `.claude/settings.json` exists)

### Step 7: Report

```
## Codex Sync Complete: <project>

### Generated Files
| File | Source | Status |
|------|--------|--------|
| AGENTS.md | CLAUDE.md | Created/Updated |
| .codex/skills/<name>/SKILL.md | .claude/commands/<name>.md | Created/Updated |
| .codex/config.toml | .claude/settings.json | Created/Updated/Skipped |

### Translations Applied
- <N> sections preserved verbatim
- <N> sections rewritten (list which ones)
- <N> hooks translated, <N> documented as comments (no direct mapping)
```

---

## Process: Clean (`--clean`)

1. Find all files containing the provenance header:
   - Markdown files: `<!-- Generated from Claude config by project-forge. Do not edit directly. -->`
   - TOML files: `# Generated from Claude config by project-forge. Do not edit directly.`
2. List them and ask for confirmation
3. Remove only those files
4. Remove empty `.codex/skills/*/` directories
5. Remove `.codex/skills/` and `.codex/` if empty

---

## Registry Integration

### `targets` Field

The `targets` field in `registry/projects.yaml` controls which projects are eligible for `/codex-sync all`:

```yaml
mill_ui:
  repo: qprime/mill_ui
  path: ~/Code/mill_ui
  tags: [python, pipeline, declarative-input, github-issues]
  targets: [claude, codex]  # eligible for codex-sync
```

Projects without a `targets` field default to `[claude]` — they are skipped by `/codex-sync all`.

---

## Rules

1. **Claude is source of truth** — never modify Claude files during codex-sync
2. **Approval before write** — always show changes and wait for confirmation (FG-4)
3. **Provenance headers required** — every generated file must be marked
4. **Clean only removes generated files** — identified by provenance header, never deletes hand-authored files
5. **Minimal rewriting** — preserve domain logic; only translate tool-specific references
6. **Registry is truth** — use `registry/projects.yaml` for `all` target resolution (FG-1)
7. **Report unmapped hooks** — document hooks with no direct Codex equivalent as TOML comments

## Related

- `/bootstrap` — creates Claude configuration (source files for codex-sync); auto-generates Codex files when `targets` includes `codex`
- `/rebase` — updates Claude configuration; auto-regenerates Codex files when `targets` includes `codex`
- `/drift` — detects stale Codex configs via content hash comparison
- `docs/invariants/global.md` — FG-4 authorizes this operation
