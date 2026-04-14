# project-forge

Cross-project intelligence system, bootstrap orchestrator, and change monitoring service. Owns the capability baseline that all projects bootstrap from, maintains a registry of projects and their configurations, and provides cross-project analysis — pattern extraction, drift detection, change monitoring, and knowledge publishing. Reads other projects to learn from them; writes to them only during bootstrap and rebase operations. Watches how projects change over time and generalizes patterns into baseline candidates.

## Tags

`[python]`, `[github-issues]`, `[infrastructure]`, `[bootstrap-source]`

## Mental Model

Forge is the meta-project. It doesn't build software — it understands how all your projects are built, configured, and maintained. The registry is the single source of truth for what exists. The baseline is the single source of truth for how projects should be configured. Everything else — surveys, profiles, drift reports, monitor proposals — is derived from reading live state.

Forge has two observation modes: **spatial** (surveys, comparing projects at a point in time) and **temporal** (monitoring how projects change over time, what you ask for repeatedly, where corrections recur). Both feed into the same output: proposals for baseline improvement.

Forge self-bootstraps: its own configuration is expressed in its own baseline. If the baseline can't describe forge, the baseline is incomplete.

## Capabilities

| Capability | Source | Notes |
|---|---|---|
| Investigate-First | Always-on | Search before implementing |
| Trace-Debug | Always-on | Root-cause, not symptoms |
| Minimal-Diff | Always-on | Exactly what's asked |
| Close-Out-Rigor | Always-on | Full verification before commit |
| No-Comments | Always-on | Code self-documents |
| No-Plan-Mode | Always-on | Just do the work |
| Immutability-Discipline | `[python]` | Frozen dataclasses, pure functions |
| Python-Conventions | `[python]` | Type hints, pytest, no shell=True |
| GitHub-Integration | `[github-issues]` | Issues track work, reference in commits |
| Infrastructure-Safety | `[infrastructure]` | Dry-run before destructive ops |
| Tool-Codification | `[infrastructure]` | Repeatable operations become CLI tools |
| Baseline-Dogfooding | `[bootstrap-source]` | Config must be expressible in own baseline |

## Key Directories

| Path | Purpose |
|---|---|
| `registry/` | Project manifest — `projects.yaml` is the single source of truth (FG-1) |
| `baseline/` | Canonical capability baseline, coding guidelines, enforcement matrix (FG-2) |
| `docs/invariants/` | Forge invariants (FG-1 through FG-6) |
| `.claude/commands/` | Skills — standard + forge-specific |
| `profiles/` | Survey-derived project profiles (FG-3, created by `/survey`) |

## Invariants

See `docs/invariants/global.md` for full definitions.

| ID | Name | Classification | Summary |
|---|---|---|---|
| FG-1 | Registry-is-Truth | HARD | `registry/projects.yaml` is the single source of truth |
| FG-2 | Baseline-Canonical | HARD | `baseline/` files are canonical — consumers never modify |
| FG-3 | Survey-Derived | STRUCTURAL | Profiles from `/survey` are derived, never manually edited |
| FG-4 | Read-Before-Write | HARD | Reads freely; writes only during `/bootstrap` or `/rebase` with approval |
| FG-5 | Self-Bootstrap | STRUCTURAL | Bootstrappable from cold start using only own baseline |
| FG-6 | No-Stale-Pointers | POLICY | All registry paths/refs must resolve; `/status` detects broken ones |
| FG-7 | Monitor-Proposes | HARD | `/monitor` proposes changes, never auto-applies — human decides what gets codified |

## Don't

- Don't run other projects (build, test, deploy) — forge reads and understands, it doesn't operate
- Don't duplicate project-specific skills — forge owns cross-project and bootstrap skills
- Don't store full copies of project state — store profiles, pointers, and summaries; read live when detail is needed
- Don't auto-rebase projects without human approval — drift detection and proposals, not auto-modification
- Don't manually edit survey-derived profiles — re-run `/survey` instead
- Don't duplicate registry data in other files

## Domain Framing

**For `/architect`:** Meta-project — registry integrity, baseline consistency, cross-project analysis correctness, bootstrap idempotency, survey derivation accuracy

**For `/engineer`:** Bootstrap orchestrator — registry management, baseline maintenance, survey/profile generation, cross-project pattern extraction, change monitoring infrastructure

**For `/monitor`:** Change monitoring service — prompt log analysis, cross-project git activity, pattern extraction, proposal generation. Temporal complement to `/survey` (spatial)

**For `/debug`:** Check registry resolution, baseline version comparisons, profile freshness, cross-reference integrity, prompt log parsing
