from __future__ import annotations

import warnings
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from forge.manifest import Manifest, load_manifest
from forge.resolver import (
    ResolverError,
    _compose_skill,
    _parse_contribution,
    _read_text,
    resolve,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FORGE_MANIFEST = REPO_ROOT / ".forge" / "manifest.yaml"


# ---------------------------------------------------------------------------
# Synthetic baseline / project builders
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).lstrip("\n"), encoding="utf-8")
    return path


def _build_baseline(
    root: Path,
    *,
    skill_template: str = "# Tinyskill\n\nValue: {{X=ok}}\n",
    pattern: str = "tiny",
    pattern_skill: str | None = None,
    invariants_global: str | None = "## GL-1 — Foo\n\nrule\n",
    invariants_pattern: str | None = None,
    invariants_domain: dict[str, str] | None = None,
    conventions_global: str | None = "# Global conventions\n",
    conventions_pattern: dict[str, str] | None = None,
    conventions_domain: dict[str, dict[str, str]] | None = None,
    extra_global_skills: dict[str, str] | None = None,
) -> Path:
    _write(root / "skills" / "global" / "tinyskill.md", skill_template)
    if extra_global_skills:
        for name, body in extra_global_skills.items():
            _write(root / "skills" / "global" / f"{name}.md", body)
    (root / "skills" / "pattern" / pattern).mkdir(parents=True, exist_ok=True)
    if pattern_skill is not None:
        _write(root / "skills" / "pattern" / pattern / "tinyskill.md", pattern_skill)
    (root / "conventions" / "domain").mkdir(parents=True, exist_ok=True)
    (root / "conventions" / "pattern" / pattern).mkdir(parents=True, exist_ok=True)
    if invariants_global is not None:
        _write(root / "invariants" / "global.md", invariants_global)
    if invariants_pattern is not None:
        _write(root / "invariants" / "pattern" / f"{pattern}.md", invariants_pattern)
    for domain, body in (invariants_domain or {}).items():
        _write(root / "invariants" / "domain" / f"{domain}.md", body)
        (root / "conventions" / "domain" / domain).mkdir(parents=True, exist_ok=True)
    if conventions_global is not None:
        _write(root / "baseline" / "coding_guidelines.md", conventions_global)
    for lang, body in (conventions_pattern or {}).items():
        _write(root / "conventions" / "pattern" / pattern / f"{lang}.md", body)
    for domain, langs in (conventions_domain or {}).items():
        (root / "conventions" / "domain" / domain).mkdir(parents=True, exist_ok=True)
        for lang, body in langs.items():
            _write(root / "conventions" / "domain" / domain / f"{lang}.md", body)
    return root


def _build_manifest(
    project_root: Path,
    *,
    primary: str = "tiny",
    domains: tuple[str, ...] = (),
    secondaries: tuple[tuple[str, str], ...] = (),
    language: str = "python",
    skills_dir: str = ".claude/commands/",
    invariants_dir: str = "docs/invariants/",
    conventions_dir: str = "docs/conventions/",
) -> Manifest:
    payload = {
        "schema_version": 1,
        "patterns": {
            "primary": primary,
            "secondary": [{"name": n, "scope": s} for n, s in secondaries],
        },
        "domains": list(domains),
        "language": language,
        "python_version": "3.12" if language == "python" else None,
        "project_context": {"description": "synthetic"},
        "resolution": {
            "baseline_version": "2026-04-27",
            "skills_dir": skills_dir,
            "invariants_dir": invariants_dir,
            "conventions_dir": conventions_dir,
        },
    }
    if language != "python":
        payload.pop("python_version")
    (project_root / ".forge").mkdir(parents=True, exist_ok=True)
    manifest_path = project_root / ".forge" / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    for n, s in secondaries:
        (project_root / s).mkdir(parents=True, exist_ok=True)
    return manifest_path


# ---------------------------------------------------------------------------
# Forge dogfood (negative test in v1)
# ---------------------------------------------------------------------------


