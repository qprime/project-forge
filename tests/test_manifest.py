from __future__ import annotations

import warnings
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from forge.manifest import (
    Manifest,
    ManifestError,
    load_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_MANIFEST = REPO_ROOT / "tests" / "fixtures" / "sample_project" / ".forge" / "manifest.yaml"


VALID_MINIMAL = {
    "schema_version": 1,
    "patterns": {"primary": "compiler"},
    "language": "python",
    "python_version": "3.12",
    "project_context": {"description": "A short project description."},
    "resolution": {
        "baseline_version": "2026-04-27",
        "commands_dir": ".claude/commands/",
        "invariants_dir": "docs/invariants/",
        "conventions_dir": "docs/conventions/",
    },
}


@pytest.fixture
def baseline_root(tmp_path: Path) -> Path:
    """A minimal baseline tree with a single registered pattern (`compiler`)
    and a registered domain (`cad-cam`)."""
    (tmp_path / "commands" / "pattern" / "compiler").mkdir(parents=True)
    (tmp_path / "commands" / "pattern" / "compiler" / ".gitkeep").touch()
    (tmp_path / "conventions" / "domain" / "cad-cam").mkdir(parents=True)
    (tmp_path / "conventions" / "domain" / "cad-cam" / ".gitkeep").touch()
    return tmp_path


@pytest.fixture
def project_tree(tmp_path: Path) -> Path:
    """A project working tree with a `.forge/` directory."""
    project = tmp_path / "myproject"
    (project / ".forge").mkdir(parents=True)
    (project / "src" / "processing").mkdir(parents=True)
    return project


def write_manifest(project: Path, payload: dict) -> Path:
    path = project / ".forge" / "manifest.yaml"
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Sample project: the canonical end-to-end manifest must load against the
# baseline (forge's `commands/global/` and `commands/pattern/`).
# ---------------------------------------------------------------------------


def test_sample_manifest_loads():
    m = load_manifest(SAMPLE_MANIFEST, baseline_root=REPO_ROOT)
    assert isinstance(m, Manifest)
    assert m.schema_version == 1
    assert m.primary_pattern == "compiler"
    assert m.language == "python"
    assert m.python_version == "3.12"


def test_manifest_is_frozen():
    m = load_manifest(SAMPLE_MANIFEST, baseline_root=REPO_ROOT)
    with pytest.raises(Exception):
        m.primary_pattern = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# File presence and shape
# ---------------------------------------------------------------------------


def test_missing_file(baseline_root, project_tree):
    missing = project_tree / ".forge" / "manifest.yaml"
    with pytest.raises(ManifestError, match="manifest not found"):
        load_manifest(missing, baseline_root=baseline_root)


def test_yaml_parse_error(baseline_root, project_tree):
    path = project_tree / ".forge" / "manifest.yaml"
    path.write_text(":\n  - bad: : :\n", encoding="utf-8")
    with pytest.raises(ManifestError, match="YAML parse error"):
        load_manifest(path, baseline_root=baseline_root)


def test_top_level_must_be_mapping(baseline_root, project_tree):
    path = project_tree / ".forge" / "manifest.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ManifestError, match="must be a YAML mapping"):
        load_manifest(path, baseline_root=baseline_root)


def test_unknown_top_level_key(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "totally_made_up": True}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unknown top-level key|totally_made_up"):
        load_manifest(path, baseline_root=baseline_root)


def test_manifest_path_must_be_in_dot_forge(baseline_root, tmp_path):
    elsewhere = tmp_path / "manifest.yaml"
    elsewhere.write_text(yaml.safe_dump(VALID_MINIMAL), encoding="utf-8")
    with pytest.raises(ManifestError, match=r"\.forge/manifest\.yaml"):
        load_manifest(elsewhere, baseline_root=baseline_root)


# ---------------------------------------------------------------------------
# schema_version
# ---------------------------------------------------------------------------


def test_unsupported_schema_version(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "schema_version": 99}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unsupported schema_version"):
        load_manifest(path, baseline_root=baseline_root)


# ---------------------------------------------------------------------------
# patterns.primary
# ---------------------------------------------------------------------------


def test_unknown_primary_pattern(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "patterns": {"primary": "no-such-pattern"}}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unknown pattern: 'no-such-pattern'"):
        load_manifest(path, baseline_root=baseline_root)


def test_primary_registered_via_invariants_dir(baseline_root, project_tree):
    """A pattern is registered if it appears in any of the three layers."""
    (baseline_root / "invariants" / "pattern").mkdir(parents=True, exist_ok=True)
    (baseline_root / "invariants" / "pattern" / "compiler.md").write_text("# pattern\n")
    payload = {**VALID_MINIMAL, "patterns": {"primary": "compiler"}}
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_root)
    assert m.primary_pattern == "compiler"


