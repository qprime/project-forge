---
layer: pattern
pattern: compiler
language: python
---

# Compiler pattern — Python conventions

Conventions for projects declaring the Compiler pattern. Extends the global Python coding guidelines in `baseline/coding_guidelines.md`.

The Compiler pattern: input AST → IR → output codegen, with the IR as the single canonical intermediate form.

---

## Pipeline architecture

### Strict layer separation

Implements GL-1 (pipelines do not re-enter or escape scope).

```python
# Right
model = parse(raw_input)
validated = validate(model)
output = render(validated)

# Wrong (skipped validation)
def build_and_export(raw_input):
    model = parse(raw_input)
    output = render(model)
    return model
```

### Use an explicit IR as the validation checkpoint

The IR describes *what*, not *how*. Validation happens once. Tests target the IR, not the full pipeline.

### No pass-through of computed data through semantic layers

```python
# Right (semantic layer stays clean)
@dataclass(frozen=True)
class Feature:
    name: str
    position: float

def feature_to_backend(feature: Feature) -> BackendInput:
    offset = compute_offset(feature.position)
    return BackendInput(offset=offset)

# Wrong (implementation detail leaks into semantic)
@dataclass(frozen=True)
class Feature:
    name: str
    computed_offset: float
```

---

## Dependency direction

### Imports flow downward

```
Input/CLI → Parser → IR/Model → Validation → Backend/Output
```

Lower layers must not import from higher layers. Removing a higher layer must not break lower modules' imports.

### Adapter pattern at boundaries

```python
# Right (adapter at boundary)
# model.py
@dataclass(frozen=True)
class Feature:
    style: str  # generic

# adapter.py
from model import Feature
from renderer.types import RenderHint

def feature_to_render_hint(feature: Feature) -> RenderHint:
    return STYLE_MAP[feature.style]

# Wrong (model depends on renderer)
# model.py
from renderer.types import RenderHint

@dataclass(frozen=True)
class Feature:
    render_hint: RenderHint
```
