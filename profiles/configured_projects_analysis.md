# Configured Projects: Deep Comparison

**Generated:** 2026-04-12 | **Projects analyzed:** mill_ui, homenet, TenneCNC_LLC, penumbra-poc

---

## Configuration Maturity Matrix

|  | mill_ui | homenet | TenneCNC_LLC | penumbra-poc |
|--|---------|---------|--------------|--------------|
| **Domain** | CAM pipeline | Infrastructure ops | Document corpus | ML pipeline POC |
| **Baseline version** | 2026-04-05 | — | 2026-04-05 | — |
| **CLAUDE.md** | Yes | Yes | Yes | Yes |
| **Skills** | 13 | 8 | 12 | 7 |
| **Invariant files** | 19 | 8 | 1 | 4 |
| **Hooks** | lint-python | lint-python | — | lint-python |
| **settings.json** | Yes | Yes | No | Yes |
| **Capabilities listed** | 68 | 13 | 6 (overridden) | ~10 |
| **Test files** | 99 | 0 | 0 | 8 |
| **Source LoC** | ~76,000 | ~3,400 | — (docs) | ~2,800 |

---

## Skill Coverage vs Baseline

The baseline defines 6 core skill templates: `/spec`, `/architect`, `/review`, `/engineer`, `/close-out`, `/debug`. Pre-split projects ship a standalone `/audit`; in the current baseline its work is folded into `/architect` (design-time concerns) and `/review` (artifact concerns).

| Baseline Skill | mill_ui | homenet | TenneCNC | penumbra-poc |
|----------------|---------|---------|----------|--------------|
| /spec | Yes | Yes | — | Yes |
| /architect | **MISSING** | **MISSING** | — | Yes |
| /review | Yes | Yes | Yes (6 personas) | Yes |
| /engineer | cam-engineer | Yes (infra) | — | Yes (ML) |
| /close-out | Yes | Yes (extended) | — | Yes |
| /debug | Yes | Yes (infra) | — | Yes |

**Key gap:** `/architect` is missing from 3 of 4 projects — it was added to the baseline after they were bootstrapped. This is the clearest rebase signal.

**TenneCNC is structurally different:** It replaces the engineering skill stack (spec, engineer, debug, close-out) with business/operational personas (staff, business, whitepaper). This is intentional — it's not a codebase.

### Project-Specific Skills (not in baseline)

| Skill | Project | Category | Baseline Candidate? |
|-------|---------|----------|---------------------|
| `/cam-engineer` | mill_ui | Domain engineering | No — domain-specific |
| `/pml-author` | mill_ui | Domain engineering | No — domain-specific |
| `/extend` | mill_ui | Extension patterns | **Yes** — generalizable |
| `/profile` | mill_ui | Performance audit | **Yes** — generalizable |
| `/snapshot-recipes` | mill_ui | Artifact lifecycle | **Maybe** — golden test pattern |
| `/update-docs` | mill_ui | Doc maintenance | **Maybe** — trigger table pattern |
| `/check-invariants` | mill_ui, homenet | Invariant loading | **Yes** — already in 2 projects |
| `/glossary` | mill_ui, homenet | Terminology | **Yes** — already in 2 projects |
| `/whitepaper` | TenneCNC | Doc editing | No — doc-corpus-specific |
| `/business` | TenneCNC | Domain advisor | No — domain-specific |
| `/staff` | TenneCNC | Multi-persona | **Yes** — pattern generalizable |
| `/review` (6 personas) | TenneCNC | Multi-perspective review | **Yes** — adversarial/constructive pattern |

---

## Where Each Project Is Ahead

### mill_ui — Most Mature Overall

