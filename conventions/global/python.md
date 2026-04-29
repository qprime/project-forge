# Python Coding Guidelines

Rules for AI agents writing Python in projects created from this baseline.

Each rule has: the rule (imperative), a right/wrong code pair, and the failure mode if violated. Cross-references to invariants in `invariants/global.md` (GL-N) are noted where applicable.

How to use: when about to make a decision listed below, look up the rule. If a rule blocks correct work, raise it; do not work around it locally.

---

## Declaring a dataclass

### Frozen by default for data shared across modules

Implements GL-3 (data shared across modules is immutable by default). Mutation is allowed at documented boundaries — builders mid-construction, caches with a documented eviction contract, ORM models, framework-managed objects.

```python
# Right
@dataclass(frozen=True)
class Measurement:
    width_mm: float
    height_mm: float

# Wrong (shared across modules, not frozen)
@dataclass
class Measurement:
    width_mm: float
```

**Failure mode:** shared mutable state turns innocuous changes into action-at-a-distance bugs.

### Field order

1. Required (no default)
2. Optional typed (`field: Type | None = None`)
3. Factory defaults (`field(default_factory=...)`)
4. Scalar defaults (`field: Type = value`)

```python
@dataclass(frozen=True)
class Feature:
    name: str                                                # required
    width_mm: float
    description: str | None = None                           # optional
    tags: tuple[str, ...] = field(default_factory=tuple)     # factory
    enabled: bool = True                                     # scalar
```

**Failure mode:** `TypeError` from fields-without-defaults following fields-with-defaults; constructors become unpredictable.

### Tuples for structural collections

```python
# Right
items: tuple[Item, ...]
boundaries: tuple[Point, ...]

# Wrong
items: list[Item]
```

**Failure mode:** accidental mutation of shared structure.

---

## Modifying a frozen dataclass

### Always use `replace()`

```python
# Right
new_item = replace(item, width_mm=100)

# Wrong
item.width_mm = 100  # FrozenInstanceError at runtime
```

### Replace nested dicts wholesale

```python
# Right
new_item = replace(item, metadata={**item.metadata, "processed": True})

# Wrong
item.metadata["processed"] = True  # mutates shared dict
```

**Failure mode:** technically-mutable nested structures break the immutability contract.

### Provide `with_*()` helpers for repeated patterns

```python
def with_tags(self, *new_tags: str) -> Feature:
    return replace(self, tags=self.tags + new_tags)
```

---

## Writing a function that transforms data

### Pure: no input mutation, no side effects

Implements GL-4 (same input, same output).

```python
# Right
def process(domain: Domain) -> tuple[Item, ...]:
    return tuple(items_from(domain))

# Wrong
def process(domain: Domain) -> tuple[Item, ...]:
    domain.metadata["processed"] = True
    return tuple(items_from(domain))
```

**Failure mode:** debugging becomes guessing; tests become flaky; reproductions become impossible.

### No hidden state, explicit seeds

```python
# Right
def shuffle(items: tuple[Item, ...], *, seed: int) -> tuple[Item, ...]:
    rng = random.Random(seed)
    return tuple(rng.sample(items, len(items)))

# Wrong
def shuffle(items: tuple[Item, ...]) -> tuple[Item, ...]:
    return tuple(random.sample(items, len(items)))  # unseeded
```

### Always return a collection for zero-or-more results

```python
# Right
def split(region: Region) -> tuple[Region, ...]: ...

# Wrong
def split(region: Region) -> Region | tuple[Region, ...]: ...
```

**Failure mode:** caller branches on type to handle "one vs many." Agents copy whichever branch they saw first and miss the other.

---

## Building a collection

### Explicit loop when error handling or branching is involved

```python
# Right
items: list[Item] = []
warnings: list[str] = []
for raw in source:
    try:
        items.append(Item.from_raw(raw))
    except ValueError as e:
        warnings.append(f"Skipped {raw.id}: {e}")

# Wrong
items = [Item.from_raw(raw) for raw in source]  # any failure kills the batch
```

### Comprehensions only for simple, infallible transforms

```python
# Right
names = [item.name for item in items]
```

### Convert to tuple at the return boundary

```python
# Right
def collect_items(source) -> tuple[Item, ...]:
    result: list[Item] = []
    for raw in source:
        result.append(Item.from_raw(raw))
    return tuple(result)
```

### Preserve input order; dedupe with dict keyed by identity

