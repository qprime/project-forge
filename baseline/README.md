# Claude Code Project Bootstrap Guide

**Status:** Reference Document

A step-by-step process for bootstrapping a new Claude Code project with AI infrastructure — skills, invariants, hooks, and starter code. Derived from the mill_ui pattern, generalized for any project.

---

## Overview

The bootstrap creates five layers of infrastructure:

| Layer | Purpose | Files |
|-------|---------|-------|
| **Agent Instructions** | What the AI agent is, how it behaves | `CLAUDE.md` |
| **Skills** | Specialized personas activated by `/command` | `.claude/commands/*.md` |
| **Invariants** | Rules that cannot be violated without amendment | `docs/invariants/*.md` |
| **Hooks & Settings** | Automated quality enforcement | `.claude/settings.json`, `.claude/hooks/` |
| **Starter Code** | Functional skeleton demonstrating patterns | Project-specific |

These layers interact: CLAUDE.md references invariants, skills reference invariants, coding guidelines inform invariant design, and hooks enforce code style from the guidelines.

---

## Project Prompt Template

Before bootstrapping, create a project prompt that defines these inputs. The bootstrap process consumes this prompt to generate all artifacts.

### Required Inputs

| Input | Description | Example |
|-------|-------------|---------|
| **Project name** | Short identifier | `mill_ui`, `invoice_pipeline` |
| **One-line description** | What it does | "CNC toolpath generator from declarative markup" |
| **Agent role** | Who the agent is | "CNC toolpath engineer", "network operator" |
| **Core workflow** | Pipeline stages or state machine | "Parse → Validate → Plan → Generate → Verify" |
| **Language** | Primary implementation language | Python 3.10+, TypeScript, Rust |

### Constraints & Safety

| Input | Description | Example |
|-------|-------------|---------|
| **Hard constraints** | Rules that cannot be violated | "No committed secrets", "dry-run before destructive ops" |
| **Safety-critical concerns** | What can go wrong | "Hardware damage from bad toolpaths", "data loss", "lockout" |
| **Secrets handling** | What credentials exist, where they live | "SSH keys in ~/.ssh, API tokens in .env" |

### Architectural Decision Points

These determine which conditional guidelines become invariants:

| Decision | If Yes | If No |
|----------|--------|-------|
| **Extensible IR?** Does the project use an intermediate representation that new features extend without code changes? | §5 Flat Type Systems becomes DS-4: FLAT_IR (HARD) | Use typed dataclasses freely |
| **Declarative user input?** Does the project accept user-facing input that describes *what*, not *how*? | §13 Feature Completeness becomes invariant; input format must cover all features | Skip |
| **Union type dispatch?** Does the project dispatch on variant types where missing a case causes silent failure? | §17 Exhaustiveness becomes DS-6: EXHAUSTIVE_DISPATCH (HARD) | Convention only |

### Starter Code Specification

Define the initial functional code the bootstrap should generate:

| Input | Description | Example |
|-------|-------------|---------|
| **Shared library modules** | Common helpers needed | Logging, config loading, SSH connections, error formatting |
| **Initial tools/commands** | 3-5 specific tools with one-line descriptions | `discover.py` — scan network for devices; `provision.py` — configure a device from template |
| **Config templates** | What environment/config files | `.env.example` with DB_HOST, API_KEY; `config.yaml` schema |
| **Project-specific directories** | Beyond the standard structure | `tools/`, `templates/`, `inventory/` |

### Subsystem Identification

List the major subsystems that will each get their own invariant file:

| Subsystem | Applies To | Key Constraints |
|-----------|------------|-----------------|
| *Example:* Data Structures | Model classes, serialization | Immutability, round-trip completeness |
| *Example:* Pipeline | Parser → IR → Backend flow | Layer separation, no pass-through |
| *Example:* Security | Auth, secrets, credentials | No committed secrets, env-only config |

### Example Project Prompt

