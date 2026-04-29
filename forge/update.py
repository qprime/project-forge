from __future__ import annotations

import argparse
import difflib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from forge.manifest import Manifest, ManifestError, load_manifest
from forge.resolver import ResolverError, resolve

ChangeKind = Literal["unchanged", "update", "create"]


class UpdateError(Exception):
    """Raised when update planning or application fails."""


@dataclass(frozen=True)
class FileChange:
    path: Path
    kind: ChangeKind
    body: str
    diff: str


@dataclass(frozen=True)
class UpdatePlan:
    changes: tuple[FileChange, ...]

    @property
    def has_drift(self) -> bool:
        return any(c.kind != "unchanged" for c in self.changes)


def plan_update(
    manifest: Manifest,
    baseline_root: str | Path,
    project_root: str | Path,
) -> UpdatePlan:
    baseline_root = Path(baseline_root)
    project_root = Path(project_root)
    resolved = resolve(manifest, baseline_root=baseline_root, project_root=project_root)
    commands_dir = project_root / manifest.resolution.commands_dir
    changes: list[FileChange] = []
    for name in sorted(resolved.commands):
        body = resolved.commands[name]
        target = commands_dir / f"{name}.md"
        if target.is_file():
            current = target.read_text(encoding="utf-8")
            if current == body:
                changes.append(FileChange(path=target, kind="unchanged", body=body, diff=""))
                continue
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(keepends=True),
                    body.splitlines(keepends=True),
                    fromfile=str(target),
                    tofile=str(target),
                )
            )
            changes.append(FileChange(path=target, kind="update", body=body, diff=diff))
        else:
            diff = "".join(
                difflib.unified_diff(
                    [],
                    body.splitlines(keepends=True),
                    fromfile="/dev/null",
                    tofile=str(target),
                )
            )
            changes.append(FileChange(path=target, kind="create", body=body, diff=diff))
    return UpdatePlan(changes=tuple(changes))


def apply_update(plan: UpdatePlan) -> None:
    for change in plan.changes:
        if change.kind == "unchanged":
            continue
        if not change.body.endswith("\n"):
            raise UpdateError(
                f"refusing to write {change.path}: composed body lacks trailing newline"
            )
        try:
            change.path.parent.mkdir(parents=True, exist_ok=True)
            change.path.write_text(change.body, encoding="utf-8")
        except OSError as exc:
            raise UpdateError(f"failed to write {change.path}: {exc}") from exc


def _format_status(change: FileChange) -> str:
    if change.kind == "unchanged":
        return f"unchanged  {change.path}"
    if change.kind == "create":
        added = len(change.body.splitlines())
        return f"would create  {change.path} ({added}+)"
    added = sum(1 for line in change.diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in change.diff.splitlines() if line.startswith("-") and not line.startswith("---"))
    return f"would update  {change.path} ({added}+/{removed}-)"


def _applied_status(change: FileChange) -> str:
    if change.kind == "unchanged":
        return f"unchanged  {change.path}"
    if change.kind == "create":
        return f"created  {change.path}"
    return f"updated  {change.path}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="forge update", description=__doc__)
    _add_arguments(parser)
    args = parser.parse_args(argv)
    return _run(args)


def _add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--apply", action="store_true", help="write composed commands to disk")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="exit non-zero when drift is detected (no-op with --apply)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="path to manifest (default: <cwd>/.forge/manifest.yaml)",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=None,
        help="path to baseline root (default: manifest's project root)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="path to project root (default: manifest's parent's parent)",
    )


def _run(args: argparse.Namespace) -> int:
    manifest_path = args.manifest or Path.cwd() / ".forge" / "manifest.yaml"
    project_root = args.project_root or manifest_path.parent.parent
    baseline_root = args.baseline_root or project_root
    try:
        manifest = load_manifest(
            manifest_path, baseline_root=baseline_root, project_root=project_root
        )
        plan = plan_update(manifest, baseline_root=baseline_root, project_root=project_root)
    except (ManifestError, ResolverError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.apply:
        try:
            apply_update(plan)
        except UpdateError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        for change in plan.changes:
            print(_applied_status(change))
        return 0

    for change in plan.changes:
        print(_format_status(change))
    for change in plan.changes:
        if change.kind != "unchanged" and change.diff:
            print()
            print(change.diff, end="")

    if args.exit_code and plan.has_drift:
        return 1
    return 0
