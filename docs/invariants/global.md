# Forge Invariants

Project-forge invariants. These are hard rules that govern how forge operates.

---

## FG-1: Registry-is-Truth

**Classification:** HARD

`registry/projects.yaml` is the single source of truth for project metadata. No other file duplicates this data.

---

## FG-2: Baseline-Canonical

**Classification:** HARD

Baseline files in forge (`baseline/`) are the canonical source. All other repos consume via bootstrap/rebase — they never modify baseline content.

---

## FG-3: Survey-Derived

**Classification:** STRUCTURAL

Project profiles produced by `/survey` are derived from reading live project state. They are never manually edited — re-survey to update.

---

## FG-4: Read-Before-Write

**Classification:** HARD

Forge reads other projects freely. It writes to other projects only during explicit `/bootstrap`, `/rebase`, or `/codex-sync` operations, and only with user approval.

---

## FG-6: No-Stale-Pointers

**Classification:** POLICY

Every project path and repo reference in the registry must resolve. `/status` detects and reports broken references.

---

## FG-7: Monitor-Proposes

**Classification:** HARD

`/monitor` analyzes prompt logs, git activity, and permission events to detect recurring patterns. It produces proposals — candidate skills, rules, capabilities, and invariants. It never auto-applies proposals. The human reviews and decides what gets codified into the baseline, CLAUDE.md, or settings.
