from __future__ import annotations

import warnings
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from forge.manifest import Manifest, load_manifest
from forge.resolver import (
    INSERT_RE,
    PLACEHOLDER_RE,
    SLOT_INSERT_HEADER_RE,
    ResolverError,
    _fence_regions,
    _in_fence,
    _is_paragraph_embedded,
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
# Forge dogfood (positive — FG-5 self-bootstrap)
# ---------------------------------------------------------------------------


def _authored_probes(contribution_path: Path) -> list[tuple[str, str, str]]:
    """Read a contribution file and return (kind, name, probe) tuples for each
    declared slot/insert. The probe is the first non-blank line of the body as
    authored — independent of how the resolver parses block boundaries. If the
    composed skill is missing the probe, content was lost during composition."""
    if not contribution_path.is_file():
        return []
    text = contribution_path.read_text(encoding="utf-8")
    fences = _fence_regions(text)
    headers = [
        m for m in SLOT_INSERT_HEADER_RE.finditer(text)
        if not _in_fence(m.start(), fences)
    ]
    out: list[tuple[str, str, str]] = []
    for i, match in enumerate(headers):
        kind, name = match.group(1), match.group(2)
        body_start = match.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end].strip()
        if not body:
            continue
        probe = body.splitlines()[0].strip()
        if probe:
            out.append((kind, name, probe))
    return out


def _paragraph_embedded_slots(template: str) -> list[tuple[str, str | None, str]]:
    """For each paragraph-embedded slot in `template`, return (name, default,
    suffix). Suffix is the literal template text from immediately after the
    placeholder to whichever comes first: end-of-line, the next `{{` (another
    placeholder), or EOF. It is what must directly follow the substituted
    value in correctly composed output for the paragraph to be intact."""
    out: list[tuple[str, str | None, str]] = []
    for match in PLACEHOLDER_RE.finditer(template):
        if not _is_paragraph_embedded(template, match.start(), match.end()):
            continue
        name = match.group(1)
        default = match.group(2)
        end = match.end()
        line_end = template.find("\n", end)
        next_placeholder = template.find("{{", end)
        candidates = [c for c in (line_end, next_placeholder) if c != -1]
        boundary = min(candidates) if candidates else len(template)
        suffix = template[end:boundary]
        out.append((name, default, suffix))
    return out


def test_forge_dogfood_resolves_cleanly():
    """Forge resolves itself cleanly against its own baseline (FG-5).

    The expected skill set is derived from `skills/global/*.md` so adding a
    new global skill without a matching forge contribution surfaces here.
    Every composed skill must be non-empty, contain no leftover slot
    placeholders or insert markers, and contain every authored slot/insert
    body. The body-presence check is what makes the dogfood positive: a
    contribution whose content is silently dropped during composition fails
    here even though the structural checks pass."""
    manifest = load_manifest(FORGE_MANIFEST, baseline_root=REPO_ROOT)
    out = resolve(manifest, baseline_root=REPO_ROOT, project_root=REPO_ROOT)

    expected = {
        f.stem
        for f in (REPO_ROOT / "skills" / "global").glob("*.md")
        if "." not in f.stem
    }
    assert set(out.skills.keys()) == expected

    project_skills_dir = REPO_ROOT / manifest.resolution.skills_dir

    global_dir = REPO_ROOT / "skills" / "global"

    for name, body in out.skills.items():
        assert body, f"composed skill {name!r} is empty"
        assert PLACEHOLDER_RE.search(body) is None, (
            f"composed skill {name!r} still has slot placeholders"
        )
        assert INSERT_RE.search(body) is None, (
            f"composed skill {name!r} still has insert markers"
        )
        for kind, slot_name, probe in _authored_probes(
            project_skills_dir / f"{name}.custom.md"
        ):
            assert probe in body, (
                f"composed {name!r}: {kind} {slot_name!r} authored content "
                f"missing — probe {probe!r} not found in output"
            )

        template = (global_dir / f"{name}.md").read_text(encoding="utf-8")
        contrib_path = project_skills_dir / f"{name}.custom.md"
        contrib_slots: dict[str, str] = {}
        if contrib_path.is_file():
            contrib_text = contrib_path.read_text(encoding="utf-8")
            fences = _fence_regions(contrib_text)
            headers = [
                m for m in SLOT_INSERT_HEADER_RE.finditer(contrib_text)
                if not _in_fence(m.start(), fences)
            ]
            for i, h in enumerate(headers):
                if h.group(1) != "slot":
                    continue
                body_start = h.end()
                body_end = headers[i + 1].start() if i + 1 < len(headers) else len(contrib_text)
                value = contrib_text[body_start:body_end].strip()
                if value:
                    contrib_slots[h.group(2)] = value

        for slot_name, default, suffix in _paragraph_embedded_slots(template):
            value = contrib_slots.get(slot_name, default)
            if value is None or not suffix:
                continue
            value = value.strip()
            assert f"{value}{suffix}" in body, (
                f"composed {name!r}: paragraph-embedded slot {slot_name!r} "
                f"broken — expected {value!r}{suffix!r} adjacent in output"
            )
            assert f"{value}\n{suffix.lstrip()}" not in body, (
                f"composed {name!r}: paragraph-embedded slot {slot_name!r} "
                f"broke paragraph — found newline between value and suffix"
            )


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