```markdown
# Project: mill_ui

CNC toolpath generator that converts declarative PML markup into machine-ready G-code.

## Agent Role
CNC toolpath engineer. Expertise in machining operations, coordinate systems,
and safe material removal. Conservative about tool engagement, explicit about
assumptions.

## Core Workflow
Parse PML → Build Domain Model → Validate Constraints → Plan Operations →
Generate Toolpaths → Write G-code → Verify Safety

## Language
Python 3.12+

## Constraints
- HARD: No rapids into material
- HARD: Validate all toolpaths against stock boundaries
- HARD: Single unit system (mm internally, convert at boundaries)
- STRUCTURAL: IR layer required between parsing and generation

## Safety-Critical
- Bad toolpath = broken tool, damaged workpiece, potential injury
- Post-generation verification mandatory
- Dry-run simulation before any real output

## Architectural Decisions
- Extensible IR: YES — new operation types added via flat type + data dict
- Declarative input: YES — PML describes what to make, not how
- Union dispatch: YES — unhandled operation types would produce incomplete output

## Starter Code
Shared library:
- `lib/logging.py` — structured session logging
- `lib/config.py` — load .env and config files
- `lib/units.py` — boundary conversion helpers

Initial tools:
- `parse_pml.py` — parse PML file, emit domain model JSON
- `validate.py` — check domain model against constraints
- `generate.py` — produce G-code from validated model
- `simulate.py` — dry-run toolpath verification

Config templates:
- `.env.example` — MACHINE_PROFILE, OUTPUT_DIR
- `machines/default.yaml` — machine capability profile

## Subsystems
| Subsystem | Applies To | Key Constraints |
|-----------|------------|-----------------|
| Data Structures | Domain model, PML AST | Frozen dataclasses, tuple collections |
| Pipeline | Parse → Generate flow | Layer separation, IR checkpoint |
| Toolpath Safety | G-code generation | No rapids into material, boundary checks |
| Serialization | Model ↔ JSON/YAML | Round-trip completeness, determinism |
```

---

## Phase 1: Directory Structure

Create the skeleton first. Every project follows this shape, with project-specific directories added alongside.

```
project/
├── .claude/
│   ├── commands/          # skill definitions (slash commands)
│   ├── hooks/             # post-tool-use hooks (linting, formatting)
│   └── settings.json      # hook configuration
├── docs/
│   └── invariants/        # subsystem invariant files
│       └── README.md      # global axioms + subsystem index
├── .gitignore
├── CLAUDE.md              # master agent instructions
└── README.md              # human-facing project overview
```

**Prompt to generate structure:**
> Create the directory structure for a new project at `<path>`. Include `.claude/commands/`, `.claude/hooks/`, `docs/invariants/`, and the root files: `CLAUDE.md`, `README.md`, `.gitignore`. Add project-specific directories: `<list them>`.

---

## Phase 2: CLAUDE.md — Master Agent Instructions

This is the most important file. It defines the agent's identity, capabilities, constraints, and escape hatches. It's loaded into context on every conversation.

### Structure

```markdown
# CLAUDE.md — <Project Name>

**Status:** Active | **As-Of:** YYYY-MM-DD

## Agent Constraints
[Hard limits on agent behavior — e.g., "Do not use EnterPlanMode"]

## Baseline Persona
[Who the agent is. 2-3 sentences that establish domain expertise and working philosophy.]

## What This Is
[1-2 sentences: what the project does, at the highest level.]

## Mental Model
[The core transformation or workflow, expressed as a pipeline or state machine.]

## Quick Commands
[Copy-pasteable commands for common operations. The agent uses these; so does the human.]

## Code Style
[Language-specific conventions. Keep it short — link to coding_guidelines.md for details.]

## Capabilities
[Table of existing features. Check-before-implementing gate.]

## Don't
[Anti-patterns. Things the agent must not do. Be specific.]

## <Domain-Specific Principle>
[The project's core design principle — e.g., "Tool-First Principle", "PML-First Principle".]

## Invariants (MANDATORY)
[Pointer to docs/invariants/README.md. Statement that invariants must be read before modifying subsystems.]

## When Stuck
[Pointers to documentation, examples, and the user.]
```

### Key Design Decisions