# ---------------------------------------------------------------------------
# patterns.secondary
# ---------------------------------------------------------------------------


def test_secondary_unknown_name(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "phantom", "scope": "src/processing/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unknown pattern: 'phantom'"):
        load_manifest(path, baseline_root=baseline_root)


def test_secondary_scope_missing(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "compiler", "scope": "src/nonexistent/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="scope not found"):
        load_manifest(path, baseline_root=baseline_root)


def test_secondary_scope_absolute_rejected(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "compiler", "scope": "/etc/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"scope: must be relative path"):
        load_manifest(path, baseline_root=baseline_root)


def test_secondary_scope_traversal_rejected(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "compiler", "scope": "../escape/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"scope: path traversal not allowed"):
        load_manifest(path, baseline_root=baseline_root)


def test_secondary_scope_tilde_rejected(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "compiler", "scope": "~/escape/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"scope: must be relative path"):
        load_manifest(path, baseline_root=baseline_root)


def test_secondary_scope_resolves(baseline_root, project_tree):
    payload = {
        **VALID_MINIMAL,
        "patterns": {
            "primary": "compiler",
            "secondary": [{"name": "compiler", "scope": "src/processing/"}],
        },
    }
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_root)
    assert m.secondary_patterns[0].scope == "src/processing/"


# ---------------------------------------------------------------------------
# domains
# ---------------------------------------------------------------------------


def test_unknown_domain(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "domains": ["nope"]}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unknown domain: 'nope'"):
        load_manifest(path, baseline_root=baseline_root)


def test_known_domain_loads(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "domains": ["cad-cam"]}
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_root)
    assert m.domains == ("cad-cam",)


# ---------------------------------------------------------------------------
# language / python_version
# ---------------------------------------------------------------------------


def test_python_requires_python_version(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "python_version": None}
    payload.pop("python_version")
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="python_version required"):
        load_manifest(path, baseline_root=baseline_root)


def test_invalid_python_version(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "python_version": "three.twelve"}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="invalid python_version"):
        load_manifest(path, baseline_root=baseline_root)


def test_non_python_language_warns(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "language": "rust"}
    payload.pop("python_version")
    path = write_manifest(project_tree, payload)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        m = load_manifest(path, baseline_root=baseline_root)
    assert m.language == "rust"
    assert any("rust" in str(w.message) for w in caught)


# ---------------------------------------------------------------------------
# resolution.*_dir
# ---------------------------------------------------------------------------


def test_resolution_commands_dir_required(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "resolution": {**payload["resolution"]}}
    payload["resolution"].pop("commands_dir")
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="resolution.commands_dir required"):
        load_manifest(path, baseline_root=baseline_root)


def test_resolution_dir_absolute_rejected(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "resolution": {**payload["resolution"], "commands_dir": "/abs/path"}}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"resolution\.commands_dir: must be relative path"):
        load_manifest(path, baseline_root=baseline_root)


def test_resolution_dir_traversal_rejected(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "resolution": {**payload["resolution"], "invariants_dir": "../etc/"}}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"resolution\.invariants_dir: path traversal not allowed"):
        load_manifest(path, baseline_root=baseline_root)


def test_resolution_dir_tilde_rejected(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "resolution": {**payload["resolution"], "conventions_dir": "~/conventions/"}}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"resolution\.conventions_dir: must be relative path"):
        load_manifest(path, baseline_root=baseline_root)


def test_invalid_baseline_version(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {**payload, "resolution": {**payload["resolution"], "baseline_version": "April 27"}}
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="invalid baseline_version"):
        load_manifest(path, baseline_root=baseline_root)


# ---------------------------------------------------------------------------
# project_context.description
# ---------------------------------------------------------------------------


def test_description_too_long(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    payload = {
        **payload,
        "project_context": {**payload["project_context"], "description": "x" * 281},
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match=r"must be ≤ 280 chars, got 281"):
        load_manifest(path, baseline_root=baseline_root)


# ---------------------------------------------------------------------------
# Toolchain normalization
# ---------------------------------------------------------------------------


def test_toolchain_missing_keys_normalize_to_none(baseline_root, project_tree):
    payload = {**VALID_MINIMAL, "toolchain": {"test": "pytest"}}
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_root)
    assert m.toolchain.test == "pytest"
    assert m.toolchain.lint is None
    assert m.toolchain.type_check is None


def test_toolchain_omitted_normalizes(baseline_root, project_tree):
    payload = {**VALID_MINIMAL}
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_root)
    assert m.toolchain.test is None
    assert m.toolchain.lint is None
    assert m.toolchain.type_check is None


