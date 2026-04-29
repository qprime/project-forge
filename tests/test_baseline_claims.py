from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOBAL_COMMANDS_DIR = REPO_ROOT / "commands" / "global"

DOC_FILES_CLAIMING_BASELINE: tuple[Path, ...] = ()

_SKILL_NAME = r"/([a-z][a-z0-9-]*)"
_SKILL_RE = re.compile(rf"`{_SKILL_NAME}`")

_DEFINES_RE = re.compile(
    r"baseline\s+defines[^.]*?:\s*(?P<list>(?:`/[a-z0-9-]+`[\s,;]*)+)",
    re.IGNORECASE,
)

_TABLE_HEADER_RE = re.compile(r"^\s*\|\s*Baseline\s+Skill\s*\|", re.IGNORECASE)
_TABLE_ROW_FIRST_CELL_RE = re.compile(r"^\s*\|\s*(?P<cell>[^|]+?)\s*\|")


def _baseline_skills() -> set[str]:
    return {p.stem for p in GLOBAL_COMMANDS_DIR.glob("*.md") if "." not in p.stem}


def _claims_from_defines_sentences(text: str) -> set[str]:
    claimed: set[str] = set()
    for match in _DEFINES_RE.finditer(text):
        for skill in _SKILL_RE.finditer(match.group("list")):
            claimed.add(skill.group(1))
    return claimed


def _claims_from_baseline_skill_tables(text: str) -> set[str]:
    claimed: set[str] = set()
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if _TABLE_HEADER_RE.match(lines[i]):
            i += 1
            if i < len(lines) and re.match(r"^\s*\|\s*-", lines[i]):
                i += 1
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cell_match = _TABLE_ROW_FIRST_CELL_RE.match(lines[i])
                if cell_match:
                    skill_match = re.match(rf"^{_SKILL_NAME}\s*$", cell_match.group("cell"))
                    if skill_match:
                        claimed.add(skill_match.group(1))
                i += 1
        else:
            i += 1
    return claimed


def _claimed_skills(doc: Path) -> set[str]:
    text = doc.read_text(encoding="utf-8")
    return _claims_from_defines_sentences(text) | _claims_from_baseline_skill_tables(text)


def test_doc_claims_match_global_commands():
    actual = _baseline_skills()
    assert actual, "commands/global/ is empty — test setup is wrong"

    for doc in DOC_FILES_CLAIMING_BASELINE:
        claimed = _claimed_skills(doc)
        missing = claimed - actual
        assert not missing, (
            f"{doc.relative_to(REPO_ROOT)} claims baseline skills "
            f"{sorted(missing)} that do not exist in commands/global/. "
            f"Either add the file or strike the claim. "
            f"Actual baseline: {sorted(actual)}"
        )
