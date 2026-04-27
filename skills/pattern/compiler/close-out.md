---
layer: pattern
pattern: compiler
skill: close-out
---

# Compiler pattern — close-out contribution

Fills placeholders in `skills/global/close-out.md` for projects declaring the Compiler pattern.

Note: verification-checks here assumes the project's language/toolchain matches what most Compiler-pattern projects in this registry use. Override at the project layer if the project uses a different toolchain.

---

## insert: verification-checks

1. **Tests:** If `tests/` exists or `pyproject.toml` declares pytest config, run `python -m pytest tests/ -x -q 2>&1 | tail -5`. If neither is present, report "no test suite detected" and proceed.
2. **Lint:** If `ruff.toml` or `[tool.ruff]` in `pyproject.toml`, run `ruff check . 2>&1 | tail -3 && ruff format --check . 2>&1 | tail -3`. If neither, report "no ruff config detected".
3. **Type check:** If `pyrightconfig.json` or `[tool.pyright]` in `pyproject.toml`, run `pyright 2>&1 | tail -5`. Skip if neither.