- **Capabilities table prevents reimplementation.** LLMs reinvent existing features unless told they exist. The table is a mandatory pre-check.
- **Don't section is specific, not aspirational.** Each entry addresses a real mistake the agent has made or is likely to make.
- **Quick Commands are authoritative.** The agent should use these exact commands, not improvise alternatives.

**Prompt to generate:**
> Write CLAUDE.md for a project that [description]. The agent's role is [role]. The core workflow is [workflow]. Key constraints: [list]. Existing capabilities: [list or "none yet"]. Anti-patterns to prevent: [list].

---

## Phase 3: Invariants

Invariants are the load-bearing rules. They are not style preferences — violating them breaks the system. They exist in a hierarchy: global axioms apply everywhere, subsystem invariants apply to specific areas.

### Global Axioms (docs/invariants/README.md)

Start with 5-12 global rules that apply across the entire project. Each gets a prefixed ID.

**ID prefix convention:**
| Prefix | Domain |
|--------|--------|
| SEC- | Security, auth, secrets |
| OPS- | Operations, workflows |
| NET- | Network, connectivity |
| CFG- | Configuration, environment |
| INV- | Inventory, documentation |
| TL- | Tooling, scripts |
| DS- | Data structures |
| PL- | Pipeline, layer contracts |
| TST- | Testing |

**Invariant classification:**
| Type | Meaning |
|------|---------|
| HARD | Violation breaks the system |
| STRUCTURAL | Requires coordinated migration to change |
| POLICY | Current default, can change with care |
| FALLBACK | Defensive behavior signaling an upstream bug |

**README.md structure:**
```markdown
# System Invariants

## Global Axioms
[Table: ID, Invariant Name, Rule]

## Regression Traps
[Table: ID, Invariant Name, Why It's a Trap]

## Subsystem Invariant Files
[Table: Subsystem, File, Applies To]

## Core Principles (Quick Reference)
[Right/Wrong code examples for the most-violated rules]

## Error Philosophy
[Table: Category, Behavior, Use When]

## Amendment Process
[How to change an invariant — stop, evaluate, amend explicitly, same commit]
```

### Deriving Invariants from Coding Guidelines

The coding guidelines document (`coding_guidelines.md`) is a source of invariants, but not every guideline becomes an invariant. The mapping:

| Guideline Section | Invariant? | Why / Why Not |
|-------------------|-----------|---------------|
| §1 Immutability by Default | **YES — DS-type** | Mutation of shared state corrupts data. HARD invariant. |
| §2 Pipeline Architecture | **YES — PL-type** | Layer violations bypass validation. STRUCTURAL invariant. |
| §3 Function Purity | **YES — DS-type** | Input mutation corrupts shared state. HARD invariant. |
| §4 Error Handling | **YES — global** | Silent partial output is never allowed. HARD invariant. |
| §5 Data Structure Design | **Conditional** | Flat-vs-class is domain-dependent. Only invariant if the project commits to flat IR. |
| §6 Testing | **NO** | Testing conventions are style/process, not system-breaking. Document in code style, not invariants. |
| §7 Coordinate/Unit Discipline | **YES — CS-type** | Mixed units produce wrong output. HARD invariant. |
| §8 Defaults and Configuration | **Partial** | "Document defaults" is process. "Defaults must agree" is STRUCTURAL. |
| §9 Validation | **YES — global** | Validate at construction + boundaries. HARD invariant. |
| §10 Invariant Management | **META** | This is the invariant system itself — the amendment process. |
| §11 Code Style | **NO** | Style is enforced by hooks (ruff), not invariants. |
| §12 Output/Serialization | **YES — PL-type** | Non-deterministic output breaks golden testing. STRUCTURAL. |
| §13 Feature Completeness | **Conditional** | Only invariant if the project has a declarative-input-first principle. |
| §14 Safety-Critical Constraints | **YES — SEC-type** | Safety violations cause real harm. HARD invariant. |
| §15 Dependency Direction | **YES — PL-type** | Inverted deps create circular imports. STRUCTURAL invariant. |
| §16 Enums vs String Literals | **NO** | Design guidance, not system-breaking. |
| §17 Union Types / Exhaustiveness | **Conditional** | Exhaustive dispatch is HARD if unhandled variants cause silent drops. |
| §18 Logging | **NO** | Style convention. Enforce via code review, not invariants. |
| §19 Exception Types | **NO** | Convention. Consistent, but not system-breaking if violated. |
| §20 Error Semantics by Layer | **YES — PL-type** | Per-item isolation prevents batch kills. STRUCTURAL. |
| §21 Expected-Failure Exceptions | **NO** | Pattern guidance, not invariant. |
| §22 Dispatch Patterns | **NO** | Style. Registry vs if/elif doesn't break the system. |
| §23 Function Signatures | **NO** | Convention. Good practice, not load-bearing. |
| §24 Naming Vocabulary | **NO** | Convention. Enforced by review, not invariants. |
| §25 Guard Clauses | **NO** | Style preference. |
| §26 Collection Building | **NO** | Pattern guidance. |
| §27 Serialization Completeness | **YES — DS-type** | Dropped fields cause silent data loss. HARD invariant. |
| §28 Nullable Numeric Parsing | **YES — DS-type** | The `or` trap silently replaces valid zeros. HARD invariant. |
| §29 Type System Conventions | **NO** | Design guidance. |
| §30 Dataclass Field Ordering | **NO** | Convention. |
| §31 Amendment Culture | **META** | This IS the amendment process. |

