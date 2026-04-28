from __future__ import annotations

import os
import warnings
from dataclasses import replace
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from forge.cli import main as cli_main
from forge.manifest import load_manifest
from forge.resolver import ResolverError, resolve
from forge.update import (
    FileChange,
    UpdateError,
    UpdatePlan,
    apply_update,
    plan_update,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PROJECT = REPO_ROOT / "tests" / "fixtures" / "sample_project"
SAMPLE_MANIFEST = SAMPLE_PROJECT / ".forge" / "manifest.yaml"


# ---------------------------------------------------------------------------
# Synthetic baseline / project builders (mirrors test_resolver.py)
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
) -> Path:
    _write(root / "skills" / "global" / "tinyskill.md", skill_template)
    (root / "skills" / "pattern" / pattern).mkdir(parents=True, exist_ok=True)
    if pattern_skill is not None:
        _write(root / "skills" / "pattern" / pattern / "tinyskill.md", pattern_skill)
    (root / "conventions" / "domain").mkdir(parents=True, exist_ok=True)
    (root / "conventions" / "pattern" / pattern).mkdir(parents=True, exist_ok=True)
    _write(root / "invariants" / "global.md", "## GL-1 — Foo\n\nrule\n")
    _write(root / "baseline" / "coding_guidelines.md", "# global\n")
    return root


def _build_manifest_file(
    project_root: Path,
    *,
    primary: str = "tiny",
    skills_dir: str = ".claude/commands/",
) -> Path:
    payload = {
        "schema_version": 1,
        "patterns": {"primary": primary, "secondary": []},
        "domains": [],
        "language": "python",
        "python_version": "3.12",
        "project_context": {"description": "synthetic"},
        "resolution": {
            "baseline_version": "2026-04-27",
            "skills_dir": skills_dir,
            "invariants_dir": "docs/invariants/",
            "conventions_dir": "docs/conventions/",
        },
    }
    (project_root / ".forge").mkdir(parents=True, exist_ok=True)
    manifest_path = project_root / ".forge" / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(payload), encoding="utf-8")
    return manifest_path


def _setup(tmp_path: Path, **baseline_kwargs):
    baseline = tmp_path / "baseline"
    project = tmp_path / "proj"
    _build_baseline(baseline, **baseline_kwargs)
    manifest_path = _build_manifest_file(project)
    manifest = load_manifest(manifest_path, baseline_root=baseline)
    return baseline, project, manifest


# ---------------------------------------------------------------------------
# plan_update
# ---------------------------------------------------------------------------


