from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from scripts import validate_skills


class SkillValidatorTests(unittest.TestCase):
    def make_skill(
        self,
        root: Path,
        frontmatter: str = "name: demo-skill\ndescription: A useful demo skill.",
        body: str = "# Demo\n\nFollow the instructions.\n",
    ) -> Path:
        directory = root / "demo-skill"
        directory.mkdir()
        (directory / "SKILL.md").write_text(
            f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8"
        )
        return directory

    def assert_invalid(self, directory: Path) -> None:
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            validate_skills.validate_skill(directory)

    def test_accepts_valid_minimal_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with redirect_stdout(StringIO()):
                validate_skills.validate_skill(
                    self.make_skill(Path(temporary_directory))
                )

    def test_rejects_empty_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                frontmatter='name: demo-skill\ndescription: ""',
            )
            self.assert_invalid(directory)

    def test_rejects_malformed_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                frontmatter='name: "demo-skill\ndescription: broken',
            )
            self.assert_invalid(directory)

    def test_rejects_duplicate_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                frontmatter=(
                    "name: demo-skill\n"
                    "name: shadow-name\n"
                    "description: A useful demo skill."
                ),
            )
            self.assert_invalid(directory)

    def test_rejects_missing_local_markdown_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                body="# Demo\n\nRead [the contract](references/contract.md).\n",
            )
            self.assert_invalid(directory)

    def test_rejects_link_outside_skill_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "outside.md").write_text("outside\n", encoding="utf-8")
            directory = self.make_skill(
                root,
                body="# Demo\n\nRead [outside](../outside.md).\n",
            )
            self.assert_invalid(directory)

    def test_rejects_missing_reference_style_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                body=(
                    "# Demo\n\nRead [the contract][contract].\n\n"
                    "[contract]: references/missing.md\n"
                ),
            )
            self.assert_invalid(directory)

    def test_accepts_balanced_parentheses_in_link_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                body="# Demo\n\nRead [version two](contract_(v2).md).\n",
            )
            (directory / "contract_(v2).md").write_text(
                "# Contract\n", encoding="utf-8"
            )
            with redirect_stdout(StringIO()):
                validate_skills.validate_skill(directory)

    def test_ignores_link_examples_in_fenced_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(
                Path(temporary_directory),
                body=(
                    "# Demo\n\n"
                    "```markdown\n[example](not-a-dependency.md)\n```\n"
                ),
            )
            with redirect_stdout(StringIO()):
                validate_skills.validate_skill(directory)

    def test_rejects_agent_prompt_without_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = self.make_skill(Path(temporary_directory))
            agents = directory / "agents"
            agents.mkdir()
            (agents / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Demo Skill"\n'
                '  short_description: "Perform one carefully bounded demo task"\n'
                '  default_prompt: "Run the demo now."\n',
                encoding="utf-8",
            )
            self.assert_invalid(directory)


if __name__ == "__main__":
    unittest.main()