def test_h2_inside_body_does_not_terminate_block(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: section -->\n"
    pattern_contrib = (
        "## insert: section\n\n"
        "## Subsection\n\n"
        "Body content under the H2.\n"
    )
    _build_baseline(baseline, skill_template=template, pattern_skill=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "## Subsection" in skill
    assert "Body content under the H2." in skill


def test_h2_inside_fenced_code_block_does_not_terminate_block(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: protocol -->\n"
    pattern_contrib = (
        "## insert: protocol\n\n"
        "Post a comment shaped like:\n\n"
        "```\n"
        "## Implementation Summary\n\n"
        "<description>\n"
        "```\n\n"
        "Trailing prose after the fence.\n"
    )
    _build_baseline(baseline, skill_template=template, pattern_skill=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "## Implementation Summary" in skill
    assert "Trailing prose after the fence." in skill
    assert skill.count("```") == 2


def test_multiple_inserts_with_internal_h2(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: first -->\n<!-- insert: second -->\n"
    pattern_contrib = (
        "## insert: first\n\n"
        "## First Subhead\n\n"
        "first body\n\n"
        "## insert: second\n\n"
        "## Second Subhead\n\n"
        "second body\n"
    )
    _build_baseline(baseline, skill_template=template, pattern_skill=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "## First Subhead" in skill
    assert "first body" in skill
    assert "## Second Subhead" in skill
    assert "second body" in skill
    assert skill.index("first body") < skill.index("## Second Subhead")
    assert "second body" not in skill[: skill.index("## Second Subhead")]


def test_slot_header_inside_fence_is_quoted_not_parsed(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: docs -->\n"
    pattern_contrib = (
        "## insert: docs\n\n"
        "Authors declare slots like:\n\n"
        "```\n"
        "## slot: NESTED\n\n"
        "value\n"
        "```\n\n"
        "End of docs.\n"
    )
    _build_baseline(baseline, skill_template=template, pattern_skill=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "## slot: NESTED" in skill
    assert "End of docs." in skill


def test_crlf_line_endings_do_not_break_boundary_detection(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: mixed -->\n"
    pattern_text = (
        "## insert: mixed\r\n\r\n"
        "## Sub\r\n\r\n"
        "prose\r\n\r\n"
        "```\r\n"
        "## Implementation Summary\r\n"
        "```\r\n\r\n"
        "tail prose\r\n"
    )
    (baseline / "skills" / "global").mkdir(parents=True, exist_ok=True)
    (baseline / "skills" / "global" / "tinyskill.md").write_text(
        template, encoding="utf-8"
    )
    (baseline / "skills" / "pattern" / "tiny").mkdir(parents=True, exist_ok=True)
    (baseline / "skills" / "pattern" / "tiny" / "tinyskill.md").write_bytes(
        pattern_text.encode("utf-8")
    )
    (baseline / "conventions" / "pattern" / "tiny").mkdir(parents=True, exist_ok=True)
    (baseline / "baseline").mkdir(parents=True, exist_ok=True)
    (baseline / "baseline" / "coding_guidelines.md").write_text("# g\n", encoding="utf-8")
    (baseline / "invariants").mkdir(parents=True, exist_ok=True)
    (baseline / "invariants" / "global.md").write_text(
        "## GL-1 — Foo\n\nrule\n", encoding="utf-8"
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "## Sub" in skill
    assert "prose" in skill
    assert "## Implementation Summary" in skill
    assert "tail prose" in skill


def test_authored_probes_is_fence_aware(tmp_path: Path):
    """The dogfood oracle (`_authored_probes`) must agree with the parser on
    what counts as a slot/insert header. A `## slot:` or `## insert:` line
    inside a fence is content, not a header — the oracle must skip it, or it
    will mis-extract probes from contributions that quote the grammar in
    documentation."""
    contribution = tmp_path / "fence-aware.md"
    contribution.write_text(
        "## insert: real_one\n\n"
        "first body\n\n"
        "```\n"
        "## insert: quoted_in_fence\n\n"
        "should not be treated as a header\n"
        "```\n\n"
        "## insert: real_two\n\n"
        "second body\n",
        encoding="utf-8",
    )
    probes = _authored_probes(contribution)
    names = [name for _, name, _ in probes]
    assert names == ["real_one", "real_two"]
    assert "quoted_in_fence" not in names


def test_paragraph_embedded_slot_strips_trailing_newline(tmp_path: Path):
    """Discrimination test: a single template with one paragraph-embedded slot
    and one top-of-section slot. Paragraph-embedded site must compose without
    a stray newline; top-of-section site must keep its newline so the
    paragraph that follows does not run on. A fix that strips unconditionally
    fails the section assertion; a fix that never strips fails the embedded
    assertion."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = (
        "# T\n\n"
        "Read (a) X, (b) {{EMBEDDED=default-clause}}, and (c) Y.\n\n"
        "{{SECTION=section-default}}\n\n"
        "Trailing paragraph.\n"
    )
    _build_baseline(baseline, skill_template=template)
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## slot: EMBEDDED\n\nembedded-value\n\n## slot: SECTION\n\nsection-value\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "Read (a) X, (b) embedded-value, and (c) Y." in skill
    assert "section-value\n\n\nTrailing paragraph." in skill


def test_paragraph_embedded_slot_default_path(tmp_path: Path):
    """Same template, no contribution. The embedded site must compose with the
    inline default unbroken — `_normalize_block` is not in the path, but the
    substitution-time fix must still produce intact prose."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = (
        "# T\n\n"
        "Read (a) X, (b) {{EMBEDDED=default-clause}}, and (c) Y.\n\n"
        "{{SECTION=section-default}}\n\n"
        "Trailing paragraph.\n"
    )
    _build_baseline(baseline, skill_template=template)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "Read (a) X, (b) default-clause, and (c) Y." in skill


def test_paragraph_embedded_slot_at_eof(tmp_path: Path):
    """Placeholder on the last line of the template, with non-blank content on
    the same line. EOF on the trailing side must be treated as paragraph-
    embedded (newline stripped). Guards against a wrong implementation that
    treats EOF as a blank line and so leaves the trailing newline intact."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\nClause: {{EMBEDDED=default-clause}}."
    _build_baseline(baseline, skill_template=template)
    manifest_path = _build_manifest(project)
    _write(
        project / ".claude" / "commands" / "tinyskill.custom.md",
        "## slot: EMBEDDED\n\neof-value\n",
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    skill = out.skills["tinyskill"]
    assert "Clause: eof-value." in skill
    assert "eof-value\n." not in skill


def test_resolved_project_is_frozen(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, skill_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    with pytest.raises(Exception):
        out.skills = {}  # type: ignore[misc]