```python
seen: dict[str, Item] = {}
for item in items:
    key = item.identity_key()
    if key not in seen:
        seen[key] = item
return tuple(seen.values())
```

---

## Raising an error

### Choose the standard exception

| Exception | When |
|---|---|
| `ValueError` | Right type, violates constraint (negative width, out of range) |
| `TypeError` | Wrong type, unhandled union variant |
| `KeyError` | Required key missing from a mapping |
| `RuntimeError` | "Shouldn't happen" state, runtime invariant violation |
| `NotImplementedError` | Interface method not yet implemented |
| `FileNotFoundError` | Expected file does not exist |

### Message format: what failed, what field, what constraint, actual value

Implements GL-5 (failures carry context).

```python
# Right
raise ValueError("SheetConfig: width_mm must be > 0, got -3.5")

# Wrong
raise ValueError("invalid width")
```

If the violation maps to an invariant, cite it:

```python
raise ValueError("Joint at 150mm aligns with adjacent layer (BM-9 violation)")
```

### Never silently drop unsupported cases

If the unsupported case is required behavior, raise. If skipping is acceptable per the contract, collect a structured warning (see *Handling errors per layer*) — not `warnings.warn`, which is easy to miss in generated CLIs and pipelines.

```python
# Right (required behavior — fail hard)
if constraint.type not in SUPPORTED:
    raise ValueError(f"Constraint {constraint.type} not implemented")

# Right (skipping is part of the contract)
if constraint.type not in SUPPORTED:
    warnings_out.append(f"Constraint {constraint.type} not implemented — skipped")
    continue

# Wrong (silent skip)
if constraint.type in SUPPORTED:
    apply(constraint)
```

**Failure mode:** silent partial output is the hardest class of bug to diagnose.

### Custom exceptions only when callers will catch them specifically

```python
# Right (one per subsystem when callers distinguish)
class ValidationError(ValueError):
    """Constraint check failed during validation."""

# Wrong (class explosion)
class WidthTooSmallError(ValidationError): ...
class HeightTooSmallError(ValidationError): ...
```

---

## Handling expected failures

### `SkipError` for "operation impossible for this input"

```python
class SkipError(ValueError):
    """Operation impossible for this input — expected condition, not a bug."""

def generate(domain: Domain, params: Params, *, allow_empty: bool = False) -> tuple[Item, ...]:
    if domain.area < min_area(params):
        if allow_empty:
            return ()
        raise SkipError(f"Domain area {domain.area} below minimum {min_area(params)}")
    return tuple(do_work(domain, params))
```

The layer above catches `SkipError`. It never propagates past the immediate caller.

### Per-item isolation when partial output is part of the contract

Use per-item isolation when the operation's contract allows partial output (analysis, reporting, best-effort transforms). Do *not* use it for transactional, safety-critical, publishing, migration, or validation paths — those must fail the whole batch on any item failure.

```python
# Right (analysis — partial output is acceptable)
results: list[Result] = []
warnings: list[str] = []
for item in items:
    try:
        results.append(analyze(item))
    except ValueError as e:
        warnings.append(f"Skipped {item.id}: {e}")

# Right (transactional — any failure aborts)
results = [persist(item) for item in items]  # raises kill the batch, as required
```

---

## Dispatching on a value

### Registry dict at 5+ branches or when types are added regularly

```python
# Right
@dataclass(frozen=True)
class FeatureData:
    width_mm: float
    depth_mm: float
    params: Mapping[str, Any]

HANDLERS: dict[str, Callable[[FeatureData], Output]] = {
    "pocket": handle_pocket,
    "profile": handle_profile,
    "hole": handle_hole,
}

def handle(feature_type: str, data: FeatureData) -> Output:
    handler = HANDLERS.get(feature_type)
    if handler is None:
        raise ValueError(f"Unknown feature type: {feature_type}")
    return handler(data)
```

### Decorator registration for large registries

```python
HANDLERS: dict[str, Callable[[FeatureData], Output]] = {}

def register(feature_type: str):
    def decorator(fn: Callable[[FeatureData], Output]):
        HANDLERS[feature_type] = fn
        return fn
    return decorator

@register("pocket")
def handle_pocket(data: FeatureData) -> Output: ...
```

### Normalize at dispatch entry, not in handlers

