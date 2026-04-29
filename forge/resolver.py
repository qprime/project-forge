from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from pathlib import Path

from forge.manifest import Manifest

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)(?:=([^}]*))?\}\}")
INSERT_RE = re.compile(r"^[ \t]*<!-- insert: ([A-Za-z][A-Za-z0-9_-]*) -->[ \t]*\n?", re.MULTILINE)
SLOT_INSERT_HEADER_RE = re.compile(
    r"^## (slot|insert): ([A-Za-z][A-Za-z0-9_-]*)\s*$", re.MULTILINE
)
FENCE_LINE_RE = re.compile(r"^(`{3,})[^\n]*$", re.MULTILINE)
INVARIANT_ID_RE = re.compile(r"^## ((?:GL|FG|[A-Z]{2,4})-\d+) —", re.MULTILINE)


class ResolverError(Exception):
    """Raised when resolver composition fails."""


@dataclass(frozen=True)
class ResolvedProject:
    commands: dict[str, str]
    invariants: str
    conventions: dict[str, str]


@dataclass(frozen=True)
class _Contribution:
    slots: dict[str, str]
    inserts: dict[str, str]
    source: Path


def resolve(
    manifest: Manifest,
    baseline_root: str | Path,
    project_root: str | Path,
) -> ResolvedProject:
    baseline_root = Path(baseline_root)
    project_root = Path(project_root)

    if manifest.secondary_patterns:
        warnings.warn(
            f"resolver v1 does not compose scoped artifacts; "
            f"{len(manifest.secondary_patterns)} secondary patterns ignored",
            stacklevel=2,
        )

    commands = _compose_commands(manifest, baseline_root, project_root)
    invariants = _compose_invariants(manifest, baseline_root, project_root)
    conventions = _compose_conventions(manifest, baseline_root, project_root)

    return ResolvedProject(commands=commands, invariants=invariants, conventions=conventions)


def _compose_commands(
    manifest: Manifest, baseline_root: Path, project_root: Path
) -> dict[str, str]:
    global_dir = baseline_root / "commands" / "global"
    command_names = sorted(
        f.stem for f in global_dir.glob("*.md") if "." not in f.stem
    )

    pattern_dir = baseline_root / "commands" / "pattern" / manifest.primary_pattern

    out: dict[str, str] = {}
    for name in command_names:
        template = _read_text(global_dir / f"{name}.md")
        pattern_contrib = _parse_contribution(pattern_dir / f"{name}.md")
        project_contrib = _project_contribution(manifest, name)
        out[name] = _compose_command(name, template, pattern_contrib, project_contrib)
    return out


def _project_contribution(manifest: Manifest, command_name: str) -> _Contribution:
    layer = manifest.project.get(command_name)
    if layer is None:
        return _Contribution(slots={}, inserts={}, source=manifest.source_path)
    return _Contribution(
        slots=dict(layer.slots),
        inserts=dict(layer.inserts),
        source=manifest.source_path,
    )


