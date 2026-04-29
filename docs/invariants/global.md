# Forge Invariants

Project-forge invariants. These are hard rules that govern how forge operates.

Numbering preserved across deletions; gaps are honest signals that retired invariants existed.

---

## FG-1: Registry-is-Truth

**Classification:** HARD

`registry/projects.yaml` is the single source of truth for project metadata. No other file duplicates this data.

---

## FG-2: Baseline-Canonical

**Classification:** HARD

The baseline trees (`commands/global/`, `commands/pattern/`, `invariants/`, `conventions/`) are the canonical source. Projects receive composed copies via `forge create` and `forge update` — they never modify the baseline content directly. Project-specific content lives in the project's `.forge/manifest.yaml`.

---

## FG-4: Read-Before-Write

**Classification:** HARD

Forge reads other projects freely. It writes to other projects only during explicit `forge create` or `forge update` operations, and only with user approval.
