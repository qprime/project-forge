---
layer: project
command: architect
kind: authoring-prompt
---

# architect — project-layer authoring prompt

Run during create (or update) to produce project-specific content for the `architect` skill. The output is a YAML fragment that fills named placeholders in `commands/global/architect.md` via the project manifest's `project` block.

---

## Inputs

- The target project's spec / guidance document (design doc, README, CLAUDE.md draft, or whatever it offered at create-time).
- The project's declared pattern(s).
- The global template at `commands/global/architect.md` — read it to see exact placeholders and surrounding prose.
- Any pattern contributions that apply (`commands/pattern/<pattern>/architect.md`) — read them so you don't duplicate.

## Output

A YAML fragment to merge under `project.architect:` in `<project>/.forge/manifest.yaml`. Include only keys with real content. Omit any placeholder you can't fill well — an empty placeholder is better than a generic one.

Rule of thumb: if a cousin project on the same pattern would want the same text, it belongs in the pattern contribution, not here.

---

## slot: PERSONA_DOMAIN

A short noun phrase naming the domain this architect is expert in, specific to this project.

- Good: `"intent-driven PLC simulation and IEC 61131-3 structured text generation"`
- Bad: `"software architecture"` (generic)

Test: would this phrase be wrong if pasted into a different project's template? If no, it's too generic.

## slot: PERSONA_UNDERSTANDING

A clause describing what architectural concerns this architect grasps that a generic architect wouldn't. Derive from the project's load-bearing architectural commitments — the things a newcomer would get wrong.

- Good: `"how LLM-authored implementation composes with post-oracle verification, and why disposable implementation changes what 'maintainable code' means"`
- Bad: `"software design and tradeoffs"` (generic)

## slot: PERSONA_MENTAL_MODEL

A short phrase naming the vocabulary the architect thinks in. Pull from the project's own terms — the nouns that appear repeatedly in its CLAUDE.md and invariants.

- Good: `"specs, refinement, traces, and post-oracles"`
- Bad: `"systems, components, and interfaces"` (generic)

## slot: HANDOFF_TARGET

The downstream spec-drafting skill. Default `/spec`. Change only if the project uses a different name.

## insert: context-discovery-extras

Additional numbered items to append to the context-discovery list beyond the four defaults. Include project-specific docs the architect should always know exist — glossaries, design docs, invariant files not at the default path.

Format as numbered continuation starting from 5:

```
5. `docs/refinement.md` — how the LLM refinement loop is supposed to behave
6. `docs/data_gates.md` — pre-gate contracts between stages
```

Omit if the four defaults cover the project.

## insert: investigate-anchors

Optional prose block naming project-specific subsystems the architect should mentally index. Use when the project has well-established subsystems worth naming.

Good:
```
Key subsystems: `relay/runtime/` (simulation engine), `relay/verify/` (trace assertions), `relay/generator/` (ST code synthesis from spec).
```

Omit if the project is small enough that naming paths adds noise. Don't duplicate pattern-contributed anchors — read the pattern contribution first.

---

## Output shape

A YAML fragment for `project.architect:` in `<project>/.forge/manifest.yaml`. Use plain scalars for one-line slot values and `|` block scalars for multi-line insert bodies (markdown content survives verbatim, including embedded H2 headers and fenced code blocks).

```yaml
architect:
  slots:
    PERSONA_DOMAIN: <noun phrase>
    PERSONA_UNDERSTANDING: <clause>
    PERSONA_MENTAL_MODEL: <phrase>
    HANDOFF_TARGET: <skill name, default /spec>
  inserts:
    context-discovery-extras: |
      <numbered lines>
    investigate-anchors: |
      <prose>
```

Keys with no content are omitted entirely. If a skill has no project-layer content at all, omit `architect:` from `project`.
