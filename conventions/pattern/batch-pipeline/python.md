---
layer: pattern
pattern: batch-pipeline
language: python
status: provisional
---

# Batch-pipeline pattern — Python conventions

Conventions for projects with a multi-stage pipeline that processes a collection of items where partial output is part of the contract: per-item failures are tolerated, accumulated, and reported.

**Status:** name is provisional. Candidate alternatives: per-item-fault-tolerant, item-batch. Pin during pattern taxonomy review.

Examples in the registry: mill_ui (panel processing), penumbra-poc (per-log evaluation), image-forge (per-image generation).

---

## Handling errors per layer

| Layer | On Failure | Mechanism |
|---|---|---|
| Parser | Fail hard | Raise; malformed input is not recoverable |
| Resolver / Builder | Skip item | Catch expected exceptions; continue |
| Adapter | Warn + skip | Catch `ValueError` per item; collect warnings; continue |
| Core engine / Planner | Warn + skip | Structured accumulator; skip item; continue |
| Pipeline orchestrator | Collect + gate | Accumulate; halt on safety-critical failures |

Failures become less fatal as you move outward. The parser is strict; the orchestrator is lenient about items but strict about safety.

This table assumes per-item isolation is part of the pipeline's contract. For transactional, publishing, migration, or validation paths, abort the batch on any failure — see *Per-item isolation when partial output is part of the contract* in the global guidelines.

### Structured warning collection

Skipping an item emits both:

1. `logger.warning(...)` for diagnostics
2. A structured warning into the pipeline result

Warning messages always include: item identity, the specific problem, the action taken (`— skipped`).
