#!/usr/bin/env python3
"""Validate the structure, metadata, and local links of bundled Codex skills."""

from __future__ import annotations

import py_compile
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EXPECTED_SKILLS = {
    "adversarial-review",
    "deep-plan",
    "harvest-agent-branches",
    "reasoning-codebase-review",
    "steward-brownfield",
    "trace-data-provenance",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN = MarkdownIt("commonmark")


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[object, object]:
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_yaml(text: str, source: Path) -> object:
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        fail(f"{display_path(source)} has invalid YAML: {error}")


def split_skill(skill_file: Path) -> tuple[dict[str, object], str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail(f"{display_path(skill_file)} does not start with YAML frontmatter")

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing_index is None:
        fail(f"{display_path(skill_file)} has incomplete YAML frontmatter")

    metadata = load_yaml("".join(lines[1:closing_index]), skill_file)
    if not isinstance(metadata, dict):
        fail(f"{display_path(skill_file)} frontmatter must be a YAML mapping")
    return metadata, "".join(lines[closing_index + 1 :])


def validate_local_links(skill_directory: Path) -> None:
    skill_root = skill_directory.resolve()
    for markdown_file in sorted(skill_directory.rglob("*.md")):
        text = markdown_file.read_text(encoding="utf-8")
        targets: list[str] = []
        for token in MARKDOWN.parse(text):
            for child in token.children or []:
                if child.type == "link_open":
                    target = child.attrGet("href")
                elif child.type == "image":
                    target = child.attrGet("src")
                else:
                    continue
                if target:
                    targets.append(target)

        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (markdown_file.parent / unquote(parsed.path)).resolve()
            try:
                resolved.relative_to(skill_root)
            except ValueError:
                fail(
                    f"{display_path(markdown_file)} links outside its skill package: "
                    f"{target!r}"
                )
            if not resolved.exists():
                fail(
                    f"{display_path(markdown_file)} links to missing local target "
                    f"{target!r}"
                )


def validate_agent_metadata(skill_directory: Path) -> None:
    metadata_file = skill_directory / "agents" / "openai.yaml"
    if not metadata_file.exists():
        return
    metadata = load_yaml(metadata_file.read_text(encoding="utf-8"), metadata_file)
    if not isinstance(metadata, dict):
        fail(f"{display_path(metadata_file)} must be a YAML mapping")

    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        fail(f"{display_path(metadata_file)} requires an interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        value = interface.get(field)
        if not isinstance(value, str) or not value.strip():
            fail(f"{display_path(metadata_file)} requires a non-empty {field}")
    short_description = interface["short_description"].strip()
    if not 25 <= len(short_description) <= 64:
        fail(f"{display_path(metadata_file)} short_description must be 25-64 characters")
    if f"${skill_directory.name}" not in interface["default_prompt"]:
        fail(
            f"{display_path(metadata_file)} default_prompt must mention "
            f"${skill_directory.name}"
        )


def validate_skill(directory: Path) -> None:
    skill_file = directory / "SKILL.md"
    if not skill_file.is_file():
        fail(f"missing {display_path(skill_file)}")

    metadata, body = split_skill(skill_file)
    unexpected_fields = set(metadata) - {"name", "description"}
    if unexpected_fields:
        fail(
            f"{display_path(skill_file)} has unexpected frontmatter fields: "
            f"{sorted(unexpected_fields)}"
        )

    name = metadata.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        fail(f"{display_path(skill_file)} has no valid hyphen-case name")
    if name != directory.name:
        fail(f"{display_path(skill_file)} name does not match its directory")

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        fail(f"{display_path(skill_file)} has no non-empty description")
    if len(description) > 1024:
        fail(f"{display_path(skill_file)} description exceeds 1024 characters")
    if not body.strip():
        fail(f"{display_path(skill_file)} has an empty instruction body")

    validate_local_links(directory)
    validate_agent_metadata(directory)
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
