from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import yaml
from jsonschema import Draft202012Validator

SCHEMA_VERSION = 1
DESCRIPTION_MAX_CHARS = 280
BASELINE_VERSION_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PYTHON_VERSION_RE = re.compile(r"^\d+\.\d+$")


class ManifestError(ValueError):
    """Raised when a manifest fails to load or validate."""


@dataclass(frozen=True)
class SecondaryPattern:
    name: str
    scope: str


@dataclass(frozen=True)
class Toolchain:
    test: str | None = None
    lint: str | None = None
    type_check: str | None = None


@dataclass(frozen=True)
class DeclarativeArtifactAxis:
    format: str | None = None
    authorship: str | None = None
    mutability: str | None = None


@dataclass(frozen=True)
class VerificationAxis:
    position: str | None = None
    consequence: str | None = None


@dataclass(frozen=True)
class Axes:
    intent_translation: str | None = None
    declarative_artifact: DeclarativeArtifactAxis = field(default_factory=DeclarativeArtifactAxis)
    verification: VerificationAxis = field(default_factory=VerificationAxis)
    state: str | None = None
    contract_surface: str | None = None


@dataclass(frozen=True)
class ProjectContext:
    description: str
    vocabulary: tuple[str, ...] = ()
    load_bearing_subsystems: tuple[str, ...] = ()
    invariant_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class Resolution:
    baseline_version: str
    skills_dir: str
    invariants_dir: str
    conventions_dir: str


@dataclass(frozen=True)
class SkillCustomization:
    slots: Mapping[str, str]
    inserts: Mapping[str, str]


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    primary_pattern: str
    secondary_patterns: tuple[SecondaryPattern, ...]
    domains: tuple[str, ...]
    language: str
    python_version: str | None
    toolchain: Toolchain
    axes: Axes
    project_context: ProjectContext
    resolution: Resolution
    customizations: Mapping[str, SkillCustomization]
    source_path: Path
    project_root: Path


def load_manifest(
    manifest_path: str | Path,
    *,
    baseline_root: str | Path,
    project_root: str | Path | None = None,
) -> Manifest:
    """Load a manifest from disk and validate it.

    The loader is registry-unaware: callers pass the manifest path directly. The
    baseline root is the directory holding `skills/pattern/`, `conventions/`, and
    `invariants/` — used for pattern and domain registration checks.
    """
    manifest_path = Path(manifest_path)
    baseline_root = Path(baseline_root)
    if project_root is None:
        if manifest_path.parent.name != ".forge":
            raise ManifestError(
                f"manifest path must live under <project>/.forge/manifest.yaml; "
                f"got {manifest_path}"
            )
        project_root = manifest_path.parent.parent
    project_root = Path(project_root)

    if not manifest_path.exists():
        raise ManifestError(f"manifest not found at {manifest_path}")

    try:
        raw_text = manifest_path.read_text(encoding="utf-8")
        raw = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ManifestError(f"manifest YAML parse error: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestError(
            f"manifest must be a YAML mapping at top level; got {type(raw).__name__}"
        )

    _validate_schema(raw)
    _validate_semantics(raw, baseline_root=baseline_root, project_root=project_root)

    return _build_manifest(raw, source_path=manifest_path, project_root=project_root)


