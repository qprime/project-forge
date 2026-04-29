---
layer: pattern
pattern: declare-and-satisfy
command: review
---

# Declare-and-satisfy pattern — review contribution

Fills placeholders in `commands/global/review.md` for projects declaring the Declare-and-satisfy pattern.

---

## insert: architectural-review-extras

- **Declaration persistence** — flag any intent that drives execution without being written to a durable artifact first
- **Refinement bounds** — flag regeneration loops without an explicit, enforced budget
- **Dispatch explicitness** — flag satisfier selection by name-branching; dispatch through a registry instead
- **Verifier-declaration alignment** — verification must check against the declaration, not just against the execution trace