**Ahead of baseline in:**
- **Invariant depth** (19 subsystem files vs baseline's suggestion of "3-8")
- **Regression traps** — 8 documented LLM-specific failure modes with invariant responses
- **Capabilities table** — 68 entries, organized by functional category
- **Performance profiling** — 360-line `/profile` skill with measurement discipline, triage, known gotchas
- **Extension codex** — `/extend` skill with 7 patterns for safely adding features
- **Change-aware audit** — tracks `last_audit_commit`, defers findings, escalates growing debt
- **Snapshot/golden lifecycle** — decoupled recipe baselines with explicit regeneration workflow
- **Feature completeness gate** — PML-First Principle requires 5 artifacts per feature (impl, AST, parser, syntax doc, recipe)

**Innovations to pull back:**
1. Regression traps section in invariant templates
2. `/profile` skill template
3. `/extend` skill template (extension pattern codex)
4. Change-aware audit with context tracking
5. Feature completeness gate pattern

### homenet — Best Infrastructure Safety Model

**Ahead of baseline in:**
- **Operational safety invariants** — SEC-1 through SEC-6, OPS-1 through OPS-5 covering secrets, blacklists, auth sequencing, idempotency, dry-run, session logging
- **Command blacklist** — explicit denial list (rm -rf /, mkfs, etc.) enforced as HARD invariant
- **Tool-first governance** — formal checklist: argparse CLI, .env secrets, session logging, --dry-run, capabilities table entry
- **PKI invariant subsystem** — 5 PKI-specific invariants (no self-signed, CA key protection, short-lived certs, trust-before-verify, root cert only)
- **Close-out with infrastructure verification** — Phase 1 includes SSH connectivity, service status, role compliance, inventory accuracy checks alongside code checks
- **Intentional exceptions table** — documented justified deviations (UniFi, Tailscale) with rationale

**Innovations to pull back:**
1. Command blacklist pattern for `[infrastructure]` projects
2. Tool completeness checklist (5-point gate)
3. Session logging as invariant
4. Infrastructure-aware close-out (machine verification phase)
5. Intentional exceptions documentation pattern

### TenneCNC_LLC — Most Novel Architecture

**Ahead of baseline in:**
- **Multi-persona system** — 6 specialized roles with shared context, independent review, conflict resolution via President synthesis
- **Shared context architecture** — `staff/context/tennecnc.md` loaded by all personas before responding, ensures consistent numbers/assumptions
- **Voice enforcement** — prohibited language lists, three claim types, scale-invariant framing, abstraction boundary enforcement
- **Cross-reference protocol** — micro-summary + canonical pointer, never copy-paste, CONCEPT_COVERAGE.md as searchable index
- **Capability override with rationale** — each baseline override states why (e.g., "Documents don't have bugs — they have inconsistencies")
- **TODO protocol** — specific, categorized, actionable placeholders replacing the no-comments rule
- **6-persona review** — 3 adversarial (Skeptic, Auditor, Philosopher) + 3 constructive (Mentor, First Reader, Builder) with cross-persona synthesis
- **5-phase corpus audit** — Census → Redundancy → Consistency → Structure → Gap

**Innovations to pull back:**
1. Multi-persona staff template (roles + shared context + synthesis)
2. Voice enforcement for `[doc-corpus]` (prohibited lists, claim types)
3. Cross-reference protocol
4. Capability override documentation pattern
5. Adversarial/constructive review framework

### penumbra-poc — Best Research/POC Pattern

**Ahead of baseline in:**
- **Stage gating** — SG-1 invariant with explicit advancement criteria (<80% ceiling → advance, >90% ceiling → stay), documentation required for each gate
- **Data gates** — `docs/data_gates.md` blocks code advancement until schema questions resolved
- **Confidence-required** — CT-3 invariant mandates per-angle confidence scores on all completions
- **Mask preservation** — CT-2 invariant preserves visible/hidden distinction throughout pipeline
- **Edge deployment constraint** — every model must have CPU inference path, <50ms target, no GPU-only designs
- **Operator vs engineering metrics** — EV-3 explicitly distinguishes operator-facing (BF/MBF) from engineering (RMSE) metrics
- **Stratified evaluation** — EV-2 requires results by difficulty class, coverage angle, confidence bin, species
- **Cleanest baseline alignment** — 7/7 baseline skills present, zero project-specific skill additions

**Innovations to pull back:**
1. Stage gating pattern for `[pipeline]` or new `[staged-research]` tag
2. Data gates blocking code advancement
3. Operator vs engineering metric distinction
4. Confidence-required pattern for ML projects

---

## Where Each Project Needs Updates

### Rebase Gaps (baseline skills added after bootstrap)

| Project | Missing | Action |
|---------|---------|--------|
| mill_ui | `/architect` | Rebase — add from baseline template, frame for CAM |
| homenet | `/architect` | Rebase — add from baseline template, frame for infrastructure |
| TenneCNC_LLC | `/architect` | Rebase — add from baseline template, frame for corpus analysis |
| penumbra-poc | (none) | Current |

### Configuration Gaps

| Gap | mill_ui | homenet | TenneCNC | penumbra-poc |
|-----|---------|---------|----------|--------------|
| baseline_version in registry | 2026-04-05 | **MISSING** | 2026-04-05 | **MISSING** |
| Hooks/settings.json | Yes | Yes | **MISSING** | Yes |
| Invariant depth | 19 files | 8 files | **1 file (9 invariants)** | 4 files |
| Test coverage | 99 files | **None** | N/A (docs) | 8 files |

### Specific Observations

**homenet:**
- No `baseline_version` in registry despite being fully configured
- No tests (all validation is operational — SSH to machines)
- Invariant system is comprehensive (8 files) but pre-dates baseline extraction
- Missing `/architect` skill

**TenneCNC_LLC:**
- No hooks or settings.json — voice enforcement is skill-level only, not automated
- Single invariant file with 9 invariants (CI-1 through CI-6, PI-1 through PI-3) — could benefit from splitting into corpus.md and personas.md
- Missing standard engineering skills (spec, engineer, debug, close-out) — intentional for non-code project, but `/spec` could still be useful for planning corpus work

**penumbra-poc:**
- No `baseline_version` in registry despite being configured
- Newest project — cleanest baseline alignment
- Small invariant set (4 files) appropriate for POC scope

---

## Patterns to Pull Back to Baseline

### Tier 1: Ready to Generalize (proven in 2+ projects)

| Pattern | Source | Evidence | Proposed Baseline Change |
|---------|--------|----------|--------------------------|
| `/check-invariants` skill | mill_ui, homenet | Subsystem-to-file mapping, load before modifying | Add skill template |
| `/glossary` skill | mill_ui, homenet | Domain terminology reference, prevents semantic drift | Add skill template |
| Post-edit lint hook | mill_ui, homenet, penumbra-poc | settings.json + lint-python.sh | Add to bootstrap Phase 5 as standard |
| Regression traps in invariants | mill_ui, homenet | Explicit LLM failure modes documented | Add section to invariant templates |
| Amendment process | mill_ui, homenet | 5-step protocol for changing invariants | Add to baseline invariant docs |
| Change-aware review | mill_ui, homenet | `last_audit_commit` tracking, deferred findings | Fold into `/review` template |

### Tier 2: Worth Generalizing (proven in 1 project, clearly reusable)

| Pattern | Source | Proposed Baseline Change |
|---------|--------|--------------------------|
| `/profile` skill | mill_ui | Add performance audit template for `[python]` |
| `/extend` skill | mill_ui | Add extension pattern codex template |
| Feature completeness gate | mill_ui | Document as pattern for `[declarative-input]` |
| Multi-persona framework | TenneCNC | Add `/staff` template for `[multi-persona]` |
| Voice enforcement | TenneCNC | Add to `[doc-corpus]` capability with prohibited lists |
| Cross-reference protocol | TenneCNC | Add to `[doc-corpus]` capability |
| Stage gating | penumbra-poc | Add as pattern for `[pipeline]` research projects |
| Data gates | penumbra-poc | Document as pattern for data-driven POCs |
| Command blacklist | homenet | Add to `[infrastructure]` capability |
| Tool completeness checklist | homenet | Add to Tool-Codification capability |

### Tier 3: Novel but Domain-Specific (document, don't template)

| Pattern | Source | Notes |
|---------|--------|-------|
| 6-persona adversarial/constructive review | TenneCNC | Powerful but heavy — document as advanced pattern |
| Capability override with rationale | TenneCNC | Document the pattern; each project does it differently |
| Operator vs engineering metrics | penumbra-poc | ML-specific distinction |
| PKI invariant subsystem | homenet | Infrastructure-specific |

---

## Recommended Next Actions

1. **Rebase `/architect` into mill_ui, homenet, TenneCNC_LLC** — all three are missing it. This is the clearest drift signal from the 2026-04-05 baseline.

2. **Add `baseline_version` to registry for homenet and penumbra-poc** — they're configured but the registry doesn't reflect it.

3. **Pull Tier 1 patterns into baseline** — `/check-invariants` template, `/glossary` template, lint hook as standard, regression traps section, amendment process, change-aware review.

4. **Add TenneCNC hooks** — it's the only configured project without settings.json. Even for a doc corpus, a hook checking markdown link resolution or CONCEPT_COVERAGE sync could add value.

5. **Split TenneCNC invariants** — 9 invariants in one file would benefit from corpus.md + personas.md split matching the two subsystem categories.