def test_forge_dogfood_raises_on_unfilled_required_slots():
    """Top-level resolve() raises on the first skill whose template has unfilled
    required slots. Skills are composed in sorted order, so `architect` (with
    `PERSONA_DOMAIN`) is the first to fail."""
    manifest = load_manifest(FORGE_MANIFEST, baseline_root=REPO_ROOT)
    with pytest.raises(ResolverError) as excinfo:
        resolve(manifest, baseline_root=REPO_ROOT, project_root=REPO_ROOT)
    msg = str(excinfo.value)
    assert "slot 'PERSONA_DOMAIN' in architect" in msg
    assert "no layer filled it" in msg


def test_forge_dogfood_unfilled_slots_cover_each_skill():
    """Walk each forge global skill independently and assert that the per-skill
    `ResolverError` names a known unfilled slot. This is stricter than the
    top-level dogfood test: it ensures every skill that should error does, and
    that we know which slot stops each one. When #8 (full slot migration)
    lands, this test should be deleted along with the negative dogfood test."""
    manifest = load_manifest(FORGE_MANIFEST, baseline_root=REPO_ROOT)
    expected_first_slot = {
        "architect": "PERSONA_DOMAIN",
        "engineer": "PROJECT_DESCRIPTION",
        "spec": "ISSUE_TRACKER",
    }
    expected_clean = {"close-out", "debug", "review"}

    global_dir = REPO_ROOT / "skills" / "global"
    pattern_dir = REPO_ROOT / "skills" / "pattern" / manifest.primary_pattern
    project_skills_dir = REPO_ROOT / manifest.resolution.skills_dir

    seen: set[str] = set()
    for skill_path in sorted(global_dir.glob("*.md")):
        name = skill_path.stem
        if "." in name:
            continue
        seen.add(name)
        template = _read_text(skill_path)
        pattern_contrib = _parse_contribution(pattern_dir / f"{name}.md")
        project_contrib = _parse_contribution(project_skills_dir / f"{name}.custom.md")
        if name in expected_clean:
            _compose_skill(name, template, pattern_contrib, project_contrib)
            continue
        with pytest.raises(ResolverError) as excinfo:
            _compose_skill(name, template, pattern_contrib, project_contrib)
        msg = str(excinfo.value)
        assert f"slot '{expected_first_slot[name]}' in {name}" in msg

    assert seen == set(expected_first_slot) | expected_clean


# ---------------------------------------------------------------------------
# Synthetic full-stack composition
# ---------------------------------------------------------------------------


def test_full_stack_global_pattern_project(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template=(
            "# Tinyskill\n\n"
            "Value: {{X}}\n"
            "Default: {{Y=fallback}}\n\n"
            "<!-- insert: bullets -->\n"
        ),
        pattern_skill=(
            "## slot: X\n\nfrom-pattern\n\n"
            "## insert: bullets\n\n- pattern bullet\n"
        ),
    )
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## insert: bullets\n\n- project bullet\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "Value: from-pattern" in skill
    assert "Default: fallback" in skill
    assert "- pattern bullet" in skill
    assert "- project bullet" in skill
    assert "<!-- insert:" not in skill


def test_slot_precedence_project_over_pattern_over_default(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X=template-default}}\n",
        pattern_skill="## slot: X\n\npattern-value\n",
    )
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## slot: X\n\nproject-value\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "project-value" in out.skills["tinyskill"]
    assert "pattern-value" not in out.skills["tinyskill"]
    assert "template-default" not in out.skills["tinyskill"]


def test_slot_pattern_used_when_no_project_layer(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X=template-default}}\n",
        pattern_skill="## slot: X\n\npattern-value\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "pattern-value" in out.skills["tinyskill"]


def test_slot_inline_default_used_when_no_layer(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, skill_template="# T\n\n{{X=the-default}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "the-default" in out.skills["tinyskill"]


def test_insert_ordering_pattern_then_project(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n<!-- insert: items -->\n",
        pattern_skill="## insert: items\n\nP1\n",
    )
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## insert: items\n\nQ1\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert skill.index("P1") < skill.index("Q1")
    between = skill[skill.index("P1") + 2 : skill.index("Q1")]
    assert between == "\n\n"


def test_empty_insert_removes_comment_line(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\nbefore\n<!-- insert: missing -->\nafter\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "<!-- insert:" not in skill
    assert "before\nafter\n" in skill


def test_unknown_placeholder_in_contribution_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X=ok}}\n",
        pattern_skill="## slot: NOT_DEFINED\n\nbogus\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="unknown placeholder 'NOT_DEFINED'"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_required_slot_unfilled_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, skill_template="# T\n\n{{REQUIRED}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="slot 'REQUIRED'"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_empty_slot_body_falls_through_to_pattern(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X}}\n",
        pattern_skill="## slot: X\n\npattern-wins\n",
    )
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## slot: X\n\n\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "pattern-wins" in out.skills["tinyskill"]