```python
# Right
def handle(feature_type: str, data: FeatureData) -> Output:
    handler = HANDLERS.get(feature_type.lower().strip())
    ...

# Wrong (normalization scattered into handlers)
def handle_pocket(data: FeatureData) -> Output:
    if data.kind.lower() == "pocket":
        ...
```

### Short chains (2–3 branches, unlikely to grow) can use if/elif

---

## Matching on a union type

### Exhaustive with explicit `else`

```python
# Right
def process(feature: FaceFeature) -> Output:
    if isinstance(feature, DrillHole):
        return process_hole(feature)
    elif isinstance(feature, SquareMortise):
        return process_mortise(feature)
    elif isinstance(feature, CarvedDesign):
        return process_carving(feature)
    else:
        raise TypeError(f"Unhandled feature type: {type(feature).__name__}")

# Wrong (silent fallthrough)
def process(feature: FaceFeature) -> Output:
    if isinstance(feature, DrillHole):
        return process_hole(feature)
    elif isinstance(feature, SquareMortise):
        return process_mortise(feature)
    # CarvedDesign returns None silently
```

### `match` with wildcard

```python
match feature:
    case DrillHole():
        ...
    case SquareMortise():
        ...
    case _:
        raise TypeError(f"Unhandled feature type: {type(feature).__name__}")
```

**Failure mode:** new variant added to the union, dispatch silently returns `None`.

---

## Picking a type mechanism

| Mechanism | When |
|---|---|
| `Enum` with `auto()` | Internal identity types where the value doesn't matter |
| `Enum` with string values | Serialized or user-facing values |
| `Literal[...]` | 2–4 values constraining a single dataclass field |
| Constants class | String keys for dict lookup/dispatch |
| Pipe union (`A \| B`) | Sum types at module level |
| `Protocol` | Structural-subtyping interface (add `@runtime_checkable` only if `isinstance`/`issubclass` is needed at runtime) |

### Closed set with new code path on add → `Enum`

```python
class Mode(Enum):
    FAST = auto()
    SAFE = auto()
    DRY_RUN = auto()
```

### Open set extensible by data → `str`

```python
# Shape types in a flat IR — new shapes from config, no new code
@dataclass(frozen=True)
class Item:
    type: str        # "rect", "circle", or anything plugins register
    data: dict[str, Any]
```

### Decision rule

| Question | Answer | Use |
|---|---|---|
| Can a new value be added without changing Python code? | Yes | `str` |
| Adding a new value requires a new code path? | Yes | `Enum` |
| Set defined by external data (config, schema)? | Yes | `str` |
| Set defined by program logic? | Yes | `Enum` |

### Protocol over ABC for interfaces

Use plain `Protocol` for structural subtyping. Add `@runtime_checkable` only when the interface is checked with `isinstance` or `issubclass` at runtime.

```python
# Right (structural subtyping, static-only)
class Handler(Protocol):
    def handle(self, event: Event) -> Result: ...

# Right (runtime check needed)
@runtime_checkable
class Handler(Protocol):
    def handle(self, event: Event) -> Result: ...

# Wrong (forces inheritance coupling unless shared implementation is needed)
class Handler(ABC):
    @abstractmethod
    def handle(self, event: Event) -> Result: ...
```

---

## Designing a function signature

### At most 3 positional parameters; group the rest in a frozen params dataclass

```python
# Right
@dataclass(frozen=True)
class GridParams:
    width_mm: float
    height_mm: float
    depth_mm: float
    spacing_mm: float
    offset_mm: float = 0.0
    angle_deg: float = 0.0

def generate(domain: Domain, params: GridParams) -> tuple[Item, ...]: ...

# Wrong
def generate(width, height, depth, spacing, offset, angle): ...
```

### Keyword-only for flags

```python
def generate(
    domain: Domain,
    params: GridParams,
    *,
    allow_empty: bool = False,
) -> tuple[Item, ...]: ...
```

### Guard clauses at entry; happy path unindented

```python
# Right
def process(items: tuple[Item, ...], config: Config) -> tuple[Result, ...]:
    if not items:
        return ()
    if not config.is_valid():
        raise ValueError(f"Config: must be valid, got {config}")
    return tuple(handle(item) for item in items)

# Wrong (nested conditionals, real work indented 3 levels)
def process(items, config):
    if items:
        if config.is_valid():
            for item in items:
                ...
```

### Normalize inputs at entry, before branching

```python
# Right
def handle_shape(shape_type: str, data: dict) -> Output:
    shape_type = shape_type.lower().strip()
    handler = HANDLERS.get(shape_type)
    ...
```

