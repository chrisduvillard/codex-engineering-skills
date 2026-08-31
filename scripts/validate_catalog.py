#!/usr/bin/env python3
"""Validate catalog consistency and routing fixtures."""
from __future__ import annotations
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} has no frontmatter")
    value = yaml.safe_load(text.split("---", 2)[1])
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} frontmatter is not a mapping")
    return value


def main() -> None:
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text(encoding="utf-8"))
    entries = catalog.get("skills", {})
    discovered = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    if set(entries) != discovered:
        fail(f"catalog mismatch: {sorted(entries)} != {sorted(discovered)}")
    total = 0
    for name, entry in entries.items():
        metadata = frontmatter(SKILLS / name / "SKILL.md")
        description = metadata.get("description")
        if description != entry.get("description"):
            fail(f"{name}: catalog and SKILL.md descriptions differ")
        total += len(str(description))
        agent_path = SKILLS / name / "agents" / "openai.yaml"
        if not agent_path.is_file():
            fail(f"{name}: missing agents/openai.yaml")
        agent = yaml.safe_load(agent_path.read_text(encoding="utf-8"))
        actual = agent.get("policy", {}).get("allow_implicit_invocation")
        if actual is not entry.get("allow_implicit_invocation"):
            fail(f"{name}: invocation policy differs from catalog")
    budget = int(catalog.get("description_budget", 0))
    if total > budget:
        fail(f"description budget exceeded: {total} > {budget}")
    fixtures = yaml.safe_load((ROOT / "evals" / "routing.yaml").read_text(encoding="utf-8"))
    ids: set[str] = set()
    prompts: set[str] = set()
    for case in fixtures.get("cases", []):
        identifier = case.get("id")
        prompt = case.get("prompt")
        expected = case.get("expected")
        excluded = case.get("excluded", [])
        if not identifier or identifier in ids:
            fail(f"duplicate or empty routing id: {identifier!r}")
        if not prompt or prompt in prompts:
            fail(f"duplicate or empty routing prompt: {prompt!r}")
        if expected not in entries or expected in excluded or any(item not in entries for item in excluded):
            fail(f"{identifier}: invalid routing target or exclusion")
        ids.add(identifier)
        prompts.add(prompt)
    print(f"Validated {len(entries)} catalog entries and {len(ids)} routing cases.")
    print(f"Description budget: {total}/{budget} characters.")


if __name__ == "__main__":
    main()