def test_invariants_compose_global_pattern_domain_project(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        invariants_global="## GL-1 — Foo\n\nglobal rule\n",
        invariants_pattern="## CP-1 — Pattern\n\npattern rule\n",
        invariants_domain={"cad-cam": "## DM-1 — Domain\n\ndomain rule\n"},
    )
    manifest_path = _build_manifest(project, domains=("cad-cam",))
    _write(
        project / "docs" / "invariants" / "global.md",
        "## PR-1 — Project\n\nproject rule\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    body = out.invariants
    for marker in ("GL-1 — Foo", "CP-1 — Pattern", "DM-1 — Domain", "PR-1 — Project"):
        assert marker in body
    assert body.index("GL-1") < body.index("CP-1")
    assert body.index("CP-1") < body.index("DM-1")
    assert body.index("DM-1") < body.index("PR-1")


def test_invariant_id_collision_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        invariants_global="## GL-1 — Foo\n\nrule\n",
        invariants_pattern="## GL-1 — Bar\n\nrule\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="invariant ID 'GL-1' duplicated"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_conventions_concatenation(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        conventions_global="# global\n",
        conventions_pattern={"python": "# pattern python\n"},
        conventions_domain={"cad-cam": {"python": "# domain cad-cam python\n"}},
    )
    manifest_path = _build_manifest(project, domains=("cad-cam",))
    _write(project / "docs" / "conventions" / "python.md", "# project python\n")
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    body = out.conventions["python"]
    for marker in ("# global", "# pattern python", "# domain cad-cam python", "# project python"):
        assert marker in body
    assert body.index("# global") < body.index("# pattern python")
    assert body.index("# pattern python") < body.index("# domain cad-cam python")
    assert body.index("# domain cad-cam python") < body.index("# project python")


def test_secondary_patterns_warning(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, skill_template="# T\n\n{{X=ok}}\n")
    (baseline / "skills" / "pattern" / "extra").mkdir(parents=True, exist_ok=True)
    (baseline / "conventions" / "pattern" / "extra").mkdir(parents=True, exist_ok=True)
    manifest_path = _build_manifest(
        project, secondaries=(("extra", "src/sub"),)
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolve(manifest, baseline_root=baseline, project_root=project)
    msgs = [str(w.message) for w in caught]
    assert any("resolver v1 does not compose scoped artifacts" in m for m in msgs)


def test_language_with_no_contributions_returns_empty_string(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X=ok}}\n",
        conventions_global=None,
    )
    manifest_path = _build_manifest(project, language="rust")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert out.conventions == {"rust": ""}


def test_skill_enumeration_filters_inner_dot_names(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        skill_template="# T\n\n{{X=ok}}\n",
        extra_global_skills={"architect.notes": "stray notes\n"},
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "tinyskill" in out.skills
    assert "architect.notes" not in out.skills
    assert "architect" not in out.skills


def test_block_boundary_handles_subheadings_and_multiline_bodies(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = (
        "# T\n\n"
        "<!-- insert: section -->\n"
        "{{X}}\n"
    )
    pattern_contrib = (
        "## insert: section\n\n"
        "Top-level paragraph.\n\n"
        "### Sub-heading\n\n"
        "Sub-content with more lines.\n\n"
        "## slot: X\n\n"
        "the-x\n"
    )
    _build_baseline(baseline, skill_template=template, pattern_skill=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "Top-level paragraph." in skill
    assert "### Sub-heading" in skill
    assert "Sub-content with more lines." in skill
    assert "the-x" in skill
    assert "## insert:" not in skill
    assert "## slot:" not in skill


def test_resolved_project_is_frozen(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, skill_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    with pytest.raises(Exception):
        out.skills = {}  # type: ignore[misc]