**Rule of thumb:** A guideline becomes an invariant when violating it produces *wrong output*, *data loss*, *security breach*, or *silent failure*. If violating it merely produces *ugly code* or *inconsistent style*, it's a convention enforced by hooks or review.

### Subsystem Invariant Files

Create one file per major subsystem. Each file lists invariants specific to that subsystem with IDs, types, descriptions, and code examples.

**Prompt to generate a subsystem invariant file:**
> Write the invariant file for the [subsystem] subsystem. It applies to [files/domains]. The key constraints are: [list]. For each constraint, classify as HARD, STRUCTURAL, or POLICY. Include right/wrong code examples for the most-violated rules. Reference relevant coding guidelines sections where applicable.

---

## Phase 4: Skills (Slash Commands)

Skills are specialized agent personas loaded on demand. Each `.claude/commands/<name>.md` file defines a persona with working style, do/don't rules, and output expectations.

### Core Skills (every project needs these)

| Skill | Purpose | When Used |
|-------|---------|-----------|
| **operator** / **engineer** | Primary implementation persona | Writing code, deploying, configuring |
| **debug** | Root-cause investigator | Diagnosing failures |
| **audit** | Read-only architectural analyzer | Finding drift, duplication, violations |
| **review** | Code/change reviewer | Reviewing PRs, diffs, tools |
| **close-out** | Post-implementation verification + commit | Wrapping up work |
| **check-invariants** | Subsystem-to-invariant loader | Before modifying subsystems |
| **glossary** | Term/abbreviation lookup | When terminology is unclear |

### Skill File Structure

```markdown
---
description: One-line description — used by the skill router to decide when to activate.
---

# Skill Name

[1-2 sentence identity statement. Who this persona is.]

## Working Style
[How this persona approaches problems. Investigation-first vs direct execution.]

## Do
[Specific positive instructions.]

## Don't
[Specific negative instructions.]

## Key Invariant Files
[Which invariant files this persona should load.]

## Output Expectations
[What the skill produces: reports, code, inventory files, etc.]
```

### Skills Informed by Coding Guidelines

The coding guidelines shape skill behavior in specific ways:

| Skill | Guidelines Impact |
|-------|------------------|
| **engineer/operator** | §1 Immutability, §3 Purity, §4 Error Handling, §9 Validation, §15 Dependency Direction — all become "Do" rules |
| **debug** | §4 Error Philosophy, §20 Error Semantics by Layer — debugger traces through these layers |
| **audit** | §10 Invariant Management, §27 Serialization Completeness — auditor checks for violations |
| **review** | §11 Code Style, §16-§30 conventions — reviewer checks these |
| **close-out** | §6 Testing, §12 Deterministic Output — verification phase runs tests |

