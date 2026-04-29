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
    ResolverError,
    _is_paragraph_embedded,
    resolve,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PROJECT = REPO_ROOT / "tests" / "fixtures" / "sample_project"
SAMPLE_MANIFEST = SAMPLE_PROJECT / ".forge" / "manifest.yaml"


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
    command_template: str = "# Tinyskill\n\nValue: {{X=ok}}\n",
    pattern: str = "tiny",
    pattern_command: str | None = None,
    invariants_global: str | None = "## GL-1 — Foo\n\nrule\n",
    invariants_pattern: str | None = None,
    invariants_domain: dict[str, str] | None = None,
    conventions_global: str | None = "# Global conventions\n",
    conventions_pattern: dict[str, str] | None = None,
    conventions_domain: dict[str, dict[str, str]] | None = None,
    extra_global_commands: dict[str, str] | None = None,
) -> Path:
    _write(root / "commands" / "global" / "tinyskill.md", command_template)
    if extra_global_commands:
        for name, body in extra_global_commands.items():
            _write(root / "commands" / "global" / f"{name}.md", body)
    (root / "commands" / "pattern" / pattern).mkdir(parents=True, exist_ok=True)
    if pattern_command is not None:
        _write(root / "commands" / "pattern" / pattern / "tinyskill.md", pattern_command)
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
        _write(root / "conventions" / "global" / "python.md", conventions_global)
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
    language: str | None = "python",
    commands_dir: str = ".claude/commands/",
    invariants_dir: str = "docs/invariants/",
    conventions_dir: str = "docs/conventions/",
    customizations: dict | None = None,
) -> Manifest:
    payload = {
        "schema_version": 1,
        "patterns": {
            "primary": primary,
            "secondary": [{"name": n, "scope": s} for n, s in secondaries],
        },
        "domains": list(domains),
        "project_context": {"description": "synthetic"},
        "resolution": {
            "baseline_version": "2026-04-27",
            "commands_dir": commands_dir,
            "invariants_dir": invariants_dir,
            "conventions_dir": conventions_dir,
        },
    }
    if language is not None:
        payload["language"] = language
        if language == "python":
            payload["python_version"] = "3.12"
    if customizations is not None:
        payload["customizations"] = customizations
    (project_root / ".forge").mkdir(parents=True, exist_ok=True)
    manifest_path = project_root / ".forge" / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    for n, s in secondaries:
        (project_root / s).mkdir(parents=True, exist_ok=True)
    return manifest_path


# ---------------------------------------------------------------------------
# Sample-project end-to-end (positive)
#
# `tests/fixtures/sample_project/` is a synthetic compiler-pattern project
# that exercises the full pipeline against forge's real `commands/global/` and
# `commands/pattern/compiler/`. It plays the role the forge dogfood test
# previously did — a real, complete manifest driving composition end to end.
# ---------------------------------------------------------------------------


def _authored_probes(manifest: Manifest, command_name: str) -> list[tuple[str, str, str]]:
    """Iterate manifest.customizations for a command and return (kind, name, probe)
    tuples for each declared slot/insert. The probe is the first non-blank line
    of the body as authored — if the composed command is missing the probe,
    content was lost during composition."""
    custom = manifest.customizations.get(command_name)
    if custom is None:
        return []
    out: list[tuple[str, str, str]] = []
    for kind, mapping in (("slot", custom.slots), ("insert", custom.inserts)):
        for name, body in mapping.items():
            stripped = body.strip()
            if not stripped:
                continue
            probe = stripped.splitlines()[0].strip()
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