---

## Naming things

### Use the canonical verb at layer boundaries

| Verb | Meaning | Example |
|---|---|---|
| `parse_*` | String → structured data | `parse_config` |
| `format_*` | Structured data → string | `format_report` |
| `resolve_*` | Simplify, expand references | `resolve_layout` |
| `*_to_*` | Convert between typed reps | `ast_to_ir` |
| `validate_*` | Check, raise on failure | `validate_config` |
| `build_*` | Construct from parts | `build_pipeline` |
| `load_*` | Read from disk/external | `load_config` |
| `write_*` | Emit machine/file output | `write_output` |
| `render_*` | Emit visual output | `render_diagram` |
| `expand_*` | Parameterized instantiation | `expand_template` |

### Private helpers: underscore prefix, same verb conventions

| Pattern | Purpose |
|---|---|
| `_handle_*` | Dispatch target for a case |
| `_build_*` | Internal construction helper |
| `_validate_*` | Internal check |
| `_collect_*` / `_count_*` | Aggregation |
| `_is_*` / `_has_*` | Boolean predicate |

### Names must be true when read cold

A function called `validate_and_save` must validate *and* save. A `_legacy_` prefix on an actively-used helper is a lie. Rename when behavior changes; don't keep stale names "for compatibility."

**Failure mode:** an agent reads the name, doesn't read the body, propagates the lie.

### Public surface is contract; private surface is sketch

If a name lacks the underscore prefix, anything in the codebase will reach for it. The `_` prefix is the only signal that something is internal. Use it.

---

## Validating data

### Validate at construction with `__post_init__`

```python
@dataclass(frozen=True)
class Box:
    width_mm: float
    height_mm: float

    def __post_init__(self):
        if self.width_mm <= 0:
            raise ValueError(f"Box: width_mm must be > 0, got {self.width_mm}")
        if self.height_mm <= 0:
            raise ValueError(f"Box: height_mm must be > 0, got {self.height_mm}")
```

### Validate at system boundaries; trust internal data

User input, file parsing, API responses, database reads → validate. Internal code → trust.

### Emit an audit summary when processing constraints

When the system honors, ignores, or skips constraints, output a summary listing each. Silent partial application is a defect (GL-5).

---

## Logging

### Never `print()` in committed code; use `logging`

```python
# Right
import logging
logger = logging.getLogger(__name__)

def process(items: tuple[Item, ...]) -> tuple[Result, ...]:
    logger.info("Processing %d items", len(items))
    ...

# Wrong
def process(items):
    print(f"Processing {len(items)} items")
    ...
```

### Levels

| Level | When |
|---|---|
| `DEBUG` | Variable values, branches taken — developer detail |
| `INFO` | Progress milestones — operator detail |
| `WARNING` | Unexpected but recoverable (skip, fallback) |
| `ERROR` | Failed but program continues (one item in batch) |
| `CRITICAL` | Cannot continue |

Don't `WARNING` on expected situations. Don't `INFO` per-item.

---

## Parsing nullable numerics

### Never use `or` for numeric or string fields where `0`/`""` are valid

```python
# Right
width = data.get("width_mm")
if width is None:
    width = DEFAULT_WIDTH_MM

# Wrong
width = data.get("width_mm") or DEFAULT_WIDTH_MM  # 0 silently → default
```

```python
# Right
label = data.get("label")
if label is None:
    label = "default"

# Wrong
label = data.get("label") or "default"  # "" silently → "default"
```

**Failure mode:** legitimate falsy values (0, 0.0, "") get silently replaced with defaults.

---

## Serializing data

### `to_dict()` serializes every non-private field

```python
# Right
def to_dict(self):
    return {
        "name": self.name,
        "width_mm": self.width_mm,
        "height_mm": self.height_mm,
    }

# Wrong (silent omission)
def to_dict(self):
    return {
        "name": self.name,
        "width_mm": self.width_mm,
        # height_mm dropped
    }
```

If a field is intentionally omitted, document the omission at the serialization site.

### Round-trip completeness

Every field survives `serialize → deserialize → serialize`. When adding a field, update serializer, deserializer, and round-trip test in the same change.

### Formatter emits non-default fields; parser accepts both forms

The formatter produces the simplest valid representation. The parser accepts the most permissive.

### Round-trip tests assert on semantic equivalence