**Prompt to generate a skill:**
> Write the skill file for the [name] persona. This persona [does what]. Working style: [investigation-first / direct execution / read-only analysis]. Key invariants to reference: [list]. Output format: [description]. The project uses these coding guidelines: [relevant sections].

---

## Phase 5: Hooks and Settings

### Post-Edit Linting Hook

The linting hook enforces code style automatically on every Edit/Write. It catches violations from coding guidelines §11 (Code Style) before they reach a commit.

**`.claude/hooks/lint-<language>.sh` pattern:**
```bash
#!/bin/bash
set -euo pipefail

# Extract file path from tool input JSON
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.filePath // empty')

# Skip non-applicable files
if [[ -z "$file_path" || "$file_path" != *.<ext> ]]; then
    exit 0
fi
if [[ ! -f "$file_path" ]]; then
    exit 0
fi

# Run linter — exit 0 (pass) or 2 (block)
errors=""
lint_output=$(<linter> check "$file_path" 2>&1) || errors+="$lint_output"$'\n'
format_output=$(<formatter> --check "$file_path" 2>&1) || errors+="$format_output"$'\n'

if [[ -n "$errors" ]]; then
    echo "$errors" >&2
    exit 2
fi
```

**Language-specific linters:**
| Language | Linter | Formatter |
|----------|--------|-----------|
| Python | `ruff check` | `ruff format --check` |
| JavaScript/TypeScript | `eslint` | `prettier --check` |
| Rust | `cargo clippy` | `rustfmt --check` |
| Go | `golangci-lint run` | `gofmt -l` |
| Shell | `shellcheck` | `shfmt -d` |

**`.claude/settings.json`:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/lint-<language>.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Why Hooks, Not Invariants

Code style (§11) is enforced by hooks because:
- Violations don't break the system — they make it ugly
- Automated enforcement is cheaper than manual review
- The linter is the authority, not the agent's judgment
- Hooks run on every edit, invariants are checked manually

---

## Phase 6: Coding Guidelines Integration

The coding guidelines document (`coding_guidelines.md`) serves a different purpose than CLAUDE.md or invariants. It's the *reasoning behind* the rules.

### Where to Place It

```
project/
├── docs/
│   ├── coding_guidelines.md    # full guidelines with rationale
│   └── invariants/
│       └── README.md           # extracted hard rules (no prose)
```

### The Relationship

```
coding_guidelines.md        →  CLAUDE.md (Code Style section, brief)
  (full rationale)          →  docs/invariants/*.md (extracted HARD/STRUCTURAL rules)
                            →  .claude/hooks/ (automated style enforcement)
                            →  .claude/commands/*.md (persona-specific Do/Don't rules)
```

The guidelines are the *source of truth*. The other files are *derived artifacts* — they extract specific rules into the format each consumer needs.

### What Goes Where

| Content | Destination | Format |
|---------|-------------|--------|
| "Use frozen dataclasses" | `docs/invariants/data_structures.md` | `DS-1: FROZEN_DATACLASSES — HARD` |
| "Use `replace()` to modify" | `docs/invariants/data_structures.md` | `DS-2: USE_REPLACE — HARD` |
| "Test at IR level" | `CLAUDE.md` → Code Style section | Brief bullet point |
| "No dead code" | `.claude/hooks/lint-python.sh` | Automated by ruff's F811/F401 rules |
| "Use consistent naming verbs" | `.claude/commands/review.md` | Reviewer checks during `/review` |
| "Error messages must include four parts" | `docs/invariants/README.md` | Error Philosophy section |
| "Guard clauses at entry" | Not enforced anywhere | Style preference, not load-bearing |

---

## Phase 7: Starter Code

Write functional code that demonstrates the project's patterns. The starter code serves three purposes:
1. The project is immediately usable (not just documentation)
2. The patterns are concrete (not just described)
3. The coding guidelines are *embodied* (the code follows them)

### What to Include