def test_sample_project_resolves_cleanly():
    """The sample project resolves cleanly against forge's baseline.

    The expected skill set is derived from `commands/global/*.md` so adding a
    new global skill without a matching sample-project contribution surfaces
    here. Every composed skill must be non-empty, contain no leftover slot
    placeholders or insert markers, and contain every authored slot/insert
    body. The body-presence check is what makes this positive: a
    contribution whose content is silently dropped during composition fails
    here even though the structural checks pass."""
    manifest = load_manifest(SAMPLE_MANIFEST, baseline_root=REPO_ROOT)
    out = resolve(manifest, baseline_root=REPO_ROOT, project_root=SAMPLE_PROJECT)

    expected = {
        f.stem
        for f in (REPO_ROOT / "commands" / "global").glob("*.md")
        if "." not in f.stem
    }
    assert set(out.commands.keys()) == expected

    global_dir = REPO_ROOT / "commands" / "global"

    for name, body in out.commands.items():
        assert body, f"composed skill {name!r} is empty"
        assert PLACEHOLDER_RE.search(body) is None, (
            f"composed skill {name!r} still has slot placeholders"
        )
        assert INSERT_RE.search(body) is None, (
            f"composed skill {name!r} still has insert markers"
        )
        for kind, slot_name, probe in _authored_probes(manifest, name):
            assert probe in body, (
                f"composed {name!r}: {kind} {slot_name!r} authored content "
                f"missing — probe {probe!r} not found in output"
            )

        template = (global_dir / f"{name}.md").read_text(encoding="utf-8")
        custom = manifest.customizations.get(name)
        contrib_slots: dict[str, str] = {}
        if custom is not None:
            for slot_name, value in custom.slots.items():
                stripped = value.strip()
                if stripped:
                    contrib_slots[slot_name] = stripped

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
        command_template=(
            "# Tinyskill\n\n"
            "Value: {{X}}\n"
            "Default: {{Y=fallback}}\n\n"
            "<!-- insert: bullets -->\n"
        ),
        pattern_command=(
            "## slot: X\n\nfrom-pattern\n\n"
            "## insert: bullets\n\n- pattern bullet\n"
        ),
    )
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"inserts": {"bullets": "- project bullet\n"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "Value: from-pattern" in command
    assert "Default: fallback" in command
    assert "- pattern bullet" in command
    assert "- project bullet" in command
    assert "<!-- insert:" not in command


def test_slot_precedence_project_over_pattern_over_default(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X=template-default}}\n",
        pattern_command="## slot: X\n\npattern-value\n",
    )
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"slots": {"X": "project-value"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "project-value" in out.commands["tinyskill"]
    assert "pattern-value" not in out.commands["tinyskill"]
    assert "template-default" not in out.commands["tinyskill"]


def test_slot_pattern_used_when_no_project_layer(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X=template-default}}\n",
        pattern_command="## slot: X\n\npattern-value\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "pattern-value" in out.commands["tinyskill"]


def test_slot_inline_default_used_when_no_layer(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{X=the-default}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "the-default" in out.commands["tinyskill"]


def test_insert_ordering_pattern_then_project(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n<!-- insert: items -->\n",
        pattern_command="## insert: items\n\nP1\n",
    )
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"inserts": {"items": "Q1\n"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert command.index("P1") < command.index("Q1")
    between = command[command.index("P1") + 2 : command.index("Q1")]
    assert between == "\n\n"


def test_empty_insert_removes_comment_line(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\nbefore\n<!-- insert: missing -->\nafter\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "<!-- insert:" not in command
    assert "before\nafter\n" in command


def test_unknown_placeholder_in_contribution_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X=ok}}\n",
        pattern_command="## slot: NOT_DEFINED\n\nbogus\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="unknown placeholder 'NOT_DEFINED'"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_required_slot_unfilled_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{REQUIRED}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="slot 'REQUIRED'"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_empty_slot_body_falls_through_to_pattern(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X}}\n",
        pattern_command="## slot: X\n\npattern-wins\n",
    )
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"slots": {"X": "\n"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "pattern-wins" in out.commands["tinyskill"]


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
    _build_baseline(baseline, command_template="# T\n\n{{X=ok}}\n")
    (baseline / "commands" / "pattern" / "extra").mkdir(parents=True, exist_ok=True)
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
        command_template="# T\n\n{{X=ok}}\n",
        conventions_global=None,
    )
    manifest_path = _build_manifest(project, language="rust")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert out.conventions == {"rust": ""}


