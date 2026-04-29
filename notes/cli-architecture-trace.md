# Forge CLI architecture — trace and notes

**Purpose.** Self-notes mapping the actual code path an invocation of `forge` follows today, what each layer does, and where bootstrap-related work would slot in. Authored by tracing source in `forge/` and `tests/` end-to-end.

**Authoritative sources.** [forge/cli.py](../forge/cli.py), [forge/manifest.py](../forge/manifest.py), [forge/resolver.py](../forge/resolver.py), [forge/update.py](../forge/update.py), [forge/manifest.schema.json](../forge/manifest.schema.json), [pyproject.toml](../pyproject.toml). Tests confirm contracts: [tests/test_manifest.py](../tests/test_manifest.py), [tests/test_resolver.py](../tests/test_resolver.py), [tests/test_update.py](../tests/test_update.py).

---

## Entry point

[pyproject.toml:14](../pyproject.toml) declares one console script:

```
forge = "forge.cli:main"
```

So `forge <subcommand>` always lands in [forge/cli.py:10 main()](../forge/cli.py#L10).

## Subcommand dispatch — [forge/cli.py](../forge/cli.py)

Today there is exactly **one** subcommand: `update`. The CLI is built with `argparse.add_subparsers(dest="command", required=True)` — running `forge` with no subcommand is an error. `forge update` delegates to `forge.update._run` via `args.func`.

**Implication.** Adding `forge bootstrap` is a small structural change here: register a second sub-parser, point its `func` at a new entry. The existing dispatch shape is ready for siblings.

There is no `forge survey`, `forge status`, `forge monitor`, etc. yet. Those are LLM-side artifacts (markdown skills under `commands/forge/`), not CLI subcommands.

## `forge update` argument surface — [forge/update.py:118 _add_arguments](../forge/update.py#L118)

| Flag | Default | Purpose |
|---|---|---|
| `--apply` | off | write composed files; without it, dry-run + diff |
| `--exit-code` | off | exit 1 on drift (no-op with `--apply`) |
| `--manifest <path>` | `<cwd>/.forge/manifest.yaml` | manifest location |
| `--baseline-root <path>` | `manifest_path.parent.parent` | where `commands/global/`, `commands/pattern/`, `conventions/`, `invariants/` live |
| `--project-root <path>` | `manifest_path.parent.parent` | target project root |

**Default behavior** (`forge update` from inside a project tree): reads `<cwd>/.forge/manifest.yaml`, derives both `project_root` and `baseline_root` from the manifest's parent's parent, prints diff per command, exits 0. The dual-purpose default of `baseline_root = project_root` is what makes forge runnable on itself when the project's directory tree happens to contain a baseline — which is forge's own layout. For external consumers, `--baseline-root` must point at forge's checkout.

Exit codes: `0` clean (or apply succeeded), `1` drift with `--exit-code`, `2` manifest/resolver/IO error.

## `_run` flow — [forge/update.py:145](../forge/update.py#L145)

```
_run(args)
├── manifest_path  ← args.manifest or <cwd>/.forge/manifest.yaml
├── project_root   ← args.project_root or manifest_path.parent.parent
├── baseline_root  ← args.baseline_root or project_root
├── load_manifest(...)            ← see manifest.py trace below
├── plan_update(...)              ← see plan trace below
└── if --apply: apply_update(plan)  else: print diffs
```

Errors raised by `load_manifest` (`ManifestError`) and resolver invocations during planning (`ResolverError`) print to stderr and return 2.

---

## Manifest layer — [forge/manifest.py](../forge/manifest.py)

### Public entry point: `load_manifest(manifest_path, *, baseline_root, project_root=None)` — [manifest.py:99](../forge/manifest.py#L99)

Pipeline: read YAML → schema validation → semantic validation → build frozen dataclass.

**Path discipline.** If `project_root` is omitted, `manifest_path` *must* live under `<project>/.forge/manifest.yaml` — the loader infers the project root from that. Otherwise raises `ManifestError`.

### Schema validation — `_validate_schema` — [manifest.py:142](../forge/manifest.py#L142)

JSON-schema draft 2020-12 against [forge/manifest.schema.json](../forge/manifest.schema.json), loaded via `importlib.resources.files("forge")` — so the schema travels with the package wheel (declared as `package-data` in pyproject).

The schema enforces:

- `additionalProperties: false` at top level — no unknown keys.
- Required: `schema_version` (literal `1`), `patterns`, `project_context`, `resolution`.
- `patterns.primary` required (string); `secondary` optional array of `{name, scope}`.
- `project_context.description` required (≤280 chars).
- `resolution.{baseline_version, commands_dir, invariants_dir, conventions_dir}` all required; `baseline_version` matches `^\d{4}-\d{2}-\d{2}$`.
- Optional top-level: `domains`, `language`, `python_version` (`^\d+\.\d+$`), `toolchain`, `axes`, `customizations`.
- `customizations` is `{<command_name>: {slots?: {str: str}, inserts?: {str: str}}}` (`additionalProperties: false` per command).

**Error mapping.** `_validate_schema` translates jsonschema errors into specific `ManifestError` strings (e.g., `"patterns.primary required"`, `"unknown top-level key: …"`). This is what users see, not raw schema dumps.

### Semantic validation — `_validate_semantics` — [manifest.py:188](../forge/manifest.py#L188)

Beyond schema:

1. `language: python` ⇒ `python_version` required (else `ManifestError`).
2. `patterns.primary` must exist as a directory under one of `commands/pattern/`, `conventions/pattern/`, `invariants/pattern/` in `baseline_root`. (Pattern registration is implicit — a pattern is registered by the existence of a directory.)
3. Same for each `secondary[].name`. `secondary[].scope` must be a relative path under `project_root` resolving to an existing directory; `..` rejected.
4. `domains[]` must each be a directory under `<baseline_root>/conventions/domain/`.
5. `resolution.{commands_dir, invariants_dir, conventions_dir}` must be relative paths without `..`.
6. `customizations.<name>` must match an existing `<baseline_root>/commands/global/<name>.md` (filename stem; "stem with dot in it" excluded — e.g., `foo.prompt.md` cannot be a customization key).
7. Warns (`UserWarning`) when `language` is present and not `python`. Bug-fixed under issue #19: warning suppressed when `language` is absent.

### Frozen dataclass build — `_build_manifest` — [manifest.py:270](../forge/manifest.py#L270)

Produces `Manifest` (frozen) with read-only views: `customizations` is a `MappingProxyType` of `MappingProxyType`s. Slot/insert bodies are normalized via `_normalize_block` ([manifest.py:337](../forge/manifest.py#L337)) — strip leading `\n`, strip trailing whitespace, append single `\n` (empty string stays empty).

**Note.** The dataclass field is `customizations: Mapping[str, SkillCustomization]` and the inner type is `SkillCustomization` (slots, inserts) — even though the rename to "commands" was issue 19's headline. Issue 19 renamed directory paths and `Resolution.commands_dir`; the legacy class name `SkillCustomization` survives. Cosmetic but worth noting if a future issue wants total uniformity.

---

## Resolver layer — [forge/resolver.py](../forge/resolver.py)

### Public entry: `resolve(manifest, baseline_root, project_root) -> ResolvedProject` — [resolver.py:37](../forge/resolver.py#L37)

`ResolvedProject` is a frozen dataclass: `commands: dict[str, str]`, `invariants: str`, `conventions: dict[str, str]`. The dict values are fully composed text bodies.

If `manifest.secondary_patterns` non-empty, emits a warning saying resolver v1 ignores them (no scoped composition yet).

Pipeline: compose commands → compose invariants → compose conventions.

### Command composition — `_compose_commands` — [resolver.py:59](../forge/resolver.py#L59)

```
for each <name>.md in baseline_root/commands/global/ (excluding any stem containing "."):
    template       = read commands/global/<name>.md
    pattern_contrib = parse commands/pattern/<primary>/<name>.md (if exists)
    project_contrib = manifest.customizations[<name>] (if present)
    out[<name>]    = _compose_command(template, pattern, project)
```

The "no dot in stem" filter excludes companion files like `foo.prompt.md`.

#### `_compose_command` — [resolver.py:89](../forge/resolver.py#L89)

Two passes over the global template:

**1. Slots.** Regex `{{NAME}}` or `{{NAME=default}}` ([resolver.py:10 PLACEHOLDER_RE](../forge/resolver.py#L10)). Resolution order: project → pattern → inline default → error. Project layer **overrides** pattern layer (highest precedence wins). Confirmed by [tests/test_resolver.py:264](../tests/test_resolver.py#L264) `test_slot_precedence_project_over_pattern_over_default`.

Special handling: paragraph-embedded slots (slot whose surrounding line has prose around it, vs. slot alone on its own line) get trailing newline stripped before substitution. See `_is_paragraph_embedded` — [resolver.py:265](../forge/resolver.py#L265).

**2. Inserts.** Regex `<!-- insert: NAME -->` on its own line ([resolver.py:11 INSERT_RE](../forge/resolver.py#L11)). Composition: `pattern.inserts[name] + "\n\n" + project.inserts[name]` (whichever exist), with `.rstrip()` per part and a final trailing `\n`. **Both layers are concatenated, pattern first, project second.** Confirmed by [tests/test_resolver.py:307](../tests/test_resolver.py#L307) `test_insert_ordering_pattern_then_project`. If neither layer fills, the comment line is removed entirely (empty replacement).

**Validation gate before substitution.** For each slot/insert provided by pattern or project, the name must appear in the global template's set of placeholders. Mismatch raises `ResolverError` with the message `unknown placeholder 'X' in <source>: not defined in commands/global/<command>.md`. This is the safety net catching typos and stale customizations after a global rename.

#### Pattern contribution parsing — `_parse_contribution` — [resolver.py:211](../forge/resolver.py#L211)

`commands/pattern/<pattern>/<command>.md` files are markdown documents with `## slot: NAME` and `## insert: NAME` H2 headers. The parser:

1. Finds all `## slot:` / `## insert:` headers via `SLOT_INSERT_HEADER_RE` ([resolver.py:12](../forge/resolver.py#L12)), but **skips any inside fenced code blocks** ([resolver.py:222](../forge/resolver.py#L222), `_in_fence`).
2. Body is everything until the next header (or EOF), normalized.
3. Headers found inside fences ⇒ literal text, not parsed as a slot/insert. Allows pattern docs to *show* example syntax in code blocks without it being interpreted.

Fence detection uses `FENCE_LINE_RE` ([resolver.py:15](../forge/resolver.py#L15)) — supports nested fences via tick-count comparison.

### Invariant composition — `_compose_invariants` — [resolver.py:146](../forge/resolver.py#L146)

Concatenates (in order, only those that exist):

1. `<baseline>/invariants/global.md`
2. `<baseline>/invariants/pattern/<primary>.md`
3. `<baseline>/invariants/domain/<domain>.md` for each domain
4. `<project>/<resolution.invariants_dir>/global.md`

Joined with `\n\n` between files (each file's trailing whitespace stripped first); final `\n`.

**Collision check.** `INVARIANT_ID_RE` matches `## XX-N — Name` headers ([resolver.py:16](../forge/resolver.py#L16)). Same invariant ID present in two files ⇒ `ResolverError`. Forces uniqueness across layers.

### Convention composition — `_compose_conventions` — [resolver.py:181](../forge/resolver.py#L181)

If `manifest.language is None`: returns empty dict. Otherwise concatenates (only existing files):

1. `<baseline>/conventions/global/<language>.md` (the global conventions layer)
2. `<baseline>/conventions/pattern/<primary>/<language>.md`
3. `<baseline>/conventions/domain/<domain>/<language>.md` for each domain
4. `<project>/<resolution.conventions_dir>/<language>.md`

If none exist, returns `{language: ""}`. Otherwise `{language: composed_text}`.

The global conventions layer lives at `conventions/global/<language>.md` — symmetric with `invariants/global.md` and the pattern/domain trees.

---

## Update layer — [forge/update.py](../forge/update.py)

### `plan_update(manifest, baseline_root, project_root) -> UpdatePlan` — [update.py:37](../forge/update.py#L37)

1. Calls `resolve(...)`.
2. Iterates `resolved.commands` (sorted) and for each, writes a target path: `<project>/<resolution.commands_dir>/<name>.md`.
3. Compares against existing file:
   - Missing ⇒ `FileChange(kind="create", body, diff)` where diff is unified-diff vs `/dev/null`.
   - Different ⇒ `FileChange(kind="update", body, diff)`.
   - Identical ⇒ `FileChange(kind="unchanged", body, diff="")`.

**Today, only `commands` are written.** The resolver also produces `invariants` and `conventions`, but `plan_update` ignores them. The CLI doesn't surface them. This is a real gap — invariants composed by resolver are dead-ended, even though all the layered composition logic exists. Tests assert this scope: [test_update.py:127](../tests/test_update.py#L127) `test_only_resolver_owned_files_in_plan`.

### `apply_update(plan)` — [update.py:77](../forge/update.py#L77)

Writes only changes whose kind != `"unchanged"`. Asserts trailing newline on every body before write — `UpdateError` if missing. Creates parent directories as needed. IO errors wrapped to `UpdateError`.

---

## Composition order summary (the single most useful page)

For one command file `<name>.md` to be produced:

```
template:    baseline/commands/global/<name>.md
            └── slots: {{NAME}}, {{NAME=default}}
            └── inserts: <!-- insert: NAME -->

pattern:     baseline/commands/pattern/<primary>/<name>.md   (optional)
            └── ## slot: NAME / ## insert: NAME blocks

project:     manifest.customizations[<name>].{slots, inserts}  (optional)

For each slot in template:
    project[slot] OR pattern[slot] OR inline_default OR error

For each insert in template:
    pattern[insert] + "\n\n" + project[insert]      (concatenated; either may be empty)
```

For `invariants/global.md` (single output, never written today):

```
global  ⊕  pattern  ⊕  domain[*]  ⊕  project   (only files that exist; ID-collision-checked)
```

For `conventions/<language>.md` (single output, never written today):

```
conventions/global/lang  ⊕  pattern/lang  ⊕  domain[*]/lang  ⊕  project/lang
```

`⊕` = concatenation with `\n\n` separator and one final `\n`.

---

## Mental model — what `forge update` actually does

1. **Reads a fully-formed manifest.** It is *not* generative — the manifest must already exist with all required fields.
2. **Validates** schema and pattern/domain registration against the baseline tree.
3. **Composes** template + pattern + project per command, plus invariants and conventions.
4. **Writes** only the composed commands into `<project>/<commands_dir>/`. Invariants and conventions are computed and discarded.
5. **Idempotent** by construction: re-running yields all-`unchanged`.

That's the whole runtime. There is no LLM call, no prompt execution, no file generation outside the resolver's substitution.

---

## What `bootstrap` would need to add

Bootstrap is an *upstream* of update. Update consumes a manifest; bootstrap produces one.

**Inputs** bootstrap must obtain:

- A target project (path or registry name).
- A spec doc (CLAUDE.md, README, design doc — whatever the project provides).
- A pattern declaration (must resolve to a directory under `baseline/commands/pattern/`).
- Project context (`description` is mandatory, ≤280 chars).
- Resolution paths (`commands_dir`, `invariants_dir`, `conventions_dir`, `baseline_version`).
- Optional skeleton fields: `language`, `python_version`, `toolchain`, `axes`, `domains`.
- Customizations per command — produced by running `commands/custom/<command>.prompt.md` against the spec doc, the pattern contribution, and the global template.

**Outputs** bootstrap must produce:

- `<target>/.forge/manifest.yaml` validating against `forge/manifest.schema.json`.
- (Optionally) chained call to `apply_update(plan_update(...))` to materialize the resolved files.
- A `registry/projects.yaml` update moving the target off `manifest: none` and setting `baseline_version`.

**Wire-in points the existing code provides:**

- The CLI sub-parser pattern in [forge/cli.py:12](../forge/cli.py#L12) is ready for a second subcommand.
- `apply_update` and `plan_update` are reusable as the second half of bootstrap (after the manifest is written).
- `load_manifest` is the natural validation gate — bootstrap should call it on its own emitted YAML before declaring success.
- `_registered_patterns` ([manifest.py:249](../forge/manifest.py#L249)) is the right helper to populate the user-facing pattern menu in an interactive bootstrap.

**Wire-in points missing today:**

- No registry-aware loader. Pattern names, project paths, and `baseline_version` are everywhere in `registry/projects.yaml` but no code reads it. A bootstrap that names the target by registry key would need this.
- No prompt runner. Whether driven by Claude API or by emitting a paste-this-into-Claude bundle, `commands/custom/<command>.prompt.md` files are LLM-side instructions — they need an executor.
- No skeleton-generation prompt. The six `commands/custom/*.prompt.md` only fill `customizations:`; nothing produces patterns/axes/project_context/resolution from a spec doc.

---

## Things to keep in mind for future work

- **Update writes only commands.** Invariants and conventions are composed but discarded. If/when bootstrap needs to write them into the target, this is a real change to `plan_update`.
- **Pattern registration is by directory existence.** Adding a new pattern means creating directories under `commands/pattern/`, `conventions/pattern/`, `invariants/pattern/`. No central registry file. `_registered_patterns` walks all three.
- **Custom command names are validated against `commands/global/`.** A `customizations.foo:` block where `commands/global/foo.md` does not exist ⇒ `ManifestError` at load time, before resolution.
- **Slot validation is two-stage:** schema permits arbitrary slot names; the resolver rejects names that aren't placeholders in the template. Schema is permissive; resolver is strict.
- **Inserts are additive (pattern then project).** No subtraction. A pattern contribution that ships do-bullets cannot be suppressed at the project layer. Issue #18 trial surfaced this as F14.
- **Templates have no section-conditional mechanism.** Inserts can only fill, not omit. Hard-coded sections in global templates ship to every project. Issue #18 trial surfaced this as F15.
- **The `customizations` keys are bound to `commands/global/` filenames.** Pattern layer can ship a contribution; only the global template defines available placeholders. Adding a pattern-only command (no global counterpart) would bypass the validation gate.
- **Resolver-v1 ignores secondary patterns** with a warning. Whatever bootstrap produces, secondary patterns are decorative until composition support arrives.
- **`SkillCustomization` is the legacy class name.** Issue 19 renamed `Resolution.skills_dir → commands_dir` but left this dataclass name. Cosmetic.
- **`conventions/global/<language>.md` is the global-language conventions layer.** Symmetric with `invariants/global.md` and the pattern/domain trees. Read at [resolver.py:188](../forge/resolver.py#L188).
- **Manifest paths are normalized to absolute** at build time (`source_path.resolve()`, `project_root.resolve()`). All later path math is absolute.