class TestPlanUpdate:
    def test_unchanged_when_disk_matches(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        composed = resolve(manifest, baseline_root=baseline, project_root=project).skills["tinyskill"]
        target = project / ".claude" / "commands" / "tinyskill.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(composed, encoding="utf-8")
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        assert len(plan.changes) == 1
        assert plan.changes[0].kind == "unchanged"
        assert plan.changes[0].diff == ""
        assert plan.has_drift is False

    def test_update_when_disk_differs(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        target = project / ".claude" / "commands" / "tinyskill.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("stale content\n", encoding="utf-8")
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        assert plan.changes[0].kind == "update"
        assert plan.changes[0].diff
        assert plan.has_drift is True

    def test_create_when_disk_missing(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        assert plan.changes[0].kind == "create"
        assert plan.changes[0].diff
        assert plan.has_drift is True

    def test_only_resolver_owned_files_in_plan(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        skills_dir = project / ".claude" / "commands"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "bootstrap.md").write_text("forge command\n", encoding="utf-8")
        (skills_dir / "survey.md").write_text("forge command\n", encoding="utf-8")
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        targets = {c.path.name for c in plan.changes}
        assert targets == {"tinyskill.md"}

    def test_prompt_files_never_targeted(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        skills_dir = project / ".claude" / "commands"
        skills_dir.mkdir(parents=True, exist_ok=True)
        prompt = skills_dir / "tinyskill.prompt.md"
        prompt.write_text("companion content\n", encoding="utf-8")
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        targets = {c.path.name for c in plan.changes}
        assert "tinyskill.prompt.md" not in targets

    def test_resolver_error_propagates(self, tmp_path: Path):
        baseline, project, manifest = _setup(
            tmp_path, skill_template="# T\n\n{{REQUIRED}}\n"
        )
        with pytest.raises(ResolverError):
            plan_update(manifest, baseline_root=baseline, project_root=project)


# ---------------------------------------------------------------------------
# apply_update
# ---------------------------------------------------------------------------


class TestApplyUpdate:
    def test_apply_writes_only_non_unchanged(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        composed = resolve(manifest, baseline_root=baseline, project_root=project).skills["tinyskill"]
        target = project / ".claude" / "commands" / "tinyskill.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(composed, encoding="utf-8")
        before_mtime = target.stat().st_mtime_ns
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        apply_update(plan)
        assert target.stat().st_mtime_ns == before_mtime

    def test_apply_creates_parent_dirs(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        target = project / ".claude" / "commands" / "tinyskill.md"
        assert not target.parent.exists()
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        apply_update(plan)
        assert target.is_file()

    def test_apply_is_idempotent(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        apply_update(plan)
        plan2 = plan_update(manifest, baseline_root=baseline, project_root=project)
        assert all(c.kind == "unchanged" for c in plan2.changes)

    def test_apply_propagates_io_errors(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        skills_parent = project / ".claude"
        skills_parent.mkdir(parents=True, exist_ok=True)
        commands_dir = skills_parent / "commands"
        commands_dir.mkdir(exist_ok=True)
        commands_dir.chmod(0o500)
        try:
            if os.geteuid() == 0:
                pytest.skip("root bypasses permission checks")
            with pytest.raises(UpdateError, match="failed to write"):
                apply_update(plan)
        finally:
            commands_dir.chmod(0o700)

    def test_apply_asserts_trailing_newline(self, tmp_path: Path):
        baseline, project, manifest = _setup(tmp_path)
        plan = plan_update(manifest, baseline_root=baseline, project_root=project)
        original = plan.changes[0]
        broken = replace(original, body=original.body.rstrip("\n"))
        broken_plan = UpdatePlan(changes=(broken,))
        with pytest.raises(UpdateError, match="trailing newline"):
            apply_update(broken_plan)
        assert not original.path.exists()


# ---------------------------------------------------------------------------
# Sample-project end-to-end
# ---------------------------------------------------------------------------


class TestSampleProjectUpdate:
    def test_sample_project_update_is_idempotent_after_apply(self, tmp_path: Path):
        proj = tmp_path / "sample"
        (proj / ".forge").mkdir(parents=True)
        (proj / ".forge" / "manifest.yaml").write_text(
            SAMPLE_MANIFEST.read_text(encoding="utf-8"), encoding="utf-8"
        )

        proj_manifest = load_manifest(
            proj / ".forge" / "manifest.yaml",
            baseline_root=REPO_ROOT,
            project_root=proj,
        )
        plan = plan_update(proj_manifest, baseline_root=REPO_ROOT, project_root=proj)

        expected_skills = {
            f.stem for f in (REPO_ROOT / "skills" / "global").glob("*.md") if "." not in f.stem
        }
        targets = {c.path.stem for c in plan.changes}
        assert targets == expected_skills
        assert all(c.kind == "create" for c in plan.changes)

        apply_update(plan)
        plan2 = plan_update(proj_manifest, baseline_root=REPO_ROOT, project_root=proj)
        assert all(c.kind == "unchanged" for c in plan2.changes)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_args(project: Path, baseline: Path, *flags: str) -> list[str]:
    return [
        "update",
        "--manifest",
        str(project / ".forge" / "manifest.yaml"),
        "--baseline-root",
        str(baseline),
        "--project-root",
        str(project),
        *flags,
    ]


class TestCli:
    def test_no_apply_exits_zero_when_clean(self, tmp_path: Path, capsys):
        baseline, project, manifest = _setup(tmp_path)
        composed = resolve(manifest, baseline_root=baseline, project_root=project).skills["tinyskill"]
        target = project / ".claude" / "commands" / "tinyskill.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(composed, encoding="utf-8")
        rc = cli_main(_cli_args(project, baseline))
        assert rc == 0
        assert "unchanged" in capsys.readouterr().out

    def test_no_apply_with_exit_code_flag_exits_one_on_drift(self, tmp_path: Path, capsys):
        baseline, project, _ = _setup(tmp_path)
        rc = cli_main(_cli_args(project, baseline, "--exit-code"))
        assert rc == 1
        assert "would create" in capsys.readouterr().out

    def test_no_apply_default_exits_zero_on_drift(self, tmp_path: Path):
        baseline, project, _ = _setup(tmp_path)
        rc = cli_main(_cli_args(project, baseline))
        assert rc == 0

    def test_apply_writes_and_exits_zero(self, tmp_path: Path):
        baseline, project, _ = _setup(tmp_path)
        rc = cli_main(_cli_args(project, baseline, "--apply"))
        assert rc == 0
        assert (project / ".claude" / "commands" / "tinyskill.md").is_file()

    def test_apply_with_exit_code_still_exits_zero(self, tmp_path: Path):
        baseline, project, _ = _setup(tmp_path)
        rc = cli_main(_cli_args(project, baseline, "--apply", "--exit-code"))
        assert rc == 0

    def test_resolver_error_exits_two(self, tmp_path: Path, capsys):
        baseline, project, _ = _setup(
            tmp_path, skill_template="# T\n\n{{REQUIRED}}\n"
        )
        rc = cli_main(_cli_args(project, baseline))
        assert rc == 2
        assert "error:" in capsys.readouterr().err