# ---------------------------------------------------------------------------
# customizations
# ---------------------------------------------------------------------------


@pytest.fixture
def baseline_with_global_commands(baseline_root: Path) -> Path:
    """baseline_root with a single global command registered (`mini`)."""
    (baseline_root / "commands" / "global").mkdir(parents=True, exist_ok=True)
    (baseline_root / "commands" / "global" / "mini.md").write_text(
        "# Mini\n\n{{X=default}}\n\n<!-- insert: items -->\n",
        encoding="utf-8",
    )
    return baseline_root


def test_customizations_optional(baseline_with_global_commands, project_tree):
    """A manifest without `customizations` loads cleanly; the field is an
    empty dict on the resulting Manifest."""
    payload = {**VALID_MINIMAL}
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_with_global_commands)
    assert m.customizations == {}


def test_customizations_loads_slots_and_inserts(
    baseline_with_global_commands, project_tree
):
    payload = {
        **VALID_MINIMAL,
        "customizations": {
            "mini": {
                "slots": {"X": "from-project"},
                "inserts": {"items": "- one\n- two\n"},
            }
        },
    }
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_with_global_commands)
    assert "mini" in m.customizations
    assert m.customizations["mini"].slots == {"X": "from-project\n"}
    assert m.customizations["mini"].inserts == {"items": "- one\n- two\n"}


def test_customizations_unknown_skill_key_rejected(
    baseline_with_global_commands, project_tree
):
    """A typo in a skill name fails _validate_semantics — not the schema."""
    payload = {
        **VALID_MINIMAL,
        "customizations": {"mni": {"slots": {"X": "v"}}},
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError, match="unknown command in customizations: 'mni'"):
        load_manifest(path, baseline_root=baseline_with_global_commands)


def test_customizations_unknown_subkey_rejected(
    baseline_with_global_commands, project_tree
):
    """`additionalProperties: false` enforced at the slots/inserts structural level."""
    payload = {
        **VALID_MINIMAL,
        "customizations": {"mini": {"not_a_field": {"X": "v"}}},
    }
    path = write_manifest(project_tree, payload)
    with pytest.raises(ManifestError):
        load_manifest(path, baseline_root=baseline_with_global_commands)


def test_customizations_normalizes_trailing_newline(
    baseline_with_global_commands, project_tree
):
    """YAML `|` block scalars and plain scalars both produce values with a
    single trailing newline after _normalize_block — same shape the contribution
    parser produced."""
    payload_yaml = (
        "schema_version: 1\n"
        "patterns:\n  primary: compiler\n"
        "language: python\n"
        "python_version: \"3.12\"\n"
        "project_context:\n  description: synthetic\n"
        "resolution:\n"
        "  baseline_version: \"2026-04-27\"\n"
        "  commands_dir: .claude/commands/\n"
        "  invariants_dir: docs/invariants/\n"
        "  conventions_dir: docs/conventions/\n"
        "customizations:\n"
        "  mini:\n"
        "    slots:\n"
        "      X: plain-scalar\n"
        "    inserts:\n"
        "      items: |\n"
        "        - a\n"
        "        - b\n"
    )
    path = project_tree / ".forge" / "manifest.yaml"
    path.write_text(payload_yaml, encoding="utf-8")
    m = load_manifest(path, baseline_root=baseline_with_global_commands)
    assert m.customizations["mini"].slots["X"] == "plain-scalar\n"
    assert m.customizations["mini"].inserts["items"] == "- a\n- b\n"


def test_customizations_are_immutable(
    baseline_with_global_commands, project_tree
):
    """`SkillCustomization` is `frozen=True`, but the slot/insert mappings
    must also be immutable so the frozen claim is honest end-to-end. Without
    this, `m.customizations[name].slots[key] = ...` succeeds silently."""
    payload = {
        **VALID_MINIMAL,
        "customizations": {"mini": {"slots": {"X": "v"}}},
    }
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_with_global_commands)
    with pytest.raises(TypeError):
        m.customizations["mini"].slots["X"] = "tampered"  # type: ignore[index]
    with pytest.raises(TypeError):
        m.customizations["new"] = m.customizations["mini"]  # type: ignore[index]


def test_customizations_empty_body_filtered(
    baseline_with_global_commands, project_tree
):
    """An empty body in customizations is filtered at load time, mirroring the
    parser's `if body == "": continue` so empty falls through to the pattern
    layer at resolve time."""
    payload = {
        **VALID_MINIMAL,
        "customizations": {"mini": {"slots": {"X": "\n"}}},
    }
    path = write_manifest(project_tree, payload)
    m = load_manifest(path, baseline_root=baseline_with_global_commands)
    assert m.customizations["mini"].slots == {}