- **Shared library** — Common patterns extracted into helpers (logging, config loading, SSH connections, etc.). Demonstrates §15 Dependency Direction and §22 Dispatch Patterns.
- **3-5 functional tools/modules** — Real implementations that follow the coding guidelines. Each tool demonstrates: §4 Error Handling, §9 Validation at boundaries, §23 Function Signatures (argparse + params objects).
- **Configuration templates** — `.env.example`, role definitions, inventory templates. Demonstrates §8 Defaults and Configuration.

### Coding Guidelines Embodied in Starter Code

| Guideline | How It Appears in Starter Code |
|-----------|-------------------------------|
| §1 Immutability | Data classes are frozen where used |
| §3 Function Purity | Tools read env but don't modify shared state |
| §4 Error Handling | Every tool has clear error messages with context |
| §9 Validate at Boundaries | Input validation happens in `main()`, not deep in helpers |
| §11 No Dead Code | No commented-out code, no unused imports |
| §15 Dependency Direction | `tools/lib/` imported by `tools/`, never the reverse |
| §18 Logging | Session log module, not print statements |
| §23 Signatures | All tools use argparse, keyword-only flags for options |
| §25 Guard Clauses | Early returns for missing env, failed connectivity |
| §28 Nullable Parsing | Explicit `None` checks, never `or` for numeric fields |

**Prompt to generate starter code:**
> Write the [tool/module] for the project. It [does what]. Requirements: secrets from `.env` only (§8), error messages include host + action + next steps (§4), remote commands logged via session_log (§18), supports `--dry-run` for destructive ops, uses argparse CLI (§23). Follow the coding guidelines for immutability (§1), guard clauses (§25), and dependency direction (§15).

---

## Phase 8: Git Initialization

```bash
cd <project>
git init
git branch -m main
git add -A
git commit -m "Bootstrap project with AI infrastructure

- CLAUDE.md: agent instructions, capabilities, constraints
- .claude/commands/: 7 skills (operator, debug, audit, review, close-out, check-invariants, glossary)
- .claude/hooks/: post-edit linting hook
- docs/invariants/: global axioms + 5 subsystem invariant files
- Starter code: functional tools demonstrating project patterns
- coding_guidelines.md: full rationale document

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## File Manifest

Complete list of files created during bootstrap, with purpose:

### AI Infrastructure (project-agnostic pattern)

| File | Purpose | Lines |
|------|---------|-------|
| `CLAUDE.md` | Master agent instructions — identity, capabilities, constraints | 80-150 |
| `.claude/settings.json` | Hook configuration — runs linter on Edit/Write | 15 |
| `.claude/hooks/lint-<lang>.sh` | Post-edit linting — enforces code style automatically | 30 |
| `.claude/commands/operator.md` | Primary implementation persona | 50-80 |
| `.claude/commands/debug.md` | Root-cause investigation persona | 40-60 |
| `.claude/commands/audit.md` | Read-only architectural analysis | 60-170 |
| `.claude/commands/review.md` | Code/change review | 40-60 |
| `.claude/commands/close-out.md` | Post-implementation verification + commit | 60-110 |
| `.claude/commands/check-invariants.md` | Invariant loader before subsystem changes | 30-40 |
| `.claude/commands/glossary.md` | Terminology reference | 30-60 |
| `docs/invariants/README.md` | Global axioms, regression traps, subsystem index | 80-140 |
| `docs/invariants/<subsystem>.md` | Per-subsystem invariant files (3-8 files) | 30-60 each |
| `docs/coding_guidelines.md` | Full coding rationale (source of truth for rules) | 200-1200 |
| `.gitignore` | Standard ignores for language + secrets + logs | 20-30 |
| `README.md` | Human-facing project overview | 30-60 |

### Project-Specific (varies by domain)

| Category | Examples |
|----------|---------|
| Configuration templates | `.env.example`, role definitions, inventory templates |
| Shared library | Logging, config loading, connection helpers |
| Functional tools/modules | 3-5 working implementations |
| Dependencies | `requirements.txt`, `package.json`, `Cargo.toml` |

---

## Invariant Design Checklist

When creating invariants for a new project, walk through these questions:

1. **What can this system destroy?** → SEC-type HARD invariants
2. **What external state does it modify?** → OPS-type invariants (logging, dry-run, verification)
3. **What data flows through a pipeline?** → PL-type invariants (layer separation, determinism)
4. **What secrets does it handle?** → SEC-type HARD invariants (no committed secrets, env-only config)
5. **What data structures are shared?** → DS-type invariants (immutability, serialization completeness)
6. **What units/coordinates does it use?** → CS-type HARD invariants (single unit system)
7. **What is the testing strategy?** → TST-type STRUCTURAL invariants (test at right level)
8. **What are the regression traps?** → LLM-specific: what "improvements" would an AI make that would break things?

### LLM-Specific Regression Traps

Every project should document these. LLMs have predictable failure modes:

| Trap | Why LLMs Do It | Invariant Response |
|------|----------------|-------------------|
| Add class hierarchies | LLMs love type systems and inheritance | DS: flat type + data dict if IR is extensible |
| Shortcut pipeline layers | "Simplification" | PL: IR layer required, no pass-through |
| Add comments to everything | Default helpfulness | Style: no comments (enforced by hook or review) |
| Over-engineer error handling | Defensive programming instinct | Follow §20 error semantics by layer |
| Mutate inputs for "efficiency" | Optimization instinct | DS: frozen dataclasses, pure functions |
| Create new files instead of editing | Fresh-start bias | CLAUDE.md Don't: "Create new files when editing existing ones works" |
| Thread computed data through semantic layers | Convenience | PL: no pass-through geometry/data |
| Add backward compatibility shims | Safety instinct | Style: dead code is a defect, delete it |

---

## Master Prompt

To bootstrap a new project, first create a project prompt using the template above. Then use this master prompt with the project prompt attached:

```
Bootstrap a Claude Code project using the attached project prompt.

