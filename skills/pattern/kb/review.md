---
layer: pattern
pattern: kb
skill: review
---

# KB pattern — review contribution

Fills placeholders in `skills/global/review.md` for projects declaring the KB pattern.

---

## insert: architectural-review-extras

- **Retrieval discipline** — flag any drift toward similarity-based retrieval; dispatch against structured coordinates is the contract
- **Authorship boundary** — flag any code path where LLM output can land in the corpus. This is invariant-level.
- **Grounding** — flag synthesis that cites or references content assembly did not surface
- **Stage boundaries** — flag any collapse of retrieval, assembly, and synthesis into a single step
