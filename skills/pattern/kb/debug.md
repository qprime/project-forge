---
layer: pattern
pattern: kb
skill: debug
---

# KB pattern — debug contribution

Fills placeholders in `skills/global/debug.md` for projects declaring the KB pattern.

---

## insert: do-bullets

- Bisect by stage — is the wrong answer coming from retrieval (wrong entries), assembly (wrong frame), or synthesis (ungrounded output)?
- Dump retrieval results for the failing query before looking at synthesis — most "bad answers" are actually bad retrieval
- Check grounding — if synthesis cites something assembly didn't surface, the bug is in synthesis, not retrieval
