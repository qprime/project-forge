---
layer: global
description: Draft a GitHub issue implementation specification. Use when planning a new feature, refactor, or bug fix that needs a detailed spec before implementation.
---

<!--
Template for the spec skill. Global layer.

Placeholder syntax:
  {{SLOT_NAME}}            — single value. Exactly one layer fills it.
  <!-- insert: NAME -->    — list or block. Zero or more layers contribute; pattern first, project appended.

Only this file defines placeholders. Pattern and project layers fill them.
-->

# /spec — Implementation Specification

Draft a {{ISSUE_TRACKER}} implementation specification for: $ARGUMENTS

## Process

1. **Research first.** Before drafting, read: (a) every file named in the feature request, (b) the implementation files of any named subsystem, (c) all invariant files that govern the affected code paths, and (d) existing tests covering those paths. List what you read in a short "Context loaded" block before drafting. Understand what exists before proposing changes.

2. **Draft the spec** using the section template below. Every section is required unless explicitly marked optional. Omit a section only if it genuinely does not apply.

3. **Check for a smaller change.** Before finalizing, ask: could a narrower scope — fewer files, fewer moving parts, less ceremony — achieve the same goal? If yes, redraft around that. Spec size should match change size. This is about scope, not about removing structure that serves invariants, type safety, or tests.

4. **Self-review the draft.** Read it back as if you hadn't written it. Flag anything you're unsure about, anything resting on an unverified assumption, and anything that sounds confident but isn't grounded in what you actually read. Surface those to the user with the draft.

5. **Present the draft** to the user for review before creating the issue.

<!-- insert: process-extras -->

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
- **Data flow**: How data moves through the system. Use an ASCII diagram only if the shape isn't obvious from prose.
- **Code signatures**: Exact dataclass fields, function signatures with type annotations
- **Invariant impact**: Which invariants does this touch? Note here if any are bent; full compliance statement goes in the Invariants section below.
<!-- insert: design-extras -->

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
| `path/to/file` | Description of change |

### Invariants
Which invariant files apply to this change. For each:
- Invariant ID and name
- Whether this change complies or requires a documented exception

### Edge Cases
Scenarios worth calling out and the expected behavior. Cover what's actually at risk for this change — missing/None inputs where relevant, adjacent work having or not having landed, analysis surfacing something unexpected, partial or conflicting state.

### Testing Strategy
Named test cases with expected behavior:

```
TestClassName:
    test_case_name — description of what it verifies
```

Include at least one test whose failure would catch a plausible wrong implementation — not just one that passes when the code is correct.

<!-- insert: testing-strategy-extras -->

### What NOT to do
Anti-patterns and scope boundaries that aren't obvious from the positive rules above. Each bullet must earn its place by meeting at least one of:
- Prevents a failure mode that actually happened in a prior issue/review
- Non-obvious from the Design / Implementation sections (a reader would not infer it)
- Draws a scope boundary against adjacent work (other open issues, sibling subsystems)

If a bullet just restates a rule already given positively, cut it. Omit the whole section if nothing meets the bar.

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
- [ ] Invariant IDs are real
- [ ] No section is vague hand-waving
- [ ] Every "What NOT to do" bullet meets the bar; no bullet restates a positive rule from Design/Implementation
- [ ] Test cases have names, not just descriptions
<!-- insert: quality-checks-extras -->
