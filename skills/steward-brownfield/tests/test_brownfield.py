from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "brownfield.py"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
from brownfield_core import BrownfieldError, _source_fingerprint  # noqa: E402


class BrownfieldCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        self.repo = self.workspace / "repo"
        self.inputs = self.workspace / "inputs"
        self.repo.mkdir()
        self.inputs.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Brownfield Tests")
        self.git("config", "user.email", "brownfield-tests@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "primary.txt").write_text("primary v1\n", encoding="utf-8")
        (self.repo / "src" / "unrelated.txt").write_text("unrelated v1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("# Fixture\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "initial source")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=20,
        )
        if result.returncode:
            self.fail(
                f"git {' '.join(args)} failed with {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def invoke(self, *args: object, json_output: bool = True) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(CLI)]
        if json_output:
            command.append("--json")
        command.extend(str(arg) for arg in args)
        return subprocess.run(
            command,
            cwd=self.repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=30,
        )

    def invoke_json(self, *args: object, expected: int = 0) -> dict[str, Any]:
        result = self.invoke(*args)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"CLI did not emit JSON for {' '.join(map(str, args))}: {exc}\n"
                f"return code: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        self.assertEqual(
            expected,
            result.returncode,
            f"CLI return code mismatch for {' '.join(map(str, args))}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIsInstance(payload, dict)
        return payload

    def init_memory(self) -> dict[str, Any]:
        return self.invoke_json("init", "--root", self.repo, "--name", "Fixture")

    def begin_discovery(self) -> str:
        payload = self.invoke_json(
            "begin",
            "--root",
            self.repo,
            "--mode",
            "DISCOVERY",
            "--objective",
            "Understand the fixture",
            "--scope",
            "Read-only repository reconnaissance",
        )
        return payload["run_id"]

    def begin_source_writing(
        self,
        *,
        forbidden_path: str | None = None,
        required_check: str | None = None,
    ) -> str:
        args: list[object] = [
            "begin",
            "--root",
            self.repo,
            "--mode",
            "IMPROVE",
            "--objective",
            "Make one bounded source change",
            "--scope",
            "Only files below src",
            "--authorize-source-writes",
            "--allow-path",
            "src",
        ]
        if forbidden_path:
            args.extend(["--forbid-path", forbidden_path])
        if required_check:
            args.extend(["--required-check", required_check])
        return self.invoke_json(*args)["run_id"]

    def checkpoint(
        self,
        run_id: str,
        stage: str,
        *,
        check: str | None = None,
    ) -> dict[str, Any]:
        args: list[object] = [
            "checkpoint",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--stage",
            stage,
            "--summary",
            f"Reached {stage} in the fixture",
        ]
        if check:
            args.extend(["--check", check])
        return self.invoke_json(*args)

    def verify(self, run_id: str, name: str, *command: str) -> dict[str, Any]:
        return self.invoke_json(
            "verify", "--root", self.repo, "--run", run_id,
            "--name", name, "--", *command,
        )

    def advance_source_run_to_merging(self, run_id: str, *, check: str | None = None) -> None:
        for stage in ["INVESTIGATING", "CHANGING", "VALIDATING", "REVIEWING"]:
            self.checkpoint(run_id, stage)
        self.checkpoint(run_id, "MERGING", check=check)

    def contribution(
        self,
        run_id: str,
        *,
        agent: str,
        task: str,
        title: str,
        statement: str,
        classification: str = "INFERENCE",
        risk: str = "LOW",
    ) -> dict[str, Any]:
        payload = self.invoke_json(
            "contribution-template",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--agent",
            agent,
            "--task",
            task,
            "--record-type",
            "claim",
            "--title",
            title,
            "--statement",
            statement,
            "--classification",
            classification,
            "--risk",
            risk,
        )
        payload["sensitivity_review"]["completed"] = True
        return payload

    def record_template(
        self,
        run_id: str,
        *,
        title: str,
        statement: str,
        classification: str,
    ) -> dict[str, Any]:
        return self.invoke_json(
            "record-template",
            "--record-type",
            "claim",
            "--title",
            title,
            "--statement",
            statement,
            "--classification",
            classification,
            "--actor",
            "test-agent",
            "--run",
            run_id,
        )

    def write_input(self, name: str, value: dict[str, Any]) -> Path:
        path = self.inputs / name
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def stage(self, run_id: str, name: str, value: dict[str, Any]) -> None:
        source = self.write_input(name, value)
        result = self.invoke_json("stage", "--root", self.repo, "--run", run_id, "--input", source)
        self.assertEqual("STAGED", result["status"])

    def merge(self, run_id: str, contribution_id: str) -> dict[str, Any]:
        return self.invoke_json(
            "merge",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--contribution",
            contribution_id,
            "--reviewed-by",
            "test-coordinator",
        )

    def source_files(self) -> dict[str, bytes]:
        result: dict[str, bytes] = {}
        for path in sorted(self.repo.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(self.repo)
            if relative.parts[0] in {".git", ".brownfield"}:
                continue
            result[relative.as_posix()] = path.read_bytes()
        return result

    @staticmethod
    def sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_init_refuses_overwrite_without_changing_source_files(self) -> None:
        before = self.source_files()

        first = self.init_memory()

        self.assertEqual("INITIALIZED", first["status"])
        self.assertEqual(before, self.source_files())
        second = self.invoke_json("init", "--root", self.repo, "--name", "Again", expected=2)
        self.assertIn("Refusing to overwrite", second["error"])
        self.assertEqual(before, self.source_files())

    def test_generated_render_is_byte_identical(self) -> None:
        self.init_memory()
        generated = self.repo / ".brownfield" / "generated"
        paths = [generated / "index.json", generated / "freshness.json", generated / "HANDOFF.md"]

        self.invoke_json("render", "--root", self.repo)
        first = {path.name: path.read_bytes() for path in paths}
        self.invoke_json("render", "--root", self.repo)
        second = {path.name: path.read_bytes() for path in paths}

        self.assertEqual(first, second)

    def test_memory_only_commit_preserves_source_digest(self) -> None:
        self.init_memory()
        before = self.invoke_json("snapshot", "--root", self.repo)["repositories"][0]

        self.git("add", ".brownfield")
        self.git("commit", "-q", "-m", "checkpoint project memory")
        after = self.invoke_json("snapshot", "--root", self.repo)["repositories"][0]

        self.assertNotEqual(before["commit"], after["commit"])
        self.assertEqual(before["source_digest"], after["source_digest"])

    def test_discovery_rejects_source_write_authorization_mismatch(self) -> None:
        self.init_memory()

        result = self.invoke(
            "begin",
            "--root",
            self.repo,
            "--mode",
            "DISCOVERY",
            "--objective",
            "Read only",
            "--scope",
            "Repository",
            "--authorize-source-writes",
        )

        self.assertEqual(
            2,
            result.returncode,
            "DISCOVERY accepted --authorize-source-writes and created an unsafe contradictory run envelope",
        )
        payload = json.loads(result.stdout)
        self.assertIn("DISCOVERY", payload["error"])

    def test_merge_accepts_one_contribution_and_rejects_stale_competitor(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        first = self.contribution(
            run_id,
            agent="agent-one",
            task="task-one",
            title="First observation",
            statement="The first observation is bounded.",
        )
        second = self.contribution(
            run_id,
            agent="agent-two",
            task="task-two",
            title="Competing observation",
            statement="This proposal was prepared against the same base.",
        )
        self.stage(run_id, "first.json", first)
        self.stage(run_id, "second.json", second)

        accepted = self.merge(run_id, first["contribution_id"])
        stale = self.invoke_json(
            "merge",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--contribution",
            second["contribution_id"],
            "--reviewed-by",
            "test-coordinator",
            expected=2,
        )

        self.assertEqual("ACCEPTED", accepted["status"])
        self.assertIn("Stale contribution base revision", stale["error"])
        records = list((self.repo / ".brownfield" / "records" / "claims").glob("*.json"))
        self.assertEqual([first["operations"][0]["record"]["id"]], [path.stem for path in records])

    def test_changed_evidence_stales_target_and_dependant_only(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id,
            agent="mapper",
            task="map-evidence",
            title="Primary source claim",
            statement="Primary source content is v1.",
            classification="FACT",
        )
        snapshot = contribution["source_snapshot"]
        primary_path = self.repo / "src" / "primary.txt"
        unrelated_path = self.repo / "src" / "unrelated.txt"

        primary = contribution["operations"][0]["record"]
        dependant = self.record_template(
            run_id,
            title="Derived claim",
            statement="This conclusion depends on the primary source claim.",
            classification="INFERENCE",
        )
        unrelated = self.record_template(
            run_id,
            title="Unrelated claim",
            statement="The unrelated source content is v1.",
            classification="FACT",
        )
        primary_evidence = {
            "evidence_id": "evd-primary",
            "kind": "CODE",
            "relationship": "SUPPORTS",
            "repo": "primary",
            "path": "src/primary.txt",
            "content_sha256": self.sha256(primary_path),
            "captured_at": primary["created_at"],
            "run_id": run_id,
            "redaction_status": "REVIEWED",
        }
        unrelated_evidence = {
            "evidence_id": "evd-unrelated",
            "kind": "CODE",
            "relationship": "SUPPORTS",
            "repo": "primary",
            "path": "src/unrelated.txt",
            "content_sha256": self.sha256(unrelated_path),
            "captured_at": unrelated["created_at"],
            "run_id": run_id,
            "redaction_status": "REVIEWED",
        }
        for record, confidence in [(primary, "HIGH"), (dependant, "MEDIUM"), (unrelated, "HIGH")]:
            record["knowledge_status"] = "CURRENT"
            record["workflow_status"] = "CONFIRMED"
            record["confidence"] = confidence
            record["verification"] = {
                "snapshot": snapshot,
                "method": "fixture inspection",
                "verified_at": record["created_at"],
                "verified_by": "test-agent",
            }
        primary["evidence"] = [primary_evidence]
        dependant["depends_on"]["records"] = [primary["id"]]
        unrelated["evidence"] = [unrelated_evidence]
        contribution["operations"] = [
            {"action": "CREATE", "expected_revision": None, "record": primary},
            {"action": "CREATE", "expected_revision": None, "record": dependant},
            {"action": "CREATE", "expected_revision": None, "record": unrelated},
        ]
        self.stage(run_id, "evidence-map.json", contribution)
        self.merge(run_id, contribution["contribution_id"])

        primary_path.write_text("primary v2\n", encoding="utf-8")
        dry_run = self.invoke_json("refresh", "--root", self.repo)

        self.assertEqual({primary["id"], dependant["id"]}, set(dry_run["stale_candidates"]))
        self.assertNotIn(unrelated["id"], dry_run["stale_candidates"])
        applied = self.invoke_json("refresh", "--root", self.repo, "--run", run_id, "--apply")
        self.assertEqual("ACCEPTED", applied["status"])
        claim_dir = self.repo / ".brownfield" / "records" / "claims"
        self.assertEqual("STALE", json.loads((claim_dir / f"{primary['id']}.json").read_text())["knowledge_status"])
        self.assertEqual("STALE", json.loads((claim_dir / f"{dependant['id']}.json").read_text())["knowledge_status"])
        self.assertEqual("CURRENT", json.loads((claim_dir / f"{unrelated['id']}.json").read_text())["knowledge_status"])

    def test_context_honors_character_budget(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id,
            agent="context-author",
            task="large-context",
            title="Large bounded record",
            statement="x" * 4_800,
        )
        self.stage(run_id, "large.json", contribution)
        self.merge(run_id, contribution["contribution_id"])
        record_id = contribution["operations"][0]["record"]["id"]
        budget = 2_200

        result = self.invoke(
            "context",
            "--root",
            self.repo,
            "--mission",
            "Inspect one large record",
            "--record",
            record_id,
            "--max-chars",
            budget,
            json_output=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertLessEqual(len(result.stdout), budget)
        self.assertIn(f"Omitted record IDs: {record_id}", result.stdout)

    def test_incomplete_transaction_requires_recovery(self) -> None:
        self.init_memory()
        transaction = self.repo / ".brownfield" / "runtime" / "transactions" / "interrupted.json"
        transaction.write_text("{}\n", encoding="utf-8")

        validation = self.invoke_json("validate", "--root", self.repo, "--strict", expected=1)
        status = self.invoke_json("status", "--root", self.repo)

        self.assertTrue(any("Incomplete memory transaction" in error for error in validation["errors"]))
        self.assertEqual("RECOVERY_REQUIRED", status["classification"])
        self.assertEqual(["interrupted.json"], status["transactions"])

    def test_recover_refuses_structurally_incomplete_transaction(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        state_path = self.repo / ".brownfield" / "state.json"
        state_before = json.loads(state_path.read_text(encoding="utf-8"))
        transaction = {
            "schema_version": 1,
            "transaction_id": "sub-corrupt",
            "status": "PREPARED",
            "created_at": "not-a-timestamp",
            "before_records": {},
            "after_records": {},
            "state_before": {"memory_revision": 0},
            "state_after": {"memory_revision": 1},
            "event": {
                "kind": "CONTRIBUTION_ACCEPTED",
                "run_id": run_id,
                "contribution_id": "sub-corrupt",
            },
        }
        target = self.repo / ".brownfield" / "runtime" / "transactions" / "sub-corrupt.json"
        target.write_text(json.dumps(transaction), encoding="utf-8")

        result = self.invoke_json("recover", "--root", self.repo, expected=2)

        self.assertIn("Invalid memory transaction", result["error"])
        self.assertEqual(state_before, json.loads(state_path.read_text(encoding="utf-8")))

    def test_begin_rejects_secret_without_creating_run(self) -> None:
        self.init_memory()
        state_path = self.repo / ".brownfield" / "state.json"
        state_before = state_path.read_bytes()
        fake_secret = "password=" + "not-a-real-password-123"

        rejected = self.invoke_json(
            "begin",
            "--root",
            self.repo,
            "--mode",
            "DISCOVERY",
            "--objective",
            fake_secret,
            "--scope",
            "Read-only repository inspection",
            expected=2,
        )

        self.assertIn("sensitivity scan", rejected["error"])
        self.assertEqual(state_before, state_path.read_bytes())
        self.assertEqual([], list((self.repo / ".brownfield" / "runs").glob("*/run.json")))
        self.assertEqual("READY", self.invoke_json("status", "--root", self.repo)["classification"])

    def test_slack_token_contribution_is_rejected_before_staging(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id,
            agent="sensitivity-agent",
            task="sensitivity-test",
            title="Sensitive proposal",
            statement="This starts harmlessly.",
        )
        contribution["operations"][0]["record"]["statement"] = (
            "Accidentally retained " + "xoxb-" + "1234567890-abcdefghijkl"
        )
        source = self.write_input("sensitive.json", contribution)

        rejected = self.invoke_json(
            "stage",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--input",
            source,
            expected=2,
        )

        self.assertIn("sensitivity scan", rejected["error"])
        staged = self.repo / ".brownfield" / "runs" / run_id / "contributions"
        self.assertEqual([], list(staged.glob("*.json")))

    def test_malformed_source_snapshot_is_rejected_cleanly(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id,
            agent="snapshot-agent",
            task="snapshot-test",
            title="Malformed snapshot proposal",
            statement="The snapshot is deliberately malformed.",
        )
        contribution["source_snapshot"] = "not-a-snapshot"
        source = self.write_input("malformed-snapshot.json", contribution)

        result = self.invoke(
            "stage",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--input",
            source,
        )

        self.assertEqual(2, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("schema $.source_snapshot", payload["error"])
        self.assertIn("not of type 'object'", payload["error"])
        self.assertNotIn("Traceback", result.stderr)
        staged = self.repo / ".brownfield" / "runs" / run_id / "contributions"
        self.assertEqual([], list(staged.glob("*.json")))

    def test_moderate_contribution_cannot_exceed_low_run_ceiling(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id,
            agent="risk-agent",
            task="risk-test",
            title="Moderate proposal",
            statement="This proposal exceeds the run ceiling.",
            risk="MODERATE",
        )
        record_id = contribution["operations"][0]["record"]["id"]
        self.stage(run_id, "moderate.json", contribution)

        rejected = self.invoke_json(
            "merge",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--contribution",
            contribution["contribution_id"],
            "--reviewed-by",
            "test-coordinator",
            expected=2,
        )

        self.assertIn("exceeds run ceiling LOW", rejected["error"])
        record = self.repo / ".brownfield" / "records" / "claims" / f"{record_id}.json"
        self.assertFalse(record.exists())

    def test_finish_requires_fresh_merging_checkpoint_and_required_check(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(required_check="fixture-check")
        self.advance_source_run_to_merging(run_id, check="fixture-check")
        summary = self.inputs / "summary.md"
        summary.write_text("Verified the bounded source change.\n", encoding="utf-8")

        (self.repo / "src" / "primary.txt").write_text("primary v2\n", encoding="utf-8")
        stale_checkpoint = self.invoke_json(
            "finish",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("source changed after the final checkpoint", stale_checkpoint["error"])

        self.checkpoint(run_id, "MERGING")
        missing_check = self.invoke_json(
            "finish",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("Required verification receipts are missing", missing_check["error"])

        receipt = self.verify(run_id, "fixture-check", sys.executable, "-c", "print('ok')")
        self.assertEqual("PASS", receipt["result"])
        self.checkpoint(run_id, "MERGING")
        finished = self.invoke_json(
            "finish",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--summary-file",
            summary,
        )
        self.assertEqual("COMPLETE", finished["status"])

    def test_finish_rejects_changes_to_forbidden_path(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(
            forbidden_path="src/unrelated.txt",
            required_check="fixture-check",
        )
        (self.repo / "src" / "unrelated.txt").write_text("forbidden v2\n", encoding="utf-8")
        receipt = self.verify(
            run_id, "fixture-check", sys.executable, "-c", "print('ok')"
        )
        self.assertEqual("PASS", receipt["result"])
        self.advance_source_run_to_merging(run_id)
        summary = self.inputs / "forbidden-summary.md"
        summary.write_text("Checked the source-writing run.\n", encoding="utf-8")

        rejected = self.invoke_json(
            "finish",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--summary-file",
            summary,
            expected=2,
        )

        self.assertIn("touches a forbidden path", rejected["error"])
        state = json.loads((self.repo / ".brownfield" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(run_id, state["active_run_id"])

    def test_abort_preserves_failed_run_evidence_and_allows_explicit_successor(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(
            forbidden_path="src/unrelated.txt",
            required_check="live-release-check",
        )
        (self.repo / "src" / "unrelated.txt").write_text("forbidden v2\n", encoding="utf-8")
        self.advance_source_run_to_merging(run_id)
        summary = self.inputs / "abort-summary.md"
        summary.write_text(
            "The required live release check failed. Preserve the current source and use a successor run.\n",
            encoding="utf-8",
        )
        source_before = self.source_files()
        state_before = json.loads((self.repo / ".brownfield" / "state.json").read_text(encoding="utf-8"))

        finish = self.invoke_json(
            "finish",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("Required verification receipts are missing", finish["error"])

        proposal = self.contribution(
            run_id,
            agent="test-agent",
            task="observe-live-failure",
            title="Retain the failed observation",
            statement="The required live release check did not pass.",
        )
        self.stage(run_id, "pending-abort-contribution.json", proposal)
        pending_paths = list(
            (self.repo / ".brownfield" / "runs" / run_id / "contributions").glob(
                f"*-{proposal['contribution_id']}.json"
            )
        )
        self.assertEqual(1, len(pending_paths))
        pending_path = pending_paths[0]

        aborted = self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            summary,
        )

        self.assertEqual("ABORTED", aborted["status"])
        self.assertTrue(aborted["successor_required"])
        self.assertTrue(any("touches a forbidden path" in item for item in aborted["source_envelope_violations"]))
        self.assertEqual(source_before, self.source_files())
        self.assertTrue(pending_path.is_file())
        state = json.loads((self.repo / ".brownfield" / "state.json").read_text(encoding="utf-8"))
        self.assertIsNone(state["active_run_id"])
        self.assertEqual(state_before["last_completed_run_id"], state["last_completed_run_id"])
        self.assertEqual(state_before["last_snapshot"], state["last_snapshot"])
        run = json.loads((self.repo / ".brownfield" / "runs" / run_id / "run.json").read_text(encoding="utf-8"))
        self.assertEqual("ABORTED", run["status"])
        self.assertEqual("MERGING", run["stage"])
        self.assertIsNone(run["final_snapshot"])
        event_path = self.repo / ".brownfield" / "runs" / run_id / "events" / f"run-aborted-{run_id}.json"
        event = json.loads(event_path.read_text(encoding="utf-8"))
        self.assertEqual("live-release-check", event["failed_required_check"])
        self.assertEqual(
            self.sha256(self.repo / ".brownfield" / "runs" / run_id / "abort.md"),
            event["abort_summary"]["sha256"],
        )
        validation = self.invoke_json("validate", "--root", self.repo, "--strict")
        self.assertEqual([], validation["errors"])
        self.assertEqual([], validation["warnings"])

        second_abort = self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("No active run", second_abort["error"])
        self.assertEqual(event, json.loads(event_path.read_text(encoding="utf-8")))

        successor = self.begin_source_writing(required_check="corrected-live-release-check")
        self.assertNotEqual(run_id, successor)

    def test_abort_rejects_invalid_inputs_and_incomplete_transaction_without_mutation(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(required_check="live-release-check")
        state_path = self.repo / ".brownfield" / "state.json"
        run_path = self.repo / ".brownfield" / "runs" / run_id / "run.json"
        summary = self.inputs / "abort-summary.md"
        summary.write_text("The required live check failed.\n", encoding="utf-8")
        state_before = state_path.read_bytes()
        run_before = run_path.read_bytes()

        unknown = self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "not-required",
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("exactly match", unknown["error"])

        secret_summary = self.inputs / "secret-abort.md"
        secret_summary.write_text("password=not-a-real-password-123\n", encoding="utf-8")
        sensitive = self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            secret_summary,
            expected=2,
        )
        self.assertIn("sensitivity scan", sensitive["error"])

        transaction = self.repo / ".brownfield" / "runtime" / "transactions" / "interrupted.json"
        transaction.write_text("{}\n", encoding="utf-8")
        interrupted = self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            summary,
            expected=2,
        )
        self.assertIn("recover it before aborting", interrupted["error"])
        self.assertEqual(state_before, state_path.read_bytes())
        self.assertEqual(run_before, run_path.read_bytes())
        self.assertFalse((self.repo / ".brownfield" / "runs" / run_id / "abort.md").exists())

    def test_recover_clears_only_stale_pointer_to_valid_aborted_run(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(required_check="live-release-check")
        summary = self.inputs / "abort-summary.md"
        summary.write_text("The required live check failed.\n", encoding="utf-8")
        self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            summary,
        )
        state_path = self.repo / ".brownfield" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        last_completed_before = state["last_completed_run_id"]
        last_snapshot_before = state["last_snapshot"]
        state["active_run_id"] = run_id
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        recovered = self.invoke_json("recover", "--root", self.repo)

        self.assertEqual("RECONCILED_ABORTED_RUN", recovered["status"])
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertIsNone(state["active_run_id"])
        self.assertEqual(last_completed_before, state["last_completed_run_id"])
        self.assertEqual(last_snapshot_before, state["last_snapshot"])
        validation = self.invoke_json("validate", "--root", self.repo, "--strict")
        self.assertEqual([], validation["errors"])
        self.assertEqual([], validation["warnings"])

    def test_partial_abort_blocks_run_mutation_and_recover_finishes_exact_event(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(required_check="live-release-check")
        summary = self.inputs / "abort-summary.md"
        summary.write_text("The required live check failed.\n", encoding="utf-8")
        self.invoke_json(
            "abort",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--failed-required-check",
            "live-release-check",
            "--summary-file",
            summary,
        )
        run_path = self.repo / ".brownfield" / "runs" / run_id / "run.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run["status"] = "ACTIVE"
        run.pop("completed_at")
        run.pop("final_memory_revision")
        run_path.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        state_path = self.repo / ".brownfield" / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["active_run_id"] = run_id
        state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        event_path = self.repo / ".brownfield" / "runs" / run_id / "events" / f"run-aborted-{run_id}.json"
        event_before = event_path.read_bytes()

        validation = self.invoke_json("validate", "--root", self.repo, "--strict", expected=1)
        self.assertTrue(any("partial abort artifacts" in error for error in validation["errors"]))
        blocked = self.invoke_json(
            "checkpoint",
            "--root",
            self.repo,
            "--run",
            run_id,
            "--stage",
            "INVESTIGATING",
            "--summary",
            "Must not mutate a partially aborted run",
            expected=2,
        )
        self.assertIn("partial abort artifacts", blocked["error"])

        recovered = self.invoke_json("recover", "--root", self.repo)

        self.assertEqual("RECONCILED_PARTIAL_ABORT", recovered["status"])
        self.assertEqual(event_before, event_path.read_bytes())
        run = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual("ABORTED", run["status"])
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertIsNone(state["active_run_id"])
        validation = self.invoke_json("validate", "--root", self.repo, "--strict")
        self.assertEqual([], validation["errors"])
        self.assertEqual([], validation["warnings"])

    def test_context_output_cannot_escape_runtime_context(self) -> None:
        self.init_memory()

        rejected = self.invoke_json(
            "context",
            "--root",
            self.repo,
            "--mission",
            "Create a bounded context package",
            "--output",
            "../escaped.md",
            expected=2,
        )

        self.assertIn("Unsafe relative path", rejected["error"])
        self.assertFalse((self.repo / ".brownfield" / "runtime" / "escaped.md").exists())

    def test_unversioned_source_drift_invalidates_merge(self) -> None:
        unversioned = self.workspace / "unversioned"
        unversioned.mkdir()
        source_path = unversioned / "source.txt"
        source_path.write_text("version one\n", encoding="utf-8")
        self.invoke_json("init", "--root", unversioned, "--name", "Unversioned Fixture")
        begin = self.invoke_json(
            "begin",
            "--root",
            unversioned,
            "--mode",
            "DISCOVERY",
            "--objective",
            "Inspect unversioned source",
            "--scope",
            "The complete fixture",
        )
        run_id = begin["run_id"]
        contribution = self.invoke_json(
            "contribution-template",
            "--root",
            unversioned,
            "--run",
            run_id,
            "--agent",
            "unversioned-agent",
            "--task",
            "drift-test",
            "--record-type",
            "claim",
            "--title",
            "Unversioned observation",
            "--statement",
            "The source contains version one.",
            "--classification",
            "INFERENCE",
        )
        contribution["sensitivity_review"]["completed"] = True
        proposal = self.write_input("unversioned.json", contribution)
        self.invoke_json(
            "stage",
            "--root",
            unversioned,
            "--run",
            run_id,
            "--input",
            proposal,
        )

        source_path.write_text("version two\n", encoding="utf-8")
        rejected = self.invoke_json(
            "merge",
            "--root",
            unversioned,
            "--run",
            run_id,
            "--contribution",
            contribution["contribution_id"],
            "--reviewed-by",
            "test-coordinator",
            expected=2,
        )

        self.assertIn("Repository source changed", rejected["error"])
        record_id = contribution["operations"][0]["record"]["id"]
        record = unversioned / ".brownfield" / "records" / "claims" / f"{record_id}.json"
        self.assertFalse(record.exists())


    def test_source_glob_rejects_symlink_escape(self) -> None:
        external = self.workspace / "external.txt"
        external.write_text("outside\n", encoding="utf-8")
        link = self.repo / "src" / "external-link.txt"
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation is unavailable")
        with self.assertRaises(BrownfieldError):
            _source_fingerprint(self.repo, {"glob": "src/*.txt"})

    def test_context_expands_transitive_dependencies_before_dependant(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id, agent="context-agent", task="dependency-closure",
            title="Root record", statement="Root depends on the middle record.",
        )
        root_record = contribution["operations"][0]["record"]
        middle = self.record_template(
            run_id, title="Middle record",
            statement="Middle depends on the leaf record.", classification="INFERENCE",
        )
        leaf = self.record_template(
            run_id, title="Leaf record",
            statement="Leaf contains the foundational evidence.", classification="INFERENCE",
        )
        root_record["depends_on"]["records"] = [middle["id"]]
        middle["depends_on"]["records"] = [leaf["id"]]
        contribution["operations"] = [
            {"action": "CREATE", "expected_revision": None, "record": root_record},
            {"action": "CREATE", "expected_revision": None, "record": middle},
            {"action": "CREATE", "expected_revision": None, "record": leaf},
        ]
        self.stage(run_id, "transitive-context.json", contribution)
        self.merge(run_id, contribution["contribution_id"])
        result = self.invoke(
            "context", "--root", self.repo, "--mission", "Inspect dependency closure",
            "--record", root_record["id"], "--max-chars", 20000, json_output=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertLess(result.stdout.index(leaf["id"]), result.stdout.index(middle["id"]))
        self.assertLess(result.stdout.index(middle["id"]), result.stdout.index(root_record["id"]))
        self.assertIn("Dependency closure complete: yes", result.stdout)

    def test_schema_rejects_unexpected_record_property(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        contribution = self.contribution(
            run_id, agent="schema-agent", task="schema-test",
            title="Invalid record", statement="This record contains an unexpected field.",
        )
        contribution["operations"][0]["record"]["unexpected"] = True
        source = self.write_input("invalid-schema.json", contribution)
        result = self.invoke_json(
            "stage", "--root", self.repo, "--run", run_id,
            "--input", source, expected=2,
        )
        self.assertIn("Additional properties are not allowed", result["error"])

    def test_read_only_run_rejects_source_drift_at_finish(self) -> None:
        self.init_memory()
        run_id = self.begin_discovery()
        (self.repo / "src" / "primary.txt").write_text("changed\n", encoding="utf-8")
        for stage in ["INVESTIGATING", "VALIDATING", "REVIEWING", "MERGING"]:
            self.checkpoint(run_id, stage)
        summary = self.inputs / "read-only-summary.md"
        summary.write_text("Reviewed the repository.\n", encoding="utf-8")
        result = self.invoke_json(
            "finish", "--root", self.repo, "--run", run_id,
            "--summary-file", summary, expected=2,
        )
        self.assertIn("changed during a read-only run", result["error"])

    def test_verification_receipt_fails_closed_after_source_change(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing(required_check="fixture-check")
        receipt = self.verify(run_id, "fixture-check", sys.executable, "-c", "print('ok')")
        self.assertEqual("PASS", receipt["result"])
        (self.repo / "src" / "primary.txt").write_text(
            "changed after verification\n", encoding="utf-8"
        )
        self.advance_source_run_to_merging(run_id)
        summary = self.inputs / "stale-receipt-summary.md"
        summary.write_text("Attempted completion with a stale receipt.\n", encoding="utf-8")
        result = self.invoke_json(
            "finish", "--root", self.repo, "--run", run_id,
            "--summary-file", summary, expected=2,
        )
        self.assertIn("not current PASS results", result["error"])

    def test_tampered_copied_schema_is_rejected(self) -> None:
        self.init_memory()
        schema = self.repo / ".brownfield" / "schemas" / "record.schema.json"
        schema.write_text("{}\n", encoding="utf-8")

        result = self.invoke_json("validate", "--root", self.repo, "--strict", expected=1)

        self.assertTrue(
            any("Copied schema differs" in error for error in result["errors"]),
            result["errors"],
        )

    def test_verify_missing_executable_fails_cleanly(self) -> None:
        self.init_memory()
        run_id = self.begin_source_writing()

        result = self.invoke(
            "verify", "--root", self.repo, "--run", run_id,
            "--name", "missing-command", "--",
            "brownfield-command-that-does-not-exist-42",
        )

        self.assertEqual(2, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("Cannot start verification command", payload["error"])
        self.assertNotIn("Traceback", result.stderr)

if __name__ == "__main__":
    unittest.main()
