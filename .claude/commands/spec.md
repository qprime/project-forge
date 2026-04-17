---
description: Draft a GitHub issue implementation specification. Use when planning a new feature, refactor, or bug fix that needs a detailed spec before implementation.
---

# /spec — Implementation Specification

Draft a GitHub issue implementation specification for: $ARGUMENTS

## Process

1. **Research first.** Before drafting, read: (a) every file named in the feature request, (b) the implementation files of any named subsystem, (c) `docs/invariants/global.md` plus any subsystem invariant file touched by the change, and (d) existing tests covering the affected code paths. List what you read in a short "Context loaded" block before drafting the spec. Understand what exists before proposing changes.

2. **Draft the spec** as a GitHub issue body using the section template below. Every section is required unless explicitly marked optional. Omit a section only if it genuinely does not apply.

3. **Present the draft** to the user for review before creating the issue.

---

## Title

Start with an action verb. Describe what the change *does*, not what's missing or broken.

- **Good:** "Add drift detection for baseline version comparisons"
- **Bad:** "Projects don't know when their baseline is stale"

## Section Template

### Summary
1-3 sentences. What is being added, changed, or fixed. Actionable and specific.

### Motivation
Why this matters. Concrete pain points — user-facing or developer-facing. Not hypothetical benefits.

### Existing Architecture
What exists today that this change touches. Reference specific files and line numbers. Include function signatures, data flow, and relevant patterns. This section grounds the implementation in reality — do not skip it.

### Design
The technical approach:
- **Data flow**: ASCII diagram showing how data moves through the system
- **Code signatures**: Exact dataclass fields, function signatures with type annotations
- **Invariant exceptions**: If any invariant is bent, document the exception and why it's contained

### Constraint Interactions
How this feature interacts with existing features. For each relevant interaction:
- Is it compatible, mutually exclusive, or conditionally compatible?
- What validation enforces the constraint?

*Optional — omit only if the change is truly isolated (rare).*

### Implementation
Phased or numbered steps. For each step:
- Which file(s) change
- What specifically changes (field additions, new functions, modified logic)

Use a per-file change table when touching 3+ files:

| File | Change |
|------|--------|
| `path/to/file.py` | Description of change |

### Invariants
Which invariant files apply to this change. For each:
- Invariant ID and name
- Whether this change complies or requires a documented exception

### Edge Cases
For each parameter that can be None/omitted independently, document what happens when only some are provided. Specify the resolution rule explicitly.

### Testing Strategy
Named test cases with expected behavior:

```
TestClassName:
    test_case_name — description of what it verifies
```

### What NOT to do
Explicit anti-patterns and scope boundaries. Things that might seem like natural extensions but should not be done in this issue.

### Files to Modify
Master table of every file that will be created or modified.

### Dependencies *(optional)*
Related issues, prerequisites, or things this supersedes.

---

## Quality Checks

Before presenting the draft, verify:

- [ ] Every file referenced actually exists (or is explicitly marked as new)
- [ ] Line numbers are current (not stale)
- [ ] Function signatures match the actual codebase
- [ ] Invariant IDs are real (check `docs/invariants/global.md`)
- [ ] No section is vague hand-waving
- [ ] The "What NOT to do" section has at least one entry
- [ ] Test cases have names, not just descriptions
