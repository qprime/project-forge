---
layer: project
command: manifest-skeleton
kind: authoring-prompt
---

# manifest-skeleton — top-level authoring prompt

Run during `forge create` (and re-run during `forge update` only when the project's prose description has changed) to produce everything in `<project>/.forge/manifest.yaml` *above* the per-command `project:` block. The six per-command authoring prompts (`architect.prompt.md`, etc.) run after this one and consume the pattern this prompt selects.

This prompt does the load-bearing collapse: prose description in, crisp manifest skeleton out. If no known pattern fits the description, refuse with a proposal — do not invent a pattern or force a wrong fit.

---

## Inputs

- The target project's prose description. For new projects, the user-supplied description. For legacy projects, the existing `CLAUDE.md` and `README.md` reformatted by the legacy-migration prompt.
- The known pattern set: `compiler`, `kb`, `declare-and-satisfy`, `bracketed-probabilistic`. See `project_patterns_draft.md` for what each pattern is.
- The known command set: `architect`, `debug`, `engineer`, `review`, `spec`, `close-out`. See `commands/global/<name>.md` for what each command does.

## Output

A YAML fragment that is the entire manifest *except* the per-command `project:` block, `project_invariants`, and `project_conventions` (those are authored by other prompts). The output validates against `forge/manifest.schema.json` once the per-command prompts have run and merged their fragments in.

Rule of thumb: every field is something a downstream resolver or human reviewer actually consumes. If you can't fill a field with a meaningful, project-specific value, omit it (when optional) or refuse the whole skeleton (when required).

---

## Step 1 — Pattern selection

Read the project's description. Identify which of the four known patterns fits.

- **compiler** — declarative input → deterministic transformation pipeline → formal output (text or binary). Pre-gate verification, mutable-current state.
- **kb** — accumulating corpus organized into storage / retrieval / assembly / synthesis stages. Not all stages are necessarily built; some may be human-performed.
- **declare-and-satisfy** — specification + LLM refinement loop, with post-oracle verification deciding accept / regenerate.
- **bracketed-probabilistic** — generation-then-filter shape; output is curated from a probabilistic source, with human or oracle review as the bracket.

If exactly one pattern fits, declare it as `patterns.primary`. If a sub-tree of the project follows a different pattern (e.g., a doc-generation pipeline embedded in a KB), declare it as `patterns.secondary[]` with a `scope:` naming the sub-tree.

If **no** pattern fits, do not produce a skeleton. Emit a proposal block instead:

```yaml
refuse: pattern-mismatch
proposed_pattern:
  name: <suggested name>
  shape: <one-paragraph description of what the new pattern would be>
  why_existing_dont_fit: <one paragraph naming which pattern came closest and what's load-bearingly different>
```

Stop after emitting the refusal. A human decides whether to author the new pattern, refine the description, or pick the closest existing pattern manually.

## Step 2 — Active commands

From the known command set, pick the subset that applies to this project. Read each command's global template (`commands/global/<name>.md`) if uncertain whether it fits. The picked set goes into `commands: [...]`.

Heuristics:

- `architect` and `review` apply to almost any project. Default include unless the project genuinely has no design or review surface.
- `engineer` applies when the project has code or otherwise produces machine-consumed artifacts. Omit for `[no-codebase]` projects (a study workspace, a pure notes corpus).
- `debug` follows `engineer` — if there's nothing to debug because there's nothing executable, omit.
- `spec` applies when the project has a specification step that hands off to implementation. Omit for projects where work is its own implementation (a notes project where writing the note *is* the work).
- `close-out` applies when the project has a workflow that ends with verification + posting (PRs, issue comments). Omit for solitary-author workflows.

Pick conservatively. The downstream per-command prompts only run for commands in this list — omitting a command that turns out to apply is cheap to fix; including a wrong-fit command produces noise that takes editing to clean up.

## Step 3 — Project context

Distill the description into:

- `project_context.description` — one sentence, ≤280 characters, naming what the project *is*. Not "this is a project that..." — start with the noun (e.g., `"Personal study workspace for applied math and ML, organized for diagnostic-intuition recognition rather than technique mastery."`).
- `project_context.vocabulary` (optional) — the project's load-bearing nouns. The terms that appear repeatedly in its CLAUDE.md and that command authoring prompts will want to reflect back.
- `project_context.load_bearing_subsystems` (optional) — paths or names of the subsystems the project's invariants and conventions key off.
- `project_context.invariant_sources` (optional) — paths to existing hand-authored invariants (`docs/invariants/<id>.md`) that the project layer should read or reformulate.

Omit any optional field with no real content. An empty array is worse than an absent key.

## Step 4 — Domains and language

- `domains` (optional) — cross-cutting concerns the project carries that aren't pattern-shaped. Examples: `CAD/CAM`, `manufacturing`, `infrastructure`, `study`, `applied math`. Pulled from the description's subject matter, not from the pattern.
- `language` (optional) — the primary language for conventions resolution. Use the conventions filename stem (`python`, `markdown`, `typescript`). Omit if the project has no code-or-text conventions surface that varies by language.
- `python_version` and `toolchain` (optional) — only when language is `python` and the project has actual tooling. Don't default to `pytest`/`ruff`/`pyright` if the project doesn't use them.

## Step 5 — Resolution

The path policy is fixed:

- `commands_dir: .claude/commands/`
- `invariants_dir: docs/invariants/`
- `conventions_dir: docs/`

Use these defaults unless the project's existing on-disk layout already places these elsewhere and migration is out of scope. If you change a default, name the reason in a comment above the field.

`baseline_version` is the current baseline date (YYYY-MM-DD format). Use today's date when authoring; `forge update` will refresh it.

## Step 6 — Axes

Do not fill `axes:`. The schema accepts it as optional documentation; nothing in forge currently reads it. A separate, manual step populates axes for projects where the position vector is interesting (see `project_patterns_draft.md`).

---

## Output shape

```yaml
schema_version: 1

patterns:
  primary: <pattern name from known set>
  # secondary: optional, only when a sub-tree differs
  # secondary:
  #   - name: <pattern>
  #     scope: <subtree path or description>

domains: [<domain>, <domain>]   # omit if empty
language: <language>            # omit if not applicable

commands: [<command>, <command>, ...]

project_context:
  description: "<one sentence, ≤280 chars>"
  # optional:
  # vocabulary: [...]
  # load_bearing_subsystems: [...]
  # invariant_sources: [...]

resolution:
  baseline_version: "YYYY-MM-DD"
  commands_dir: .claude/commands/
  invariants_dir: docs/invariants/
  conventions_dir: docs/
```

Keys with no content are omitted entirely. The per-command `project:` block, `project_invariants`, and `project_conventions` are authored by other prompts and merged into the manifest separately.

If a pattern doesn't fit, emit the `refuse:` block from Step 1 instead and stop.