```python
# Right
assert parse(serialize(model)) == model

# Wrong
assert serialize(parse(input_text)) == input_text  # whitespace, key order
```

---

## Output

### Deterministic and byte-identical for same input

Implements GL-4 (same input, same output).

### Single conversion path per transformation

For any input → output transformation, exactly one code path. Multiple paths diverge.

### Output must be valid per its format spec

Malformed output is a bug here, not the consumer's problem.

### Writes to durable state: idempotent, atomic, durable

Three separable concerns. Pick which apply per write.

- **Idempotent** — running the operation twice produces the same final state as running it once. Required by GL-6.
- **Atomic** — partial state is never visible to readers. Achieved by writing to a temp file in the same directory, then `os.replace()`.
- **Durable** — the write survives a crash or power loss. Requires `fsync()` on the file (and the containing directory on POSIX).

```python
# Right (idempotent + atomic + durable)
def write_output(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    dir_fd = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)

# Right (idempotent + atomic, no durability requirement)
def write_output(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)

# Wrong (mid-crash leaves a partial file at the destination)
def write_output(path: Path, data: bytes) -> None:
    with path.open("wb") as f:
        f.write(data)
```

Use `os.replace()`, not `Path.rename()` — `os.replace()` is atomic across platforms; `rename()` raises on Windows if the destination exists.

---

## Writing tests

### Test the contract, not the implementation

Agents refactoring code preserve what tests pin and freely change what they don't. Pin behavior; the implementation is what gets rewritten.

### Test at the right level — usually the IR, not the full pipeline

```python
# Right
model = parse_and_validate(input)
assert model.items[0].width_mm == 100

# Wrong
output = full_pipeline(input)
assert "expected_string" in output
```

### Don't test what Python guarantees

```python
# Wrong (tests @dataclass, not project code)
def test_frozen():
    spec = Config(value=10)
    with pytest.raises(FrozenInstanceError):
        spec.value = 20

def test_replace():
    modified = replace(Config(value=10), value=20)
    assert modified.value == 20
```

Test construction only when `__post_init__` validation exists.

### Round-trip on semantics, not syntax

```python
# Right
assert parse(serialize(model)) == model

# Wrong
assert serialize(parse(text)) == text
```

### No duplicate coverage

Before adding a test file, check whether existing tests cover the same code paths.

### Use the framework

No `if __name__ == "__main__"` runners, no `print("PASS")`, no `return True` from test functions, no `sys.path` manipulation. pytest collects.

---

## Comments

### Encode why, never what

A comment is for non-obvious context: a hidden constraint, a workaround for a specific bug, behavior that would surprise a reader.

### Never name current state

```python
# Wrong (rots)
# TODO: refactor this
# Used by the import flow added for issue #42
# Old behavior; new behavior in process_v2

# Right (no comment needed; the code says what it does)
```

### Never comment on what code does when names already say it

If you need a comment to explain what the code does, rename until you don't.

---

## Dead code

Don't leave commented-out code, unused imports, backward-compat shims for removed features, or `# removed` markers. Delete unused code; version control remembers.

---

## Safety-critical constraints

When violation causes real harm (data loss, hardware damage, security breach):

- **Hard error on violation** — never warn-and-continue
- **Post-execution verification** — check the output respects the constraint; don't trust the generation logic
- **Cited in invariants** — mark the safety level explicitly

---

## Cross-reference: invariants implemented

| Invariant | Sections that implement it |
|---|---|
| GL-1 (pipelines do not re-enter or escape scope) | Compiler-pattern conventions (`conventions/pattern/compiler/python.md`) |
| GL-2 (non-deterministic output carries provenance) | (project-layer; not codified here) |
| GL-3 (data is immutable by default) | Declaring a dataclass, Modifying a frozen dataclass |
| GL-4 (same input, same output) | Writing a function that transforms data, Output |
| GL-5 (failures carry context) | Raising an error, Validating data; per-layer rules in batch-pipeline conventions (`conventions/pattern/batch-pipeline/python.md`) |
| GL-6 (writes to durable state are idempotent) | Output |

## Pattern and domain extensions

| File | When it applies |
|---|---|
| `conventions/pattern/compiler/python.md` | Project declares the Compiler pattern |
| `conventions/pattern/batch-pipeline/python.md` | Project's pipeline tolerates per-item failures and reports them |
| `conventions/domain/cad-cam/python.md` | Project has geometry, units, or hardware output |
