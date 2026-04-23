# Intent-Driven Machine Interaction — Exploration Notes

**Date:** 2026-04-13
**Status:** Early exploration, no active project yet

---

## The thesis

Most software layers between a human and a machine exist because humans couldn't express intent precisely enough for the machine to act on directly. Operating systems, UI frameworks, compilers, CAM software — these are translation layers. LLMs can bridge the intent-to-action gap well enough that many translation layers become optional overhead. Infrastructure layers (scheduling, memory, I/O, safety) remain necessary. Translation layers become ephemeral — generated on demand and thrown away.

The LLM becomes the universal translation layer. Nothing persists except the intent and the infrastructure.

---

## Two parallel exploration tracks

### Track 1: Intent-driven computer interface

Express intent (voice or text), get a rendered result. No persistent app, no dashboard, no framework. One-shot renders that answer a question and go away.

**Example:** "Show me the last 10 logs I scanned, sorted by recovery delta, with the worst ones highlighted" → rendered table/SVG/HTML → done. Next intent starts fresh.

**Orchestration pattern:**
1. Intent in (voice or text)
2. LLM interprets intent, decides what data to fetch and how to present it
3. Generates the artifact (HTML, SVG, table, whatever fits)
4. Renders it
5. Done. No state.

**Containment:** Same CLAUDE.md / invariant pattern used in software projects — define what the system can access, what it can render, what it can't do.

**Cost of failure:** Zero. A bad render just looks wrong. Fast iteration.

### Track 2: Intent-driven CNC

Express intent ("cut a circle, 2 inches diameter, 0.25 deep in this material"), get a verified toolpath, execute. Extension of existing G-code work.

**Key difference from Track 1:** Verification layer is load-bearing. Getting it wrong scraps material or damages the machine. The human-in-the-loop checkpoint between generation and execution is not optional.

**Cost of failure:** Real. Slower iteration, higher stakes.

---

## Exploration plan

### Phase 1 — One concrete task in each domain

- Interface: "show me [something from mill_ui or penumbra data]" → rendered output
- CNC: "cut [a specific simple part]" → verified toolpath → execution

Don't generalize. Don't build infrastructure. Just make one thing work end to end in each domain.

### Phase 2 — Notice what's common

- How was intent expressed?
- What did the orchestration layer need to know to translate it?
- Where did it need guardrails?
- What was ephemeral and what persisted?

### Phase 3 — Extract the shared pattern

Build something reusable only after two concrete working examples reveal what the abstraction actually looks like.

---

## Where the pattern breaks

Generation can be ephemeral. Verification can't. The translation layer is replaceable by LLM generation wherever the cost of a wrong answer is low or where a verification step catches errors before they matter. The pattern breaks where:

- Getting it wrong is expensive or dangerous (CNC, medical, safety systems)
- Latency of generation exceeds the available time budget
- The intent is too ambiguous for the LLM to disambiguate without extensive back-and-forth

In all three cases, the fix is the same: add a verification checkpoint, not a persistent application.

---

## Related work and context

- Penumbra POC routing architecture — same pattern of "pick the right tool, use confidence to decide"
- SuperCoder (assembly optimization) — same loop of generate → verify → measure → iterate
- Existing CNC/G-code direct-intent experiments
- mill_ui as a candidate data source for interface rendering experiments
