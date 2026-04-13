# Guidelines Enforcement Matrix

**Status:** Living Document

Maps each coding guideline section to its enforcement mechanism. Use this to understand where rules are checked and how violations are caught.

---

## Enforcement Mechanisms

| Mechanism | When It Runs | Catches |
|-----------|--------------|---------|
| **HARD Invariant** | Manual check before subsystem changes | System-breaking violations |
| **STRUCTURAL Invariant** | Manual check before migrations | Cross-file coordination issues |
| **Hook (Lint)** | Every Edit/Write | Style, syntax, simple patterns |
| **Hook (Custom)** | Every Edit/Write | Project-specific rules |
| **Skill Review** | `/review` invocation | Architectural drift, convention violations |
| **Convention** | Code review, PR process | Subjective quality, naming, structure |

---

## Matrix

| § | Guideline | Enforcement | Mechanism | Notes |
|---|-----------|-------------|-----------|-------|
| 1 | Immutability by Default | **Invariant** | DS-1: FROZEN_DATACLASSES (HARD) | Mutation corrupts shared state |
| 1 | Use `replace()` | **Invariant** | DS-2: USE_REPLACE (HARD) | — |
| 1 | Tuple Collections | **Convention** | — | Style preference, not enforced |
| 2 | Pipeline Layer Separation | **Invariant** | PL-1: LAYER_SEPARATION (STRUCTURAL) | Layer violations bypass validation |
| 2 | Intermediate Representations | **Invariant** | PL-2: IR_REQUIRED (STRUCTURAL) | Only if project has pipeline architecture |
| 2 | No Pass-Through of Computed Data | **Invariant** | PL-3: NO_PASSTHROUGH (STRUCTURAL) | Semantic layers stay clean |
| 2 | Determinism | **Invariant** | PL-4: DETERMINISM (HARD) | Same input → same output |
| 3 | Pure Transformations | **Invariant** | DS-3: PURE_FUNCTIONS (HARD) | Input mutation corrupts state |
| 3 | Return Collections | **Convention** | — | Design guidance |
| 4 | Error Philosophy | **Invariant** | Global: NO_SILENT_DROPS (HARD) | Silent partial output never allowed |
| 4 | Error Message Format | **Invariant** | Global: ERROR_FORMAT (HARD) | What/field/constraint/value |
| 4 | No Silent Drops | **Invariant** | Global: NO_SILENT_DROPS (HARD) | Unsupported features must error or warn |
| 5 | Flat Type Systems | **Conditional** | DS-4 if project commits to flat IR | Decision point in bootstrap |
| 5 | Propagation via Params | **Convention** | — | Design pattern |
| 6 | Test at Right Level | **Skill Review** | `/review` checks test structure | Not system-breaking |
| 6 | Test Project Code | **Skill Review** | `/review` flags language-feature tests | — |
| 6 | No Duplicate Coverage | **Skill Review** | `/review` finds redundant tests | — |
| 6 | Semantic Equivalence | **Convention** | — | Test design guidance |
| 6 | Use Test Framework | **Hook (Lint)** | Ruff flags `if __name__` in test files | — |
| 7 | Single Unit System | **Invariant** | CS-1: SINGLE_UNIT (HARD) | Mixed units produce wrong output |
| 7 | Coordinate Spaces | **Invariant** | CS-2: COORDINATE_CLARITY (STRUCTURAL) | Document and track transforms |
| 8 | Document Defaults | **Skill Review** | `/review` checks for default inventory | Process, not code |
| 8 | Changing Defaults | **Invariant** | CFG-1: DEFAULT_AGREEMENT (STRUCTURAL) | Defaults must agree across locations |
| 8 | Policy vs Invariant | **Convention** | — | Labeling guidance |
| 9 | Validate at Construction | **Invariant** | DS-5: VALIDATE_CONSTRUCTION (HARD) | Constraints enforced in `__post_init__` |
| 9 | Validate at Boundaries | **Invariant** | Global: BOUNDARY_VALIDATION (HARD) | Input validation at system edges |
| 9 | Constraint Auditing | **Skill Review** | `/review` checks for audit summaries | — |
| 10 | Invariant Classification | **Convention** | — | Meta: how to write invariants |
| 10 | Document Per Subsystem | **Convention** | — | Meta |
| 10 | Amendment Process | **Invariant** | META: AMENDMENT_REQUIRED (HARD) | Changes and amendments same commit |
| 11 | Self-Documenting Code | **Convention** | — | Subjective |
| 11 | No Dead Code | **Hook (Lint)** | Ruff F401 (unused import), F811 (redefinition) | — |
| 11 | Named Constants | **Hook (Lint)** | Ruff PLR2004 (magic value comparison) | Partial coverage |
| 11 | Minimal Changes | **Convention** | — | PR review guidance |
| 12 | Deterministic Output | **Invariant** | PL-4: DETERMINISM (HARD) | Byte-identical for same input |
| 12 | Single Conversion Path | **Invariant** | PL-5: SINGLE_PATH (STRUCTURAL) | No duplicate converters |
| 12 | Valid Output | **Invariant** | PL-6: VALID_OUTPUT (HARD) | Malformed output is a bug |
| 13 | End-to-End Coverage | **Conditional** | Feature completeness checklist | Only if project has declarative input |
| 13 | Declarative Input First | **Conditional** | Project principle | Decision point in bootstrap |
| 14 | Safety-Critical Constraints | **Invariant** | SEC-*: SAFETY (HARD) | Hard error, post-verification, labeled |
| 15 | Imports Flow Downward | **Invariant** | PL-7: DEPENDENCY_DIRECTION (STRUCTURAL) | Lower layers can't import higher |
| 15 | Adapter Pattern | **Convention** | — | Design pattern |
| 16 | Enums for Closed Sets | **Convention** | — | Design guidance |
| 16 | Strings for Open Sets | **Convention** | — | Design guidance |
| 17 | Explicit Unions | **Convention** | — | Type annotation style |
| 17 | Handle Every Variant | **Conditional** | DS-6 if unhandled causes silent drop | — |
| 17 | The Else Clause | **Conditional** | DS-6: EXHAUSTIVE_DISPATCH (HARD) | Must raise TypeError on unknown |
| 18 | No print() in Production | **Hook (Lint)** | Ruff T201 (print found) | Enable in ruff config |
| 18 | Level Discipline | **Convention** | — | Logging style |
| 19 | Standard Exception Hierarchy | **Convention** | — | Exception design guidance |
| 19 | Custom Exceptions | **Convention** | — | When to create them |
| 19 | Exception Granularity | **Convention** | — | Don't over-specialize |
| 20 | Layer Failure Modes | **Invariant** | PL-8: LAYER_ERROR_SEMANTICS (STRUCTURAL) | Each layer has defined behavior |
| 20 | Per-Item Isolation | **Invariant** | PL-9: ITEM_ISOLATION (STRUCTURAL) | One bad item doesn't kill batch |
| 20 | Structured Warning Collection | **Convention** | — | Implementation pattern |
| 21 | SkipError Protocol | **Convention** | — | Pattern for expected failures |
| 22 | Registry Dict | **Convention** | — | Dispatch style |
| 22 | Decorator Registration | **Convention** | — | Registry pattern |
| 22 | When If/Elif Is Fine | **Convention** | — | Guidance |
| 23 | Frozen Params Objects | **Convention** | — | Signature design |
| 23 | Keyword-Only Arguments | **Convention** | — | Use `*` for flags |
| 23 | Max Positional Parameters | **Skill Review** | `/review` flags >3 positional | — |
| 24 | Consistent Verbs | **Skill Review** | `/review` checks naming | — |
| 24 | Private Helper Prefixes | **Convention** | — | Naming style |
| 25 | Guard Clauses | **Convention** | — | Code structure preference |
| 25 | Normalize Before Branching | **Convention** | — | Input handling pattern |
| 26 | Explicit Loops for Error Handling | **Convention** | — | When comprehensions don't fit |
| 26 | Tuple at Return Boundary | **Convention** | — | Collection building pattern |
| 26 | Preserve Input Order | **Convention** | — | Output ordering |
| 27 | Serialize All Fields | **Invariant** | DS-7: SERIALIZATION_COMPLETE (HARD) | Silent field drops are data loss |
| 27 | Round-Trip Completeness | **Invariant** | DS-7 | All fields survive serialize/deserialize |
| 27 | Non-Default Emission | **Convention** | — | Formatter behavior |
| 28 | The `or` Trap | **Invariant** | DS-8: NO_OR_FOR_NULLABLE (HARD) | `or` replaces valid zeros |
| 28 | Empty String | **Invariant** | DS-8 | Same trap for strings |
| 29 | Six Type Mechanisms | **Convention** | — | Type system guidance |
| 29 | Enum vs Literal vs Constants | **Convention** | — | Decision tree |
| 29 | Protocol Over ABC | **Convention** | — | Interface design |
| 30 | Field Ordering | **Convention** | — | Dataclass style |
| 30 | `with_*()` Helpers | **Convention** | — | Mutation helper pattern |
| 31 | Amendment Culture | **Invariant** | META: AMENDMENT_REQUIRED (HARD) | No local workarounds |