def _validate_schema(raw: dict) -> None:
    schema = json.loads(files("forge").joinpath("manifest.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(raw), key=lambda e: e.path)
    if not errors:
        return
    err = errors[0]
    path = ".".join(str(p) for p in err.absolute_path) or "<root>"
    if err.validator == "additionalProperties":
        bad = ", ".join(sorted(err.message.split("'")[1::2]))
        raise ManifestError(f"unknown top-level key: {bad}" if path == "<root>" else f"{path}: {err.message}")
    if err.validator == "required":
        missing = err.message.split("'")[1]
        if path == "<root>":
            if missing == "schema_version":
                raise ManifestError("schema_version required")
            if missing == "patterns":
                raise ManifestError("patterns required")
            if missing == "language":
                raise ManifestError("language required")
            if missing == "project_context":
                raise ManifestError("project_context required")
            if missing == "resolution":
                raise ManifestError("resolution required")
        if path.startswith("resolution"):
            raise ManifestError(f"resolution.{missing} required")
        if path.startswith("project_context"):
            raise ManifestError(f"project_context.{missing} required")
        if path == "patterns":
            raise ManifestError("patterns.primary required")
        raise ManifestError(f"{path}: {missing} required")
    if err.validator == "const" and path == "schema_version":
        raise ManifestError(
            f"unsupported schema_version: {raw.get('schema_version')!r}; supported: [{SCHEMA_VERSION}]"
        )
    if err.validator == "maxLength" and path == "project_context.description":
        raise ManifestError(
            f"project_context.description: must be ≤ {DESCRIPTION_MAX_CHARS} chars, "
            f"got {len(raw['project_context']['description'])}"
        )
    if err.validator == "pattern":
        if path == "resolution.baseline_version":
            raise ManifestError(f"invalid baseline_version: {raw['resolution']['baseline_version']!r}")
        if path == "python_version":
            raise ManifestError(f"invalid python_version: {raw['python_version']!r}")
    raise ManifestError(f"{path}: {err.message}")


def _validate_semantics(raw: dict, *, baseline_root: Path, project_root: Path) -> None:
    if raw.get("language") == "python" and "python_version" not in raw:
        raise ManifestError("python_version required when language is python")

    registered_patterns = _registered_patterns(baseline_root)
    primary = raw["patterns"]["primary"]
    if primary not in registered_patterns:
        raise ManifestError(
            f"unknown pattern: {primary!r}; valid: {sorted(registered_patterns)}"
        )

    for entry in raw["patterns"].get("secondary", []) or []:
        if entry["name"] not in registered_patterns:
            raise ManifestError(
                f"unknown pattern: {entry['name']!r}; valid: {sorted(registered_patterns)}"
            )
        scope = entry["scope"]
        _validate_relative_path(scope, label="scope")
        scope_path = (project_root / scope).resolve()
        if not scope_path.is_dir():
            raise ManifestError(f"scope not found: {scope}")
        try:
            scope_path.relative_to(project_root.resolve())
        except ValueError as exc:
            raise ManifestError("scope: path traversal not allowed") from exc

    domain_root = baseline_root / "conventions" / "domain"
    valid_domains = (
        {p.name for p in domain_root.iterdir() if p.is_dir()} if domain_root.is_dir() else set()
    )
    for domain in raw.get("domains") or []:
        if domain not in valid_domains:
            raise ManifestError(
                f"unknown domain: {domain!r}; valid: {sorted(valid_domains)}"
            )

    for key in ("skills_dir", "invariants_dir", "conventions_dir"):
        _validate_relative_path(raw["resolution"][key], label=f"resolution.{key}")

    customizations = raw.get("customizations") or {}
    if customizations:
        global_skills_dir = baseline_root / "skills" / "global"
        valid_skills = (
            {p.stem for p in global_skills_dir.glob("*.md") if "." not in p.stem}
            if global_skills_dir.is_dir()
            else set()
        )
        for skill_name in customizations:
            if skill_name not in valid_skills:
                raise ManifestError(
                    f"unknown skill in customizations: {skill_name!r}; "
                    f"valid: {sorted(valid_skills)}"
                )

    if raw.get("language") != "python":
        warnings.warn(
            f"language {raw.get('language')!r} has no baseline toolchain content",
            stacklevel=3,
        )


def _registered_patterns(baseline_root: Path) -> set[str]:
    names: set[str] = set()
    for sub in ("skills/pattern", "conventions/pattern", "invariants/pattern"):
        d = baseline_root / sub
        if not d.is_dir():
            continue
        for child in d.iterdir():
            if child.is_dir():
                names.add(child.name)
            elif child.suffix == ".md":
                names.add(child.stem)
    return names


def _validate_relative_path(value: str, *, label: str) -> None:
    if Path(value).is_absolute() or value.startswith("~"):
        raise ManifestError(f"{label}: must be relative path")
    if ".." in Path(value).parts:
        raise ManifestError(f"{label}: path traversal not allowed")


def _build_manifest(raw: dict, *, source_path: Path, project_root: Path) -> Manifest:
    secondary = tuple(
        SecondaryPattern(name=e["name"], scope=e["scope"])
        for e in (raw["patterns"].get("secondary") or [])
    )
    tc = raw.get("toolchain") or {}
    toolchain = Toolchain(
        test=tc.get("test"),
        lint=tc.get("lint"),
        type_check=tc.get("type_check"),
    )
    ax = raw.get("axes") or {}
    axes = Axes(
        intent_translation=ax.get("intent_translation"),
        declarative_artifact=DeclarativeArtifactAxis(**(ax.get("declarative_artifact") or {})),
        verification=VerificationAxis(**(ax.get("verification") or {})),
        state=ax.get("state"),
        contract_surface=ax.get("contract_surface"),
    )
    pc = raw["project_context"]
    project_context = ProjectContext(
        description=pc["description"],
        vocabulary=tuple(pc.get("vocabulary") or ()),
        load_bearing_subsystems=tuple(pc.get("load_bearing_subsystems") or ()),
        invariant_sources=tuple(pc.get("invariant_sources") or ()),
    )
    res = raw["resolution"]
    resolution = Resolution(
        baseline_version=res["baseline_version"],
        skills_dir=res["skills_dir"],
        invariants_dir=res["invariants_dir"],
        conventions_dir=res["conventions_dir"],
    )
    customizations: dict[str, SkillCustomization] = {}
    for skill_name, body in (raw.get("customizations") or {}).items():
        slots = {
            k: norm
            for k, v in (body.get("slots") or {}).items()
            if (norm := _normalize_block(v)) != ""
        }
        inserts = {
            k: norm
            for k, v in (body.get("inserts") or {}).items()
            if (norm := _normalize_block(v)) != ""
        }
        customizations[skill_name] = SkillCustomization(
            slots=MappingProxyType(slots),
            inserts=MappingProxyType(inserts),
        )
    customizations_view = MappingProxyType(customizations)
    return Manifest(
        schema_version=raw["schema_version"],
        primary_pattern=raw["patterns"]["primary"],
        secondary_patterns=secondary,
        domains=tuple(raw.get("domains") or ()),
        language=raw["language"],
        python_version=raw.get("python_version"),
        toolchain=toolchain,
        axes=axes,
        project_context=project_context,
        resolution=resolution,
        customizations=customizations_view,
        source_path=source_path.resolve(),
        project_root=project_root.resolve(),
    )


def _normalize_block(body: str) -> str:
    body = body.lstrip("\n")
    body = body.rstrip()
    if body == "":
        return ""
    return body + "\n"
