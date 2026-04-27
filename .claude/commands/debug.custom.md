---
layer: project
project: project-forge
skill: debug
---

# project-forge — debug contribution

## insert: domain-debugging

## Forge-Specific Debugging

When debugging forge issues, check:
- **Registry resolution** — do all paths and refs in `registry/projects.yaml` resolve? `/status` is the canonical detector (FG-6).
- **Baseline version comparisons** — drift detection compares declared `resolution.baseline_version` in each project's manifest against the current baseline. Stale or missing values surface as drift.
- **Survey-derived profiles** — profiles in `profiles/` are derived from live state (FG-3). If a profile looks wrong, the bug is in `/survey` or in the source it read, not in the profile itself.
- **Resolver composition** — `forge/resolver.py` walks template → pattern contribution → project contribution. Unfilled required slots, unknown placeholders, and invariant ID collisions all raise `ResolverError` with the offending name; read the message before guessing.
- **Prompt log parsing** — `/monitor` reads the UserPromptSubmit log; if patterns aren't surfacing, check the log path and format before suspecting the analysis.

## insert: invariant-files-extras

- `docs/invariants/global.md` — forge's own invariants (FG-1 through FG-7); registry, baseline, survey, and monitor boundaries