Reference documents (attached or in context):
- Project prompt: [attached]
- coding_guidelines.md: [attached or path]
- This bootstrap guide: [attached or path]

Generate the following, in order:

1. **Directory structure**
   - Standard: `.claude/commands/`, `.claude/hooks/`, `docs/invariants/`
   - Project-specific directories from the prompt

2. **CLAUDE.md**
   - Agent role and persona from the prompt
   - Core workflow as Mental Model
   - Capabilities table (empty or with starter code entries)
   - Don't section derived from constraints and LLM regression traps
   - Domain-specific principle section

3. **Invariants**
   - `docs/invariants/README.md` with global axioms from constraints
   - Subsystem invariant files as specified in the prompt
   - Architectural decisions determine which conditional guidelines become invariants

4. **Skills** (7 files in `.claude/commands/`)
   - operator/engineer, debug, audit, review, close-out, check-invariants, glossary
   - Each skill references relevant invariant files from the subsystem list

5. **Hooks**
   - Post-edit linting hook for the specified language
   - `.claude/settings.json` configuration

6. **Starter code**
   - Shared library modules as specified
   - Initial tools/commands as specified
   - All code follows coding_guidelines.md

7. **Configuration**
   - `.env.example` with variables from the prompt
   - Config templates as specified
   - `.gitignore` for language + secrets + logs

8. **Documentation**
   - `README.md` — human-facing project overview
   - Copy `coding_guidelines.md` into `docs/`

9. **Git initialization**
   - Initialize repo, commit with descriptive message

Follow the coding guidelines for all generated code.
```

---

## Maintenance

After bootstrap, the infrastructure evolves through use:

- **Memory files** accumulate in `.claude/projects/<path>/memory/` as the agent learns user preferences and project context. These are auto-managed, not bootstrapped.
- **Invariants** get amended when features require it — always in the same commit as the code change.
- **Skills** get refined as working style solidifies — new Do/Don't rules based on real mistakes.
- **CLAUDE.md capabilities table** grows as features are implemented.
- **Coding guidelines** stay as the stable reference — they change slowly, through explicit amendment.

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [coding_guidelines.md](coding_guidelines.md) | Full Python coding standards with rationale |
| [enforcement_matrix.md](enforcement_matrix.md) | Maps each guideline to its enforcement mechanism |