def _compose_command(
    command: str,
    template: str,
    pattern: _Contribution,
    project: _Contribution,
) -> str:
    template_slots, template_inserts = _scan_template_placeholders(template)

    for contrib in (pattern, project):
        for placeholder in contrib.slots:
            if placeholder not in template_slots:
                raise ResolverError(
                    f"unknown placeholder {placeholder!r} in {contrib.source}: "
                    f"not defined in commands/global/{command}.md"
                )
        for placeholder in contrib.inserts:
            if placeholder not in template_inserts:
                raise ResolverError(
                    f"unknown placeholder {placeholder!r} in {contrib.source}: "
                    f"not defined in commands/global/{command}.md"
                )

    def slot_sub(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        if name in project.slots:
            value = project.slots[name]
        elif name in pattern.slots:
            value = pattern.slots[name]
        elif default is not None:
            value = default
        else:
            raise ResolverError(
                f"slot {name!r} in {command}: no layer filled it; no inline default"
            )
        if _is_paragraph_embedded(match.string, match.start(), match.end()):
            if value.endswith("\n"):
                value = value[:-1]
        return value

    filled = PLACEHOLDER_RE.sub(slot_sub, template)

    def insert_sub(match: re.Match[str]) -> str:
        name = match.group(1)
        parts: list[str] = []
        if name in pattern.inserts:
            parts.append(pattern.inserts[name])
        if name in project.inserts:
            parts.append(project.inserts[name])
        if not parts:
            return ""
        return "\n\n".join(p.rstrip() for p in parts) + "\n"

    filled = INSERT_RE.sub(insert_sub, filled)
    return filled


def _compose_invariants(
    manifest: Manifest, baseline_root: Path, project_root: Path
) -> str:
    layers: list[tuple[Path, str]] = []
    candidates = [
        baseline_root / "invariants" / "global.md",
        baseline_root / "invariants" / "pattern" / f"{manifest.primary_pattern}.md",
    ]
    for domain in manifest.domains:
        candidates.append(baseline_root / "invariants" / "domain" / f"{domain}.md")
    candidates.append(project_root / manifest.resolution.invariants_dir / "global.md")

    for path in candidates:
        if path.is_file():
            layers.append((path, _read_text(path)))

    if not layers:
        return ""

    composed = "\n\n".join(text.rstrip() for _, text in layers) + "\n"

    seen: dict[str, Path] = {}
    for path, text in layers:
        for match in INVARIANT_ID_RE.finditer(text):
            inv_id = match.group(1)
            if inv_id in seen:
                raise ResolverError(
                    f"invariant ID {inv_id!r} duplicated: defined in "
                    f"{seen[inv_id]} and {path}"
                )
            seen[inv_id] = path

    return composed


def _compose_conventions(
    manifest: Manifest, baseline_root: Path, project_root: Path
) -> dict[str, str]:
    language = manifest.language
    if language is None:
        return {}
    candidates = [
        baseline_root / "conventions" / "global" / f"{language}.md",
        baseline_root / "conventions" / "pattern" / manifest.primary_pattern / f"{language}.md",
    ]
    for domain in manifest.domains:
        candidates.append(
            baseline_root / "conventions" / "domain" / domain / f"{language}.md"
        )
    candidates.append(project_root / manifest.resolution.conventions_dir / f"{language}.md")

    layers = [_read_text(p) for p in candidates if p.is_file()]
    if not layers:
        return {language: ""}
    composed = "\n\n".join(t.rstrip() for t in layers) + "\n"
    return {language: composed}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ResolverError(f"failed to read {path}: {exc}") from exc


def _parse_contribution(path: Path) -> _Contribution:
    if not path.is_file():
        return _Contribution(slots={}, inserts={}, source=path)
    text = _read_text(path)

    slots: dict[str, str] = {}
    inserts: dict[str, str] = {}

    fences = _fence_regions(text)
    headers = [
        m for m in SLOT_INSERT_HEADER_RE.finditer(text)
        if not _in_fence(m.start(), fences)
    ]
    for i, match in enumerate(headers):
        kind = match.group(1)
        name = match.group(2)
        body_start = match.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = _normalize_block(text[body_start:body_end])
        if body == "":
            continue
        if kind == "slot":
            slots[name] = body
        else:
            inserts[name] = body
    return _Contribution(slots=slots, inserts=inserts, source=path)


def _fence_regions(text: str) -> list[tuple[int, int]]:
    regions: list[tuple[int, int]] = []
    opener: re.Match[str] | None = None
    for m in FENCE_LINE_RE.finditer(text):
        if opener is None:
            opener = m
            continue
        closer_ticks = m.group(1)
        info = m.group(0)[len(closer_ticks):]
        if len(closer_ticks) >= len(opener.group(1)) and info.strip() == "":
            regions.append((opener.start(), m.end()))
            opener = None
    if opener is not None:
        regions.append((opener.start(), len(text)))
    return regions


def _in_fence(pos: int, fences: list[tuple[int, int]]) -> bool:
    for start, end in fences:
        if start <= pos < end:
            return True
        if pos < start:
            return False
    return False


def _is_paragraph_embedded(template: str, start: int, end: int) -> bool:
    line_start = template.rfind("\n", 0, start) + 1
    line_end = template.find("\n", end)
    if line_end == -1:
        line_end = len(template)
    before = template[line_start:start]
    after = template[end:line_end]
    if before.strip() != "" or after.strip() != "":
        return True
    prev_line_end = line_start - 1
    next_line_start = line_end + 1
    prev_blank = prev_line_end < 0 or template[:prev_line_end].rsplit("\n", 1)[-1].strip() == ""
    if next_line_start >= len(template):
        next_blank = True
    else:
        nl = template.find("\n", next_line_start)
        if nl == -1:
            nl = len(template)
        next_blank = template[next_line_start:nl].strip() == ""
    return not prev_blank and not next_blank


def _normalize_block(body: str) -> str:
    body = body.lstrip("\n")
    body = body.rstrip()
    if body == "":
        return ""
    return body + "\n"


def _scan_template_placeholders(template: str) -> tuple[set[str], set[str]]:
    slots = {m.group(1) for m in PLACEHOLDER_RE.finditer(template)}
    inserts = {m.group(1) for m in INSERT_RE.finditer(template)}
    return slots, inserts