def test_omitted_language_resolves_with_empty_conventions(tmp_path: Path):
    """A manifest without `language` (notes-first projects) loads silently and
    composes conventions as `{}` — not `{"": ""}`. Guards against the empty-
    string-keyed dict shape that would otherwise leak through."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(project, language=None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        manifest = load_manifest(manifest_path, baseline_root=baseline)
    assert manifest.language is None
    assert not any("toolchain content" in str(w.message) for w in caught)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert out.conventions == {}


def test_command_enumeration_filters_inner_dot_names(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X=ok}}\n",
        extra_global_commands={"architect.notes": "stray notes\n"},
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    assert "tinyskill" in out.commands
    assert "architect.notes" not in out.commands
    assert "architect" not in out.commands


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
    _build_baseline(baseline, command_template=template, pattern_command=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "Top-level paragraph." in command
    assert "### Sub-heading" in command
    assert "Sub-content with more lines." in command
    assert "the-x" in command
    assert "## insert:" not in command
    assert "## slot:" not in command


def test_h2_inside_body_does_not_terminate_block(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\n<!-- insert: section -->\n"
    pattern_contrib = (
        "## insert: section\n\n"
        "## Subsection\n\n"
        "Body content under the H2.\n"
    )
    _build_baseline(baseline, command_template=template, pattern_command=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "## Subsection" in command
    assert "Body content under the H2." in command


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
    _build_baseline(baseline, command_template=template, pattern_command=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "## Implementation Summary" in command
    assert "Trailing prose after the fence." in command
    assert command.count("```") == 2


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
    _build_baseline(baseline, command_template=template, pattern_command=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "## First Subhead" in command
    assert "first body" in command
    assert "## Second Subhead" in command
    assert "second body" in command
    assert command.index("first body") < command.index("## Second Subhead")
    assert "second body" not in command[: command.index("## Second Subhead")]


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
    _build_baseline(baseline, command_template=template, pattern_command=pattern_contrib)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "## slot: NESTED" in command
    assert "End of docs." in command


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
    (baseline / "commands" / "global").mkdir(parents=True, exist_ok=True)
    (baseline / "commands" / "global" / "tinyskill.md").write_text(
        template, encoding="utf-8"
    )
    (baseline / "commands" / "pattern" / "tiny").mkdir(parents=True, exist_ok=True)
    (baseline / "commands" / "pattern" / "tiny" / "tinyskill.md").write_bytes(
        pattern_text.encode("utf-8")
    )
    (baseline / "conventions" / "pattern" / "tiny").mkdir(parents=True, exist_ok=True)
    (baseline / "conventions" / "global").mkdir(parents=True, exist_ok=True)
    (baseline / "conventions" / "global" / "python.md").write_text("# g\n", encoding="utf-8")
    (baseline / "invariants").mkdir(parents=True, exist_ok=True)
    (baseline / "invariants" / "global.md").write_text(
        "## GL-1 — Foo\n\nrule\n", encoding="utf-8"
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "## Sub" in command
    assert "prose" in command
    assert "## Implementation Summary" in command
    assert "tail prose" in command


def test_authored_probes_reads_from_manifest(tmp_path: Path):
    """The dogfood oracle (`_authored_probes`) must iterate
    manifest.customizations, not <commands_dir>/<name>.custom.md. Without this,
    the helper would return [] for every skill after the .custom.md migration
    and the body-presence check would silently pass vacuously."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(
        project,
        customizations={
            "tinyskill": {
                "slots": {"X": "real_slot_value"},
                "inserts": {"items": "first authored line\nsecond line\n"},
            }
        },
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    probes = _authored_probes(manifest, "tinyskill")
    names = sorted(name for _, name, _ in probes)
    assert names == ["X", "items"]
    probe_map = {name: probe for _, name, probe in probes}
    assert probe_map["X"] == "real_slot_value"
    assert probe_map["items"] == "first authored line"


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
    _build_baseline(baseline, command_template=template)
    manifest_path = _build_manifest(
        project,
        customizations={
            "tinyskill": {
                "slots": {
                    "EMBEDDED": "embedded-value",
                    "SECTION": "section-value",
                }
            }
        },
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "Read (a) X, (b) embedded-value, and (c) Y." in command
    assert "section-value\n\n\nTrailing paragraph." in command


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
    _build_baseline(baseline, command_template=template)
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "Read (a) X, (b) default-clause, and (c) Y." in command


def test_paragraph_embedded_slot_at_eof(tmp_path: Path):
    """Placeholder on the last line of the template, with non-blank content on
    the same line. EOF on the trailing side must be treated as paragraph-
    embedded (newline stripped). Guards against a wrong implementation that
    treats EOF as a blank line and so leaves the trailing newline intact."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    template = "# T\n\nClause: {{EMBEDDED=default-clause}}."
    _build_baseline(baseline, command_template=template)
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"slots": {"EMBEDDED": "eof-value"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "Clause: eof-value." in command
    assert "eof-value\n." not in command


def test_unknown_placeholder_in_manifest_customization_errors(tmp_path: Path):
    """An unknown slot name in customizations raises ResolverError citing the
    manifest path as the locator (not a synthetic locator)."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(
        project,
        customizations={"tinyskill": {"slots": {"NOT_A_SLOT": "v"}}},
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="unknown placeholder 'NOT_A_SLOT'") as exc:
        resolve(manifest, baseline_root=baseline, project_root=project)
    assert str(manifest.source_path) in str(exc.value)


