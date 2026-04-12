---
description: Run the full post-implementation close-out workflow — verification, summary, and commit. Only use when the user explicitly asks — e.g. "close it out", "wrap it up", "/close-out". Never auto-trigger after implementation.
---

# /close-out — Implementation Close-Out

Close out the implementation for: $ARGUMENTS

This skill runs the full verification, summary, and commit cycle after an implementation is complete. Follow every phase in order.

---

## Phase 1: Verification

Run all verification steps. Do not skip any.

**Context discipline:** Pipe large output to `tail` for summary. Re-run without tail on failure.

```bash
# 1. Full test suite (if tests exist)
python -m pytest tests/ -x -q 2>&1 | tail -5

# 2. Lint and type checks (if configured)
ruff check . 2>&1 | tail -3 && ruff format --check . 2>&1 | tail -3
```

**ALL tests must pass. Zero failures, zero errors, no exceptions.** Do not classify any failure as "pre-existing" — if it fails, it blocks the commit.

---

## Phase 2: Implementation Summary

Draft an implementation summary as a GitHub issue comment:

```
## Implementation Summary

<1-2 sentence description of what shipped.>

### Files Modified (<N>)

| File | Change |
|------|--------|
| `path/to/file.py` | Description of change |

### Files Created (<N>) *(if any)*

| File | Purpose |
|------|---------|
| `path/to/file.py` | Purpose |

### Design Notes
- Key architectural decisions or non-obvious choices

### Test Results
<N> passed, zero failures
```

Present to user before posting.

---

## Phase 3: Commit

1. Stage relevant files (specific, not `git add -A`)
2. Commit with:
   - Subject: imperative mood, `(closes #N)` if closing issue
   - Body: categorized bullet points
   - Trailer: `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`
3. Run `git status` to confirm clean state

Do NOT push unless explicitly asked.

---

## Phase 4: Final Summary

```
Committed as `<hash>` — all checks pass, <N> tests pass.

### What shipped
<2-3 sentence summary>

### Files
- <N> source files modified/created
```

---

## Posting to GitHub

If associated with a GitHub issue, post the Implementation Summary (Phase 2) as a comment using `gh issue comment <number> --body "..."`.
