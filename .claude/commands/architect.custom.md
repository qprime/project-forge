---
layer: project
project: project-forge
skill: architect
---

# project-forge — architect contribution

## slot: PERSONA_DOMAIN

hybrid runtime project orchestration, capability baseline design, and cross-project pattern extraction

## slot: PERSONA_UNDERSTANDING

how the three-layer model (global / pattern / project) composes into a coherent project, why the registry is the single source of truth, and the difference between baseline-owned standardization and per-project customization

## slot: PERSONA_MENTAL_MODEL

registries, baselines, manifests, patterns, layers, and propagation paths

## insert: investigate-anchors

Key subsystems: `registry/` (project manifest, FG-1), `baseline/` (canonical templates, FG-2), `skills/{global,pattern,custom}/` (three-layer skill composition), `forge/resolver.py` (deterministic layer composition), `invariants/` (stratified by layer), `.forge/manifest.yaml` (per-project pattern declaration).

## insert: domain-bullets

- Check layer fit — global content must apply to every hybrid runtime project, pattern content to every project on that pattern, project content only to this one. A counterexample in the registry collapses the layer claim.
- Check self-bootstrap (FG-5) — any change to baseline structure must remain expressible against forge itself. If forge can't dogfood the change, the baseline is incomplete.
- Check read-vs-write boundary (FG-4) — forge reads other projects freely, writes only during `/bootstrap`, `/rebase`, or `/codex-sync`. Designs that require ambient writes are wrong.