def test_resolver_reads_customizations_from_manifest(tmp_path: Path):
    """End-to-end: project-layer slot fills and insert bodies sourced from the
    manifest appear in the composed output, with no .custom.md file present."""
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# T\n\n{{X=default-x}}\n\n<!-- insert: bullets -->\n",
    )
    manifest_path = _build_manifest(
        project,
        customizations={
            "tinyskill": {
                "slots": {"X": "manifest-x"},
                "inserts": {"bullets": "- from manifest\n"},
            }
        },
    )
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    command = out.commands["tinyskill"]
    assert "manifest-x" in command
    assert "- from manifest" in command
    assert not (project / ".claude" / "commands" / "tinyskill.custom.md").exists()


def test_resolved_project_is_frozen(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, command_template="# T\n\n{{X=ok}}\n")
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    out = resolve(manifest, baseline_root=baseline, project_root=project)
    with pytest.raises(Exception):
        out.commands = {}  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Architect slot-removal regression guards (#17)
#
# Issue #17's testing strategy lists five tests; four land here. The fifth
# (`test_what_you_do_block_has_no_check_prefix_bullets`) was dropped: its
# predicate (no `- Check ` prefix bullets in the resolved `What You Do`
# block) false-positives on the long-standing baseline bullet
# `- Check structural fit — does this design compose well with what exists?`
# in `commands/global/architect.md`, which is one of seven designed
# conversation moves and unchanged by #17. The slot-mechanism tests below
# catch the actual regression vector.
# ---------------------------------------------------------------------------


def test_architect_template_has_no_domain_bullets_slot():
    template = (REPO_ROOT / "commands" / "global" / "architect.md").read_text(
        encoding="utf-8"
    )
    assert "<!-- insert: domain-bullets -->" not in template


def test_no_pattern_architect_contributes_domain_bullets():
    from forge.resolver import _parse_contribution

    pattern_dir = REPO_ROOT / "commands" / "pattern"
    for pattern in sorted(p for p in pattern_dir.iterdir() if p.is_dir()):
        contrib_path = pattern / "architect.md"
        if not contrib_path.is_file():
            continue
        contrib = _parse_contribution(contrib_path)
        assert "domain-bullets" not in contrib.inserts, (
            f"pattern {pattern.name!r} reintroduced domain-bullets contribution"
        )


def test_orphaned_domain_bullets_contribution_errors(tmp_path: Path):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(
        baseline,
        command_template="# Architect\n\n{{X=ok}}\n",
        pattern_command="## insert: domain-bullets\n\n- Check the thing.\n",
    )
    manifest_path = _build_manifest(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    with pytest.raises(ResolverError, match="unknown placeholder 'domain-bullets'"):
        resolve(manifest, baseline_root=baseline, project_root=project)


def test_architect_composes_clean_post_migration():
    manifest = load_manifest(SAMPLE_MANIFEST, baseline_root=REPO_ROOT)
    out = resolve(manifest, baseline_root=REPO_ROOT, project_root=SAMPLE_PROJECT)
    architect = out.commands["architect"]
    assert INSERT_RE.search(architect) is None
    assert "<!-- insert:" not in architect
    assert "domain-bullets" not in architect
