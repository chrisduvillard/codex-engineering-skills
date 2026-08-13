#!/usr/bin/env python3
"""Validate the structure and frontmatter of the bundled Codex skills."""

from __future__ import annotations

import py_compile
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EXPECTED_SKILLS = {
    "adversarial-review",
    "deep-plan",
    "harvest-agent-branches",
    "steward-brownfield",
    "trace-data-provenance",
}
NAME_PATTERN = re.compile(r"^name:\s*[\"']?([a-z0-9-]+)[\"']?\s*$", re.MULTILINE)
DESCRIPTION_PATTERN = re.compile(r"^description:\s*\S.+$", re.MULTILINE)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_skill(directory: Path) -> None:
    skill_file = directory / "SKILL.md"
    if not skill_file.is_file():
        fail(f"missing {skill_file.relative_to(ROOT)}")

    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{skill_file.relative_to(ROOT)} does not start with YAML frontmatter")

    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        fail(f"{skill_file.relative_to(ROOT)} has incomplete YAML frontmatter")

    name_match = NAME_PATTERN.search(frontmatter)
    if not name_match:
        fail(f"{skill_file.relative_to(ROOT)} has no valid name")
    if name_match.group(1) != directory.name:
        fail(f"{skill_file.relative_to(ROOT)} name does not match its directory")
    if not DESCRIPTION_PATTERN.search(frontmatter):
        fail(f"{skill_file.relative_to(ROOT)} has no non-empty description")
    if not body.strip():
        fail(f"{skill_file.relative_to(ROOT)} has an empty instruction body")

    print(f"OK: {directory.name}")


def main() -> None:
    discovered = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}
    if discovered != EXPECTED_SKILLS:
        fail(
            "skill set mismatch; "
            f"missing={sorted(EXPECTED_SKILLS - discovered)}, "
            f"unexpected={sorted(discovered - EXPECTED_SKILLS)}"
        )

    for skill_name in sorted(EXPECTED_SKILLS):
        validate_skill(SKILLS_ROOT / skill_name)

    with tempfile.TemporaryDirectory() as bytecode_directory:
        bytecode_root = Path(bytecode_directory)
        for index, script in enumerate(sorted(SKILLS_ROOT.rglob("*.py"))):
            py_compile.compile(
                script,
                cfile=bytecode_root / f"{index}.pyc",
                doraise=True,
            )

    print(f"Validated {len(EXPECTED_SKILLS)} skills and all Python sources.")


if __name__ == "__main__":
    main()
