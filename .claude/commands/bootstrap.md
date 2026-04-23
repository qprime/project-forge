---
description: Bootstrap or rebase a project's Claude Code configuration from the capability baseline. Use for new projects or to sync existing projects with updated baseline capabilities.
---

# Project Bootstrap

You are applying the capability baseline to a project. This creates or updates CLAUDE.md, skills, and invariant scaffolds based on project context.

**Invariant check:** This operation writes to other projects — FG-4 (Read-Before-Write) requires explicit user approval before any write.

## Usage

Determine mode from: $ARGUMENTS

| Argument | Mode | Action |
|----------|------|--------|
| `new <target>` | Bootstrap | Create fresh project configuration |
| `rebase <target>` | Rebase | Update existing project to current baseline |
| (none) | Help | Show usage |

Target can be a local path, git remote URL, or project name from registry:
- Local: `~/Code/mill_ui`, `.`, `/home/user/project`
- Remote: `git@github.com:qprime/homenet.git`
- Registry name: `homenet` (resolved via `registry/projects.yaml`)

---

## Target Resolution

### Local Path
If target starts with `/`, `~`, or `.`: verify directory exists, use directly.

### Git Remote URL
If target contains `:` or ends with `.git`:
1. Clone to `/tmp/bootstrap_<project-name>`
2. If directory already exists, `git pull` instead
3. After work is committed, prompt: "Push changes to remote? (y/n)"
4. If approved, push. Clean up temp clone.

### Registry Name
If target matches a project key in `registry/projects.yaml`, resolve to its `repo` field as a GitHub URL, or use its `path` field if present.

---

## Baseline Reference

Read before proceeding:
- `baseline/capability_baseline.md` — capabilities, tags, translation protocol
- `baseline/coding_guidelines.md` — language-specific guidelines
- `baseline/enforcement_matrix.md` — enforcement mapping

These are the canonical source (FG-2). Never modify them during bootstrap — they are read-only inputs.

---

## Mode: Bootstrap New Project

### Step 1: Gather Context
Ask user or infer from path:
1. **Project name** — directory name or explicit
2. **Brief description** — what does this project do?
3. **Language/runtime** — Python 3.x, Node, Rust, etc.
4. **Domain** — what kind of system is this?

### Step 2: Propose Tags
Based on context, propose applicable tags from baseline. Wait for user confirmation.

### Step 3: Select Capabilities
From confirmed tags:
1. Start with all always-on capabilities
2. Add conditional capabilities matching tags
3. Include dependencies (per dependency graph)

Present summary. Wait for confirmation.

### Step 4: Determine Domain Framing
Propose persona name, domain terminology, key concerns.

### Step 5: Generate Configuration
Create:
1. **CLAUDE.md** — baseline persona + project context + capabilities table + invariant references
2. **`.claude/commands/engineer.md`** — domain-framed implementation skill
3. **`.claude/commands/debug.md`** — domain-framed debugging skill
4. **`.claude/commands/spec.md`** — specification drafting
5. **`.claude/commands/architect.md`** — design thinking partner
6. **`.claude/commands/review.md`** — code, spec, and system review
7. **`.claude/commands/close-out.md`** — verification + commit
8. **`docs/invariants/README.md`** — scaffold for project invariants

### Step 6: Verify Artifacts (REQUIRED — do not skip)

Before committing, confirm every artifact from Step 5 exists on disk. Run the bootstrap checklist below. If any item fails, fix it — do not proceed to commit with a partial bootstrap.

**Bootstrap Artifact Checklist:**

| # | Path | Required Content |
|---|------|------------------|
| 1 | `CLAUDE.md` | persona, capabilities table, invariant references, Don't section |
| 2 | `.claude/commands/engineer.md` | domain-framed, references project-specific files |
| 3 | `.claude/commands/debug.md` | domain-framed |
| 4 | `.claude/commands/spec.md` | matches baseline spec template |
| 5 | `.claude/commands/architect.md` | persona section filled in (no `[DOMAIN_*]` placeholders) |
| 6 | `.claude/commands/review.md` | matches baseline review template |
| 7 | `.claude/commands/close-out.md` | verification + commit phases |
| 8 | `docs/invariants/README.md` | scaffold explaining invariant convention for this project |

**Verification commands** (run these — don't trust your memory of what you wrote):

```
ls CLAUDE.md .claude/commands/{engineer,debug,spec,architect,review,close-out}.md docs/invariants/README.md
grep -L 'DOMAIN_EXPERTISE\|DOMAIN_PERSPECTIVE\|DOMAIN_MENTAL_MODELS' .claude/commands/architect.md
```

The `ls` must show all 8 files. The `grep -L` must list `architect.md` (meaning no unfilled placeholders remain). If either check fails, fix the gap and re-verify before continuing.

Report the checklist result inline — one line per item, ✓ or ✗. The user can see whether bootstrap actually completed or stopped halfway.

### Step 7: Commit
Stage all created files, commit with structured message. If remote target, prompt to push.

### Step 8: Summary
Report files created, tags, capabilities selected, commit hash, **and the Step 6 checklist result**. If any artifact was skipped or failed verification, surface it explicitly — do not bury it. If the project's `targets` include `codex`, remind the user to run `/codex-sync <project>` to generate Codex equivalents.

---

## Mode: Rebase Existing Project

### Step 1: Read Current State
Read existing CLAUDE.md, skills, invariants, sample codebase.

### Step 2: Infer Current Tags
From existing configuration, propose tags. Show current vs target baseline version.

### Step 3: Diff Capabilities
Compare current skills against baseline:
- Capabilities to ADD (new in baseline)
- Capabilities to UPDATE (rules changed)
- Project-specific content to PRESERVE
- Overrides currently in place

### Step 4: Generate Updates
Preserve project-specific sections. Update capability-derived sections. Present diffs before applying.

### Step 5: Apply
After user confirms, write files. Do not commit yet.

### Step 6: Verify Artifacts (REQUIRED)
Run the same Bootstrap Artifact Checklist from the new-project mode (Step 6 above). Rebase must leave the project in a fully-bootstrapped state — if a baseline file was missing before rebase, it should be present after. Report the checklist result inline.

### Step 7: Commit
Stage specific files, commit.

### Step 8: Summary
Report files updated/unchanged, preserved content, overrides maintained, **and the checklist result**. If the project's `targets` include `codex`, remind the user to run `/codex-sync <project>` to regenerate Codex files.

---

## Override Handling

If rebase detects a conflict between baseline and project:
1. **Identify** the conflict
2. **Present** to user with options: accept baseline, keep override, or discuss
3. **Document** approved overrides in project CLAUDE.md

---

## Rules

1. **Never overwrite without confirmation** — show diffs for every file before writing
2. **Preserve project-specific content** — domain knowledge, custom invariants, documented overrides
3. **Label source in diffs** — mark each changed section as `[from baseline]` or `[project-specific]`
4. **Ask the user when:** (a) inferred tags conflict with user-provided tags, (b) an existing skill's persona section diverges from the baseline template in a way that can't be auto-preserved, (c) a documented override contradicts a new baseline capability
5. **Update registry** — after successful bootstrap, update `registry/projects.yaml` with `baseline_version`

---

## Related Documents

- `baseline/capability_baseline.md` — the baseline itself
- `baseline/README.md` — full bootstrap process documentation
- `baseline/enforcement_matrix.md` — how guidelines are enforced
- `registry/projects.yaml` — project registry (FG-1)
