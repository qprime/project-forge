---
layer: global
---

# Global Invariants

Invariants that apply to every project regardless of declared pattern.

Each invariant has:
- **Rule** — the constraint
- **Failure mode** — what breaks when it's violated
- **Type** — `code-side` (checkable by tests, types, static analysis), `llm-side` (enforced by pipeline structure: gates, guardrails, post-oracles), or `bridge` (LLM output must pass a deterministic check before proceeding)

---

## GL-1 — Pipelines do not re-enter or escape scope

Re-entry into earlier phases, or scope escapes (phase A reading or writing data phase B owns), are topology changes, not local edits. Phase order and per-phase scope must be documented; changes to either require explicit architectural decision.

**Failure mode:** phases bleed into each other until no one can reason about where work actually happens.
**Type:** code-side

---

## GL-2 — Non-deterministic output carries provenance

Where output from a non-deterministic source (LLM, model, human, external service) enters deterministic code, it carries evidence sufficient to reproduce or audit it. Minimum: what produced it, against what input, when, at what version.

**Failure mode:** the system cannot reproduce its own outputs.
**Type:** bridge

---

## GL-3 — Data is immutable by default

Data structures shared across modules are immutable. Mutations produce new values (e.g., `replace()` on frozen dataclasses). Mutation is allowed only at documented boundaries, with the mutation explicitly called out.

**Failure mode:** shared mutable state turns innocuous changes into action-at-a-distance bugs.
**Type:** code-side

---

## GL-4 — Same input produces same output

Deterministic components produce the same output for the same input. Randomness is explicitly seeded. Time is injected, not read. External I/O in the deterministic path is a violation.

**Failure mode:** debugging becomes guessing; tests become flaky; reproductions become impossible.
**Type:** code-side

---

## GL-5 — Failures carry context

Errors are not silently dropped. Every error states what failed, what was expected, and what was received.

**Failure mode:** silent failures accumulate; the system appears healthy while producing wrong output.
**Type:** code-side

---

## GL-6 — Writes to durable state are idempotent

Operations that write to persisted state produce the same result whether run once or many times. Retried writes do not corrupt or duplicate state.

**Failure mode:** crashes mid-operation leave the system in a state that breaks on the next run.
**Type:** code-side

---

## Not yet resolved

**Candidate fifth shape — governance at participation boundaries.** Rules that constrain *who or what* is allowed to act on which data: "X reads but does not write," "Y produces proposals, not actions." These don't fit the four shapes cleanly — not single source (who acts isn't a concern to be unified), not order (not about sequencing), not persistence (not about state class), not provenance (not about evidence).

If adopted, the rule would land here as GL-6. Until then, projects expressing this concern do so at their own layer.
