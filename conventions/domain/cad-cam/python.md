---
layer: domain
domain: cad-cam
language: python
status: provisional
---

# CAD/CAM domain — Python conventions

Conventions for projects with geometry, units, hardware output, or other spatial concerns.

**Status:** the "domain" axis is provisional. This file holds content that is clearly not global (only applies to spatial-output projects) but is also not architectural-pattern shaped (it cuts across patterns: a Compiler producing CAM output and an ML system producing toolpaths both want these rules).

Examples in the registry: mill_ui, image-forge.

---

## Coordinate and unit discipline

### One unit system, no internal conversions

```python
# Right
width_mm = 101.6

# Wrong
width_inches = 4.0
width_mm = width_inches * 25.4
```

If external input uses different units, convert at the boundary; never internally.

### Document coordinate spaces; transform at boundaries

```python
# Right
item_x = offset                # working-area space (internal)
export_x = MARGIN_MM + item_x  # transform once at export

# Wrong
item_x = MARGIN_MM + offset    # margin applied internally
export_x = MARGIN_MM + item_x  # double margin at export
```

**Failure mode:** the same transform applied twice silently corrupts geometry.