---

## Summary by Enforcement Type

| Type | Count | Sections |
|------|-------|----------|
| **HARD Invariant** | 18 | §1, §2, §3, §4, §7, §9, §10, §12, §14, §17, §27, §28, §31 |
| **STRUCTURAL Invariant** | 10 | §2, §7, §8, §12, §15, §20 |
| **Hook (Lint)** | 4 | §6, §11, §18 |
| **Skill Review** | 8 | §6, §8, §9, §23, §24 |
| **Convention** | ~40 | §1, §3, §5, §6, §8, §10, §11, §16-§30 |
| **Conditional** | 5 | §5, §13, §17 |

---

## Bootstrap Decision Points

These guidelines require a project-level decision during bootstrap:

| Guideline | Decision | If Yes | If No |
|-----------|----------|--------|-------|
| §5 Flat Type Systems | Does project use extensible IR? | DS-4: FLAT_IR invariant | Use typed dataclasses freely |
| §13 Declarative Input | Does project have user-facing input? | Feature completeness checklist | Skip |
| §17 Exhaustive Dispatch | Can unhandled variants cause silent drops? | DS-6: EXHAUSTIVE_DISPATCH invariant | Convention only |

---

## Hook Configuration Reference

To enable all lint-enforceable rules, add to `pyproject.toml`:

```toml
[tool.ruff.lint]
select = [
    "F",      # Pyflakes (F401 unused imports, F811 redefinition)
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "I",      # isort
    "UP",     # pyupgrade
    "PLR",    # Pylint refactor (PLR2004 magic values)
    "T20",    # flake8-print (T201 print found)
]
```

---

## Adding Custom Enforcement

For rules not covered by standard linters (e.g., §28 `or` trap), options:

1. **Custom ruff plugin** — Write AST visitor to detect `x or default` patterns on Optional fields
2. **Pre-commit hook** — Grep-based check for common anti-patterns
3. **Skill instruction** — Add to `/review` skill's checklist

The `or` trap (§28) is a good candidate for a custom check:

```python
# Detects: value = data.get("field") or default
# Pattern: BinOp where left is Call to .get() and op is Or
```

---

## Maintenance

When adding new guideline sections:

1. Add row to the matrix
2. Determine enforcement mechanism
3. If invariant: add to `docs/invariants/` with ID
4. If hook-enforceable: update ruff config or add custom hook
5. If skill-review: update relevant skill file's checklist
6. If conditional: add to Bootstrap Decision Points
