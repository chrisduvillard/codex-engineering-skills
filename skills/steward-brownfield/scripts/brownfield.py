#!/usr/bin/env python3
"""Command-line control plane for persistent brownfield project memory."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from brownfield_core import (
    BrownfieldError,
    MEMORY_NAME,
    RECORD_TYPES,
    RUN_STAGES,
    SCHEMA_VERSION,
    SOURCE_WRITE_MODES,
    WRITER_VERSION,
    atomic_write_json,
    atomic_write_text,
    build_context,
    canonical_json,
    changed_source_paths,
    hash_file,
    init_memory,
    known_stale_records,
    knowledge_digest,
    load_records,
    make_id,
    memory_path,
    normalize_mode,
    partial_abort_error,
    read_json,
    record_path,
    record_template,
    render_views,
    safe_child,
    secret_findings,
    semver_core,
    snapshot_vector,
    stale_records,
    utc_now,
    validate_contribution,
    validate_memory,
    validate_record,
)

AGENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
LOCK_MINUTES = 15
RISK_RANK = {"LOW": 0, "MODERATE": 1, "HIGH": 2}


def reject_sensitive(label: str, value: Any) -> None:
    findings = secret_findings(label, value)
    if findings:
        raise BrownfieldError(f"{label} failed sensitivity scan:\n- " + "\n- ".join(findings))


def path_within_any(path: str, roots: list[str]) -> bool:
    normalized = path.strip("/")
    return any(
        root.strip("/") in {"", "."}
        or normalized == root.strip("/")
        or normalized.startswith(root.strip("/") + "/")
        for root in roots
    )


def safe_relative_path(value: str) -> bool:
    candidate = Path(value)
    return bool(value) and "\\" not in value and not candidate.is_absolute() and ".." not in candidate.parts


def project_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise BrownfieldError(f"Project root does not exist: {root}")
    return root


def load_control(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    memory = memory_path(root)
    if not memory.exists():
        raise BrownfieldError(f"No {MEMORY_NAME} memory exists under {root}")
    manifest = read_json(memory / "manifest.json")
    policy = read_json(memory / "policy.json")
    state = read_json(memory / "state.json")
    for label, value in (("manifest", manifest), ("policy", policy), ("state", state)):
        if not isinstance(value, dict):
            raise BrownfieldError(f"{label}.json must contain a JSON object")
    if (
        manifest.get("schema_version") != SCHEMA_VERSION
        or policy.get("schema_version") != SCHEMA_VERSION
        or state.get("schema_version") != SCHEMA_VERSION
    ):
        raise BrownfieldError("Unsupported memory schema; remain read-only and migrate with a compatible writer")
    try:
        minimum = semver_core(manifest["minimum_writer_version"])
        writer = semver_core(WRITER_VERSION)
    except (KeyError, AttributeError, ValueError) as exc:
        raise BrownfieldError("Manifest has an invalid minimum_writer_version") from exc
    if minimum > writer:
        raise BrownfieldError(
            f"Memory requires writer {manifest['minimum_writer_version']}; current writer is {WRITER_VERSION}. Remain read-only."
        )
    if policy.get("canonical_writer") != "SINGLE_COORDINATOR":
        raise BrownfieldError("Policy canonical_writer must be SINGLE_COORDINATOR")
    for field, minimum_value in (("max_record_bytes", 1_024), ("default_context_max_chars", 2_000)):
        value = policy.get(field)
        if type(value) is not int or value < minimum_value:
            raise BrownfieldError(f"Policy {field} must be an integer of at least {minimum_value}")
    if policy.get("source_writes_require_explicit_authority") is not True:
        raise BrownfieldError("Policy must require explicit source-write authority")
    if type(state.get("memory_revision")) is not int or state["memory_revision"] < 0:
        raise BrownfieldError("State memory_revision must be a non-negative integer")
    for field in ("active_run_id", "last_completed_run_id"):
        value = state.get(field)
        if value is not None and (not isinstance(value, str) or not re.fullmatch(r"^[a-z][a-z0-9-]*$", value)):
            raise BrownfieldError(f"State {field} must be a valid run ID or null")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise BrownfieldError("Manifest repositories must be a non-empty list")
    repository_ids: set[str] = set()
    repository_uuids: set[str] = set()
    repository_paths: set[Path] = set()
    for repository in repositories:
        if not isinstance(repository, dict):
            raise BrownfieldError("Each manifest repository must be an object")
        required = {"id", "repository_uuid", "path", "role", "authority_branch", "remote_alias"}
        missing = required - repository.keys()
        if missing:
            raise BrownfieldError(f"Manifest repository is missing: {', '.join(sorted(missing))}")
        repository_id = repository.get("id")
        repository_uuid = repository.get("repository_uuid")
        repository_path = repository.get("path")
        if not isinstance(repository_id, str) or not AGENT_ID_RE.fullmatch(repository_id):
            raise BrownfieldError("Each manifest repository requires a valid string id")
        try:
            parsed_uuid = str(uuid.UUID(repository_uuid))
        except (AttributeError, TypeError, ValueError) as exc:
            raise BrownfieldError(f"Repository {repository_id} has an invalid repository_uuid") from exc
        if not isinstance(repository_path, str):
            raise BrownfieldError(f"Repository {repository_id} has a non-string path")
        resolved_path = safe_child(root, repository_path)
        if repository_id in repository_ids:
            raise BrownfieldError(f"Duplicate repository id: {repository_id}")
        if parsed_uuid in repository_uuids:
            raise BrownfieldError(f"Duplicate repository UUID: {parsed_uuid}")
        if resolved_path in repository_paths:
            raise BrownfieldError(f"Duplicate repository path: {repository_path}")
        repository_ids.add(repository_id)
        repository_uuids.add(parsed_uuid)
        repository_paths.add(resolved_path)
    return memory, manifest, policy, state


@contextmanager
def coordinator_lock(memory: Path, run_id: str, reclaim: bool = False) -> Iterator[None]:
    lock_path = memory / "runtime" / "locks" / "coordinator.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex

    def create() -> bool:
        payload = canonical_json({
            "token": token,
            "run_id": run_id,
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "created_at": utc_now(),
            "expires_at": (datetime.now(UTC) + timedelta(minutes=LOCK_MINUTES)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }).encode()
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return True

    if not create():
        existing: dict[str, Any] = {}
        well_formed = True
        try:
            candidate = read_json(lock_path)
            if not isinstance(candidate, dict):
                raise TypeError("lock must be an object")
            existing = candidate
            expiry = datetime.fromisoformat(existing["expires_at"].replace("Z", "+00:00"))
        except (BrownfieldError, KeyError, TypeError, ValueError):
            well_formed = False
            expiry = datetime.min.replace(tzinfo=UTC)
        if not reclaim or (well_formed and expiry >= datetime.now(UTC)):
            owner = existing.get("run_id", "unknown")
            raise BrownfieldError(f"Coordinator lock is held by {owner}; use --reclaim-lock only after verifying it is abandoned")
        if well_formed and existing.get("hostname") != socket.gethostname():
            raise BrownfieldError(
                "Expired coordinator lock belongs to another host and cannot be verified locally; "
                "coordinate with that host and remove the exact abandoned lock manually"
            )
        if existing.get("hostname") == socket.gethostname() and isinstance(existing.get("pid"), int):
            try:
                os.kill(existing["pid"], 0)
            except ProcessLookupError:
                pass
            except PermissionError as exc:
                raise BrownfieldError("Cannot verify whether the expired lock owner is alive; refusing reclamation") from exc
            else:
                raise BrownfieldError("Expired coordinator lock still belongs to a live local process; refusing split-brain reclamation")
        lock_path.unlink(missing_ok=True)
        if not create():
            raise BrownfieldError("Coordinator lock was acquired concurrently")
    try:
        yield
    finally:
        try:
            current = read_json(lock_path)
        except BrownfieldError:
            current = {}
        if current.get("token") == token:
            lock_path.unlink(missing_ok=True)


def active_run(
    memory: Path,
    state: dict[str, Any],
    expected: str | None = None,
    *,
    allow_partial_abort: bool = False,
) -> tuple[str, Path, dict[str, Any]]:
    run_id = state.get("active_run_id")
    if not run_id:
        raise BrownfieldError("No active run; begin one first")
    if expected and run_id != expected:
        raise BrownfieldError(f"Active run is {run_id}, not {expected}")
    path = safe_child(memory, f"runs/{run_id}/run.json")
    run = read_json(path)
    if run.get("status") != "ACTIVE":
        raise BrownfieldError(
            f"Run {run_id} is {run.get('status')}, not ACTIVE; recover control state before continuing"
        )
    abort_summary = path.parent / "abort.md"
    abort_event = path.parent / "events" / f"run-aborted-{run_id}.json"
    if not allow_partial_abort and (abort_summary.exists() or abort_event.exists()):
        raise BrownfieldError(partial_abort_error(path))
    return run_id, path, run


def event_path(memory: Path, run_id: str, kind: str, identity: str) -> Path:
    safe_kind = re.sub(r"[^a-z0-9-]+", "-", kind.lower()).strip("-")
    safe_identity = re.sub(r"[^A-Za-z0-9_.-]+", "-", identity)
    return safe_child(memory, f"runs/{run_id}/events/{safe_kind}-{safe_identity}.json")


def decision_for(memory: Path, run_id: str, contribution_id: str) -> dict[str, Any] | None:
    events = safe_child(memory, f"runs/{run_id}/events")
    if not events.exists():
        return None
    for path in events.glob(f"*-{contribution_id}.json"):
        value = read_json(path)
        if value.get("contribution_id") == contribution_id and value.get("kind") in {"CONTRIBUTION_ACCEPTED", "CONTRIBUTION_REJECTED"}:
            return value
    return None


def contribution_files(memory: Path, run_id: str) -> list[Path]:
    directory = safe_child(memory, f"runs/{run_id}/contributions")
    return sorted(directory.glob("*.json")) if directory.exists() else []


def find_contribution(memory: Path, run_id: str, selector: str) -> Path:
    direct = Path(selector).expanduser()
    if direct.is_file():
        resolved = direct.resolve()
        allowed = safe_child(memory, f"runs/{run_id}/contributions").resolve()
        try:
            resolved.relative_to(allowed)
        except ValueError as exc:
            raise BrownfieldError("Contribution must be staged inside the active run") from exc
        return resolved
    matches = []
    for path in contribution_files(memory, run_id):
        value = read_json(path)
        if value.get("contribution_id") == selector or path.name == selector:
            matches.append(path)
    if len(matches) != 1:
        raise BrownfieldError(f"Expected one staged contribution matching {selector!r}, found {len(matches)}")
    return matches[0]


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    project_name = args.name or root.name
    if not project_name.strip() or len(project_name) > 200:
        raise BrownfieldError("Project name must contain 1 to 200 characters")
    if args.authority_branch is not None and (not args.authority_branch.strip() or len(args.authority_branch) > 255):
        raise BrownfieldError("Authority branch must contain 1 to 255 characters")
    reject_sensitive(
        "initialization metadata",
        {"project_name": project_name, "authority_branch": args.authority_branch},
    )
    memory = init_memory(root, project_name, args.authority_branch)
    return {"status": "INITIALIZED", "memory": str(memory)}


def status_payload(root: Path) -> dict[str, Any]:
    memory = memory_path(root)
    if not memory.exists():
        return {"classification": "NEW", "memory": str(memory)}
    validation = validate_memory(root, strict=False)
    try:
        _, manifest, _, state = load_control(root)
        snapshot = snapshot_vector(root, manifest)
        stale = stale_records(root)
    except (BrownfieldError, KeyError, TypeError, ValueError) as exc:
        validation["errors"].append(str(exc))
        return {"classification": "RECOVERY_REQUIRED", "memory": str(memory), "validation": validation}
    transactions = sorted(path.name for path in (memory / "runtime" / "transactions").glob("*.json"))
    known_stale = known_stale_records(memory)
    if validation["errors"] or transactions:
        classification = "RECOVERY_REQUIRED"
    elif state.get("active_run_id"):
        classification = "RESUMABLE"
    elif stale or known_stale:
        classification = "STALE"
    else:
        classification = "READY"
    return {
        "classification": classification,
        "memory": str(memory),
        "memory_revision": state.get("memory_revision"),
        "knowledge_digest": knowledge_digest(memory),
        "active_run_id": state.get("active_run_id"),
        "last_completed_run_id": state.get("last_completed_run_id"),
        "source_snapshot": snapshot,
        "stale_candidates": stale,
        "known_stale_or_uncertain_records": known_stale,
        "transactions": transactions,
        "validation": validation,
    }


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    return status_payload(project_root(args.root))


def cmd_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    _, manifest, _, _ = load_control(root)
    return snapshot_vector(root, manifest)


def cmd_begin(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, manifest, _, state = load_control(root)
    mode = normalize_mode(args.mode)
    if mode in SOURCE_WRITE_MODES and not args.authorize_source_writes:
        raise BrownfieldError(f"{mode} requires --authorize-source-writes based on explicit user authority")
    if mode not in SOURCE_WRITE_MODES and args.authorize_source_writes:
        raise BrownfieldError(f"{mode} forbids source writes; remove --authorize-source-writes or select an authorized source-writing mode")
    if not args.objective.strip() or len(args.objective) > 5_000:
        raise BrownfieldError("Run objective must contain 1 to 5000 characters")
    if not args.scope.strip() or len(args.scope) > 5_000:
        raise BrownfieldError("Run scope must contain 1 to 5000 characters")
    if not AGENT_ID_RE.fullmatch(args.coordinator):
        raise BrownfieldError("Coordinator ID must contain only letters, digits, dot, underscore, or hyphen")
    if args.max_tasks < 1 or args.max_agents < 1:
        raise BrownfieldError("Run max-tasks and max-agents must be positive")
    for path in (args.allow_path or []) + (args.forbid_path or []):
        if not safe_relative_path(path):
            raise BrownfieldError(f"Run envelope path must be a safe project-relative path: {path!r}")
    for check in args.required_check or []:
        if not check.strip() or len(check) > 1_000:
            raise BrownfieldError("Required check labels must contain 1 to 1000 characters")
    for condition in args.stop_when or []:
        if not condition.strip() or len(condition) > 1_000:
            raise BrownfieldError("Stopping conditions must contain 1 to 1000 characters")
    if state.get("active_run_id"):
        raise BrownfieldError(f"Run {state['active_run_id']} is already active; resume it instead of starting over")
    validation = validate_memory(root, strict=False)
    if validation["errors"]:
        raise BrownfieldError("Memory requires recovery before a run can begin:\n- " + "\n- ".join(validation["errors"]))
    run_id = make_id("run")
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        state = read_json(memory / "state.json")
        if state.get("active_run_id"):
            raise BrownfieldError(f"Run {state['active_run_id']} became active concurrently")
        snapshot = snapshot_vector(root, manifest)
        now = utc_now()
        envelope = {
            "source_writes_authorized": bool(args.authorize_source_writes),
            "allowed_paths": args.allow_path or [],
            "forbidden_paths": args.forbid_path or [],
            "risk_ceiling": args.risk_ceiling,
            "max_tasks": args.max_tasks,
            "max_agents": args.max_agents,
            "required_checks": args.required_check or [],
            "stopping_conditions": args.stop_when or [
                "Scoped objective is complete and verified",
                "User input or new authority is required",
                "Risk or scope reaches the run envelope",
                "Further work has diminishing expected value",
            ],
        }
        run = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "status": "ACTIVE",
            "stage": "INITIALIZED",
            "mode": mode,
            "objective": args.objective,
            "scope": args.scope,
            "coordinator": args.coordinator,
            "created_at": now,
            "updated_at": now,
            "base_memory_revision": state["memory_revision"],
            "base_knowledge_digest": knowledge_digest(memory),
            "baseline": {"source_snapshot": snapshot, "known_checks": []},
            "envelope": envelope,
            "checkpoints": [],
            "final_snapshot": None,
        }
        reject_sensitive("run envelope", run)
        run_root = safe_child(memory, f"runs/{run_id}")
        for directory in ["events", "assignments", "contributions", "verification", "context"]:
            (run_root / directory).mkdir(parents=True, exist_ok=True)
        atomic_write_json(run_root / "run.json", run)
        atomic_write_json(run_root / "baseline.json", run["baseline"])
        state["active_run_id"] = run_id
        state["updated_at"] = now
        atomic_write_json(memory / "state.json", state)
        render_views(root)
    return {"status": "ACTIVE", "run_id": run_id, "mode": mode, "source_writes_authorized": envelope["source_writes_authorized"]}


def cmd_record_template(args: argparse.Namespace) -> dict[str, Any]:
    return record_template(
        args.record_type,
        args.title,
        args.statement,
        args.classification,
        args.actor,
        args.run,
    )


def contribution_template(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    memory, manifest, _, state = load_control(root)
    run_id, _, _ = active_run(memory, state, args.run)
    record = record_template(args.record_type, args.title, args.statement, args.classification, args.agent, run_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "contribution_id": make_id("sub"),
        "run_id": run_id,
        "agent_id": args.agent,
        "task_id": args.task,
        "base_memory_revision": state["memory_revision"],
        "base_knowledge_digest": knowledge_digest(memory),
        "base_record_revisions": {},
        "created_at": utc_now(),
        "source_snapshot": snapshot_vector(root, manifest),
        "operations": [{"action": "CREATE", "expected_revision": None, "record": record}],
        "checks": [],
        "uncertainties": [],
        "risk": args.risk,
        "review": {"disposition": "NOT_REVIEWED", "reviewer": None, "evidence": []},
        "sensitivity_review": {"completed": False, "redactions": []},
    }


def cmd_contribution_template(args: argparse.Namespace) -> dict[str, Any]:
    if not AGENT_ID_RE.fullmatch(args.agent):
        raise BrownfieldError("agent ID must contain only letters, digits, dot, underscore, or hyphen")
    return contribution_template(project_root(args.root), args)


def cmd_stage(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, _, policy, state = load_control(root)
    run_id, _, _ = active_run(memory, state, args.run)
    source = Path(args.input).expanduser().resolve()
    if not source.is_file():
        raise BrownfieldError(f"Contribution file does not exist: {source}")
    if source.stat().st_size > int(policy.get("max_record_bytes", 1_000_000)):
        raise BrownfieldError("Contribution exceeds the configured size limit")
    value = read_json(source)
    sensitive = secret_findings(source.name, value)
    if sensitive:
        raise BrownfieldError("Contribution failed sensitivity scan:\n- " + "\n- ".join(sensitive))
    errors, warnings = validate_contribution(value, source)
    if errors:
        raise BrownfieldError("Invalid contribution:\n- " + "\n- ".join(errors))
    if value["run_id"] != run_id:
        raise BrownfieldError(f"Contribution targets {value['run_id']}, not active run {run_id}")
    if not AGENT_ID_RE.fullmatch(value["agent_id"]):
        raise BrownfieldError("Invalid contribution agent_id")
    name = f"{value['agent_id']}-{value['contribution_id']}.json"
    destination = safe_child(memory, f"runs/{run_id}/contributions/{name}")
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        current_state = read_json(memory / "state.json")
        active_run(memory, current_state, run_id)
        if destination.exists():
            if read_json(destination) != value:
                raise BrownfieldError(f"A different contribution already uses {value['contribution_id']}")
            return {"status": "ALREADY_STAGED", "path": str(destination), "warnings": warnings}
        atomic_write_json(destination, value)
    return {"status": "STAGED", "path": str(destination), "warnings": warnings}


def _prepare_operations(memory: Path, contribution: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    records = load_records(memory)
    for operation in contribution["operations"]:
        record = operation["record"]
        record_id = record["id"]
        target = record_path(memory, record["record_type"], record_id)
        relative = target.relative_to(memory).as_posix()
        current_entry = records.get(record_id)
        if operation["action"] == "CREATE":
            if current_entry or target.exists():
                raise BrownfieldError(f"CREATE conflicts with existing record {record_id}")
            if record["record_revision"] != 1:
                raise BrownfieldError(f"New record {record_id} must start at revision 1")
            before[relative] = None
        else:
            if not current_entry:
                raise BrownfieldError(f"UPDATE targets missing record {record_id}")
            current_path, current = current_entry
            expected = operation["expected_revision"]
            if current["record_revision"] != expected:
                raise BrownfieldError(f"Record {record_id} is revision {current['record_revision']}, expected {expected}")
            if record["record_revision"] != expected + 1:
                raise BrownfieldError(f"Updated record {record_id} must advance exactly one revision")
            if current_path.resolve() != target.resolve():
                raise BrownfieldError(f"UPDATE cannot move record {record_id}")
            before[relative] = current
        after[relative] = record
    return before, after


def transaction_errors(memory: Path, value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["transaction must be a JSON object"]
    required = {
        "schema_version", "transaction_id", "status", "created_at", "before_records",
        "after_records", "state_before", "state_after", "event",
    }
    missing = required - value.keys()
    if missing:
        return [f"transaction is missing: {', '.join(sorted(missing))}"]
    errors: list[str] = []

    def valid_timestamp(candidate: Any) -> bool:
        if not isinstance(candidate, str):
            return False
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None

    if value.get("schema_version") != SCHEMA_VERSION or value.get("status") != "PREPARED":
        errors.append("transaction has an unsupported schema version or status")
    if not isinstance(value.get("transaction_id"), str) or not re.fullmatch(r"^[a-z][a-z0-9-]*$", value["transaction_id"]):
        errors.append("transaction has an invalid transaction_id")
    if not valid_timestamp(value.get("created_at")):
        errors.append("transaction has an invalid created_at timestamp")
    before_records = value.get("before_records")
    after_records = value.get("after_records")
    if not isinstance(before_records, dict) or not isinstance(after_records, dict):
        errors.append("transaction record maps must be objects")
        return errors
    if not after_records:
        errors.append("transaction must contain at least one record operation")
    if set(before_records) != set(after_records):
        errors.append("transaction before/after record paths differ")
    transaction_record_ids: list[str] = []
    for relative, record in after_records.items():
        if not isinstance(relative, str):
            errors.append("transaction record path must be a string")
            continue
        try:
            target = safe_child(memory, relative)
        except BrownfieldError as exc:
            errors.append(str(exc))
            continue
        if not relative.startswith("records/") or target.suffix != ".json":
            errors.append(f"transaction target is not a canonical record path: {relative}")
        record_validation, _ = validate_record(record, target, strict=True)
        errors.extend(record_validation)
        if isinstance(record, dict) and isinstance(record.get("id"), str) and isinstance(record.get("record_type"), str):
            transaction_record_ids.append(record["id"])
            try:
                expected = record_path(memory, record["record_type"], record["id"])
            except BrownfieldError as exc:
                errors.append(str(exc))
            else:
                if expected != target:
                    errors.append(f"transaction record path does not match record identity: {relative}")
        before = before_records.get(relative)
        if before is not None:
            prior_validation, _ = validate_record(before, target, strict=True)
            errors.extend(prior_validation)
            if isinstance(before, dict) and isinstance(record, dict):
                if before.get("id") != record.get("id") or before.get("record_type") != record.get("record_type"):
                    errors.append(f"transaction UPDATE changes record identity: {relative}")
                if type(before.get("record_revision")) is int and type(record.get("record_revision")) is int:
                    if record["record_revision"] != before["record_revision"] + 1:
                        errors.append(f"transaction UPDATE must advance one record revision: {relative}")
        elif isinstance(record, dict) and record.get("record_revision") != 1:
            errors.append(f"transaction CREATE must start at record revision 1: {relative}")
    state_before = value.get("state_before")
    state_after = value.get("state_after")
    if not isinstance(state_before, dict) or not isinstance(state_after, dict):
        errors.append("transaction state_before and state_after must be objects")
    else:
        state_fields = {
            "schema_version", "memory_revision", "active_run_id", "last_completed_run_id",
            "last_snapshot", "updated_at",
        }
        if set(state_before) != state_fields or set(state_after) != state_fields:
            errors.append("transaction control states must contain the complete schema-v1 state shape")
        if state_before.get("schema_version") != SCHEMA_VERSION or state_after.get("schema_version") != SCHEMA_VERSION:
            errors.append("transaction control states have an unsupported schema version")
        if not valid_timestamp(state_before.get("updated_at")) or not valid_timestamp(state_after.get("updated_at")):
            errors.append("transaction control states require valid updated_at timestamps")
        before_revision = state_before.get("memory_revision")
        after_revision = state_after.get("memory_revision")
        if type(before_revision) is not int or type(after_revision) is not int or after_revision != before_revision + 1:
            errors.append("transaction must advance memory_revision exactly once")
        for field in state_fields - {"memory_revision", "updated_at"}:
            if state_before.get(field) != state_after.get(field):
                errors.append(f"transaction cannot change control state field {field}")
    event = value.get("event")
    if not isinstance(event, dict):
        errors.append("transaction event must be an object")
    else:
        event_fields = {
            "schema_version", "kind", "run_id", "contribution_id", "agent_id", "reviewed_by",
            "accepted_at", "memory_revision_before", "memory_revision_after", "record_ids", "warnings",
        }
        missing_event = event_fields - event.keys()
        if missing_event:
            errors.append(f"transaction event is missing: {', '.join(sorted(missing_event))}")
        if event.get("schema_version") != SCHEMA_VERSION:
            errors.append("transaction event has an unsupported schema version")
        if event.get("kind") != "CONTRIBUTION_ACCEPTED":
            errors.append("transaction event must be CONTRIBUTION_ACCEPTED")
        for field in ("run_id", "contribution_id"):
            if not isinstance(event.get(field), str) or not re.fullmatch(r"^[a-z][a-z0-9-]*$", event[field]):
                errors.append(f"transaction event has invalid {field}")
        for field in ("agent_id", "reviewed_by"):
            if not isinstance(event.get(field), str) or not AGENT_ID_RE.fullmatch(event[field]):
                errors.append(f"transaction event has invalid {field}")
        if not valid_timestamp(event.get("accepted_at")):
            errors.append("transaction event has an invalid accepted_at timestamp")
        if event.get("contribution_id") != value.get("transaction_id"):
            errors.append("transaction and event identities differ")
        if isinstance(state_before, dict) and isinstance(state_after, dict):
            if event.get("memory_revision_before") != state_before.get("memory_revision"):
                errors.append("transaction event memory_revision_before does not match state_before")
            if event.get("memory_revision_after") != state_after.get("memory_revision"):
                errors.append("transaction event memory_revision_after does not match state_after")
            if event.get("run_id") != state_before.get("active_run_id"):
                errors.append("transaction run does not match the active run in state_before")
        record_ids = event.get("record_ids")
        if not isinstance(record_ids, list) or not record_ids or not all(isinstance(item, str) for item in record_ids):
            errors.append("transaction event record_ids must be a non-empty string list")
        elif len(record_ids) != len(set(record_ids)) or set(record_ids) != set(transaction_record_ids):
            errors.append("transaction event record_ids do not match transaction records")
        if not isinstance(event.get("warnings"), list) or not all(isinstance(item, str) for item in event.get("warnings", [])):
            errors.append("transaction event warnings must be a string list")
        run_id = event.get("run_id")
        if isinstance(run_id, str) and re.fullmatch(r"^[a-z][a-z0-9-]*$", run_id):
            run_path = safe_child(memory, f"runs/{run_id}/run.json")
            if not run_path.is_file():
                errors.append(f"transaction references missing run {run_id}")
            else:
                try:
                    run = read_json(run_path)
                except BrownfieldError as exc:
                    errors.append(str(exc))
                else:
                    if not isinstance(run, dict) or run.get("run_id") != run_id or run.get("status") != "ACTIVE":
                        errors.append(f"transaction references invalid or inactive run {run_id}")
    return errors


def _apply_transaction(root: Path, memory: Path, transaction_path: Path, transaction: dict[str, Any]) -> None:
    errors = transaction_errors(memory, transaction)
    if errors:
        raise BrownfieldError("Invalid memory transaction:\n- " + "\n- ".join(errors))
    reject_sensitive("memory transaction", transaction)
    current_state = read_json(memory / "state.json")
    before_revision = transaction["state_before"]["memory_revision"]
    after_revision = transaction["state_after"]["memory_revision"]
    if current_state != transaction["state_before"] and current_state != transaction["state_after"]:
        raise BrownfieldError(
            f"Transaction {transaction['transaction_id']} targets revisions {before_revision}->{after_revision}, "
            "but the complete current control state differs; refusing stale or corrupt replay"
        )
    for relative, after_value in transaction["after_records"].items():
        target = safe_child(memory, relative)
        before_value = transaction["before_records"].get(relative)
        current_value = read_json(target) if target.exists() else None
        if current_value != before_value and current_value != after_value:
            raise BrownfieldError(f"Transaction target changed independently: {relative}")
    event = transaction["event"]
    event_target = event_path(memory, event["run_id"], "accepted", event["contribution_id"])
    if event_target.exists() and read_json(event_target) != event:
        raise BrownfieldError("Transaction acceptance event conflicts with an existing event")
    for relative, value in transaction["after_records"].items():
        atomic_write_json(safe_child(memory, relative), value)
    atomic_write_json(memory / "state.json", transaction["state_after"])
    atomic_write_json(event_target, event)
    render_views(root)
    transaction_path.unlink(missing_ok=True)


def _merge_value(root: Path, memory: Path, state: dict[str, Any], contribution: dict[str, Any], reviewed_by: str) -> dict[str, Any]:
    run_id = contribution["run_id"]
    existing = decision_for(memory, run_id, contribution["contribution_id"])
    if existing:
        if existing["kind"] == "CONTRIBUTION_ACCEPTED":
            return {"status": "ALREADY_ACCEPTED", "event": existing}
        raise BrownfieldError("Contribution was already rejected")
    incomplete = sorted((memory / "runtime" / "transactions").glob("*.json"))
    if incomplete:
        raise BrownfieldError("Recover the incomplete memory transaction before accepting another contribution")
    integrity = validate_memory(root, strict=True)
    if integrity["errors"]:
        raise BrownfieldError("Canonical memory failed pre-merge validation:\n- " + "\n- ".join(integrity["errors"]))
    errors, warnings = validate_contribution(contribution)
    if errors:
        raise BrownfieldError("Invalid contribution:\n- " + "\n- ".join(errors))
    sensitive = secret_findings("contribution.json", contribution)
    if sensitive:
        raise BrownfieldError("Contribution failed sensitivity scan:\n- " + "\n- ".join(sensitive))
    if contribution["base_memory_revision"] != state["memory_revision"]:
        raise BrownfieldError(
            f"Stale contribution base revision {contribution['base_memory_revision']}; current is {state['memory_revision']}. "
            "Re-evaluate and stage a new immutable contribution."
        )
    if contribution["base_knowledge_digest"] != knowledge_digest(memory):
        raise BrownfieldError("Contribution knowledge digest is stale; re-evaluate it against current canonical memory")
    _, manifest, _, _ = load_control(root)
    current_snapshot = snapshot_vector(root, manifest)
    contribution_source = contribution["source_snapshot"].get(
        "source_vector_digest", contribution["source_snapshot"].get("vector_digest")
    )
    current_source = current_snapshot.get("source_vector_digest", current_snapshot["vector_digest"])
    if contribution_source != current_source:
        raise BrownfieldError("Repository source changed since this contribution was prepared")
    run = read_json(safe_child(memory, f"runs/{run_id}/run.json"))
    ceiling = run.get("envelope", {}).get("risk_ceiling", "LOW")
    if (
        contribution["risk"] not in RISK_RANK
        or ceiling not in RISK_RANK
        or RISK_RANK[contribution["risk"]] > RISK_RANK[ceiling]
    ):
        raise BrownfieldError(f"Contribution risk {contribution['risk']} exceeds run ceiling {ceiling}")
    source_change = contribution.get("source_change_ref")
    if source_change:
        envelope = run.get("envelope", {})
        if not envelope.get("source_writes_authorized"):
            raise BrownfieldError("Contribution reports source changes but the run forbids source writes")
        changed_paths = source_change.get("changed_paths", [])
        allowed = envelope.get("allowed_paths", [])
        forbidden = envelope.get("forbidden_paths", [])

        if not allowed or any(not path_within_any(path, allowed) for path in changed_paths):
            raise BrownfieldError("Source contribution contains paths outside the explicit write allowlist")
        if any(path_within_any(path, forbidden) for path in changed_paths):
            raise BrownfieldError("Source contribution touches a forbidden path")
    if contribution["risk"] == "HIGH":
        review = contribution.get("review", {})
        if review.get("disposition") != "CONFIRMED" or not review.get("reviewer"):
            raise BrownfieldError("HIGH-risk contribution requires a recorded independent CONFIRMED review")
        if review["reviewer"] == contribution["agent_id"]:
            raise BrownfieldError("HIGH-risk contributor cannot be its own reviewer")
    if not contribution.get("sensitivity_review", {}).get("completed"):
        raise BrownfieldError("Complete the contribution sensitivity review before acceptance")
    before, after = _prepare_operations(memory, contribution)
    now = utc_now()
    state_after = dict(state)
    state_after["memory_revision"] = state["memory_revision"] + 1
    state_after["updated_at"] = now
    event = {
        "schema_version": SCHEMA_VERSION,
        "kind": "CONTRIBUTION_ACCEPTED",
        "run_id": run_id,
        "contribution_id": contribution["contribution_id"],
        "agent_id": contribution["agent_id"],
        "reviewed_by": reviewed_by,
        "accepted_at": now,
        "memory_revision_before": state["memory_revision"],
        "memory_revision_after": state_after["memory_revision"],
        "record_ids": [item["record"]["id"] for item in contribution["operations"]],
        "warnings": warnings,
    }
    reject_sensitive("contribution acceptance", event)
    transaction = {
        "schema_version": SCHEMA_VERSION,
        "transaction_id": contribution["contribution_id"],
        "status": "PREPARED",
        "created_at": now,
        "before_records": before,
        "after_records": after,
        "state_before": state,
        "state_after": state_after,
        "event": event,
    }
    transaction_path = memory / "runtime" / "transactions" / f"{contribution['contribution_id']}.json"
    atomic_write_json(transaction_path, transaction)
    _apply_transaction(root, memory, transaction_path, transaction)
    return {"status": "ACCEPTED", "event": event}


def cmd_merge(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    if not AGENT_ID_RE.fullmatch(args.reviewed_by):
        raise BrownfieldError("reviewed-by must be a valid coordinator ID")
    memory, _, _, state = load_control(root)
    run_id, _, _ = active_run(memory, state, args.run)
    path = find_contribution(memory, run_id, args.contribution)
    contribution = read_json(path)
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        state = read_json(memory / "state.json")
        active_run(memory, state, run_id)
        return _merge_value(root, memory, state, contribution, args.reviewed_by)


def cmd_reject(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    if not AGENT_ID_RE.fullmatch(args.rejected_by):
        raise BrownfieldError("rejected-by must be a valid coordinator ID")
    memory, _, _, state = load_control(root)
    run_id, _, _ = active_run(memory, state, args.run)
    path = find_contribution(memory, run_id, args.contribution)
    contribution = read_json(path)
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        existing = decision_for(memory, run_id, contribution["contribution_id"])
        if existing:
            return {"status": existing["kind"], "event": existing}
        event = {
            "schema_version": SCHEMA_VERSION,
            "kind": "CONTRIBUTION_REJECTED",
            "run_id": run_id,
            "contribution_id": contribution["contribution_id"],
            "agent_id": contribution["agent_id"],
            "rejected_by": args.rejected_by,
            "rejected_at": utc_now(),
            "reason": args.reason,
        }
        reject_sensitive("contribution rejection", event)
        atomic_write_json(event_path(memory, run_id, "rejected", contribution["contribution_id"]), event)
    return {"status": "REJECTED", "event": event}


def cmd_refresh(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, manifest, _, state = load_control(root)
    candidates = stale_records(root)
    if not args.apply or not candidates:
        return {"status": "DRY_RUN" if not args.apply else "NO_CHANGES", "stale_candidates": candidates}
    run_id, _, _ = active_run(memory, state, args.run)
    records = load_records(memory)
    now = utc_now()
    operations = []
    for record_id, reasons in sorted(candidates.items()):
        current = records[record_id][1]
        updated = json.loads(json.dumps(current))
        updated["record_revision"] += 1
        updated["knowledge_status"] = "STALE"
        updated["updated_at"] = now
        updated["history"].append({"at": now, "event": "MARKED_STALE", "run_id": run_id, "reason": "; ".join(reasons)})
        operations.append({"action": "UPDATE", "expected_revision": current["record_revision"], "record": updated})
    contribution = {
        "schema_version": SCHEMA_VERSION,
        "contribution_id": make_id("sub-refresh"),
        "run_id": run_id,
        "agent_id": "freshness-engine",
        "task_id": "automatic-freshness-reconciliation",
        "base_memory_revision": state["memory_revision"],
        "base_knowledge_digest": knowledge_digest(memory),
        "base_record_revisions": {record_id: records[record_id][1]["record_revision"] for record_id in candidates},
        "created_at": now,
        "source_snapshot": snapshot_vector(root, manifest),
        "operations": operations,
        "checks": [{"kind": "DETERMINISTIC_FINGERPRINT", "result": "STALE", "records": sorted(candidates)}],
        "uncertainties": ["Dependency selectors are conservative and may not capture every semantic impact"],
        "risk": "LOW",
        "review": {"disposition": "DETERMINISTIC", "reviewer": "freshness-engine", "evidence": []},
        "sensitivity_review": {"completed": True, "redactions": []},
    }
    destination = safe_child(memory, f"runs/{run_id}/contributions/freshness-engine-{contribution['contribution_id']}.json")
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        state = read_json(memory / "state.json")
        active_run(memory, state, run_id)
        atomic_write_json(destination, contribution)
        result = _merge_value(root, memory, state, contribution, "deterministic-freshness")
    result["stale_candidates"] = candidates
    return result


def cmd_context(args: argparse.Namespace) -> dict[str, Any] | str:
    root = project_root(args.root)
    memory, _, policy, _ = load_control(root)
    max_chars = args.max_chars or int(policy.get("default_context_max_chars", 24_000))
    content, omitted = build_context(root, args.record or [], args.query, args.mission, max_chars)
    if args.output:
        reject_sensitive("context package", content)
        output = safe_child(memory / "runtime" / "context", args.output)
        atomic_write_text(output, content)
        return {"status": "CREATED", "output": str(output), "omitted_records": omitted, "characters": len(content)}
    return content


def cmd_render(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, _, _, state = load_control(root)
    run_id = state.get("active_run_id") or "render"
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        paths = render_views(root)
    return {"status": "RENDERED", "paths": {key: str(value) for key, value in paths.items()}}


def allowed_next_stage(run: dict[str, Any]) -> str:
    current = run["stage"]
    source_writes = run["envelope"]["source_writes_authorized"]
    if current == "INITIALIZED":
        return "INVESTIGATING"
    if current == "INVESTIGATING":
        return "CHANGING" if source_writes else "VALIDATING"
    if current == "CHANGING":
        return "VALIDATING"
    if current == "VALIDATING":
        return "REVIEWING"
    if current == "REVIEWING":
        return "MERGING"
    if current == "MERGING":
        return "COMPLETE"
    raise BrownfieldError(f"Run is already at terminal stage {current}")


def cmd_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, manifest, _, state = load_control(root)
    run_id, run_path, run = active_run(memory, state, args.run)
    target = args.stage.upper()
    if target == "COMPLETE":
        raise BrownfieldError("Use finish to complete a run")
    expected = "MERGING" if run["stage"] == "MERGING" and target == "MERGING" else allowed_next_stage(run)
    if target != expected:
        raise BrownfieldError(f"Next stage from {run['stage']} is {expected}, not {target}")
    if len(args.summary) > 4_000:
        raise BrownfieldError("Checkpoint summary exceeds 4000 characters; persist a concise conclusion")
    sensitive = secret_findings("checkpoint-summary.md", args.summary)
    if sensitive:
        raise BrownfieldError("Checkpoint summary failed sensitivity scan:\n- " + "\n- ".join(sensitive))
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        run = read_json(run_path)
        current_expected = "MERGING" if run["stage"] == "MERGING" and target == "MERGING" else allowed_next_stage(run)
        if target != current_expected:
            raise BrownfieldError("Run stage changed concurrently")
        now = utc_now()
        checkpoint = {
            "at": now,
            "stage": target,
            "summary": args.summary,
            "checks": args.check or [],
            "source_snapshot": snapshot_vector(root, manifest),
            "memory_revision": read_json(memory / "state.json")["memory_revision"],
        }
        reject_sensitive("run checkpoint", checkpoint)
        run["stage"] = target
        run["updated_at"] = now
        run["checkpoints"].append(checkpoint)
        atomic_write_json(run_path, run)
    return {"status": "CHECKPOINTED", "run_id": run_id, "stage": target}


def pending_contributions(memory: Path, run_id: str) -> list[str]:
    pending = []
    for path in contribution_files(memory, run_id):
        contribution = read_json(path)
        if not decision_for(memory, run_id, contribution["contribution_id"]):
            pending.append(contribution["contribution_id"])
    return pending


def source_envelope_violations(
    root: Path,
    manifest: dict[str, Any],
    run: dict[str, Any],
    current: dict[str, Any],
) -> list[str]:
    """Map current source drift against the immutable run authorization envelope."""
    envelope = run.get("envelope", {})
    if not envelope.get("source_writes_authorized"):
        return []
    baseline = run.get("baseline", {}).get("source_snapshot")
    if not isinstance(baseline, dict):
        raise BrownfieldError("Run baseline has no valid source snapshot")
    changed = changed_source_paths(root, manifest, baseline, current)
    repositories = {item["id"]: item for item in manifest["repositories"]}
    allowed = envelope.get("allowed_paths", [])
    forbidden = envelope.get("forbidden_paths", [])
    violations: list[str] = []
    for repository_id, paths in sorted(changed.items()):
        repository = repositories.get(repository_id)
        if not repository:
            violations.append(f"unknown repository {repository_id}")
            continue
        repository_root = repository["path"].strip("/")
        for relative in paths:
            if relative == "<unmapped-source-change>":
                violations.append(f"{repository_id}: source change could not be mapped to a path")
                continue
            project_relative = relative if repository_root in {"", "."} else f"{repository_root}/{relative}"
            if not allowed or not path_within_any(project_relative, allowed):
                violations.append(f"{repository_id}:{relative} is outside the source-write allowlist")
            if path_within_any(project_relative, forbidden):
                violations.append(f"{repository_id}:{relative} touches a forbidden path")
    return violations


def load_terminal_summary(raw_path: str, *, label: str) -> str:
    summary_path = Path(raw_path).expanduser().resolve()
    if not summary_path.is_file():
        raise BrownfieldError(f"{label} file does not exist: {summary_path}")
    summary = summary_path.read_text(encoding="utf-8")
    if not summary.strip():
        raise BrownfieldError(f"{label} must not be empty")
    if len(summary) > 40_000:
        raise BrownfieldError(f"{label} exceeds 40000 characters; keep durable conclusions concise")
    sensitive = secret_findings(f"{label.lower().replace(' ', '-')}.md", summary)
    if sensitive:
        raise BrownfieldError(f"{label} failed sensitivity scan:\n- " + "\n- ".join(sensitive))
    return summary


def verified_finish_snapshot(
    root: Path,
    manifest: dict[str, Any],
    run: dict[str, Any],
) -> dict[str, Any]:
    """Require completion evidence and source authority to match the current content."""
    current = snapshot_vector(root, manifest)
    current_digest = current["source_vector_digest"]
    checkpoints = run.get("checkpoints")
    if not isinstance(checkpoints, list) or not checkpoints:
        raise BrownfieldError("Run has no checkpoint linked to the current source snapshot")
    latest = checkpoints[-1]
    if not isinstance(latest, dict) or latest.get("stage") != "MERGING":
        raise BrownfieldError("The final checkpoint must be the MERGING checkpoint")
    latest_snapshot = latest.get("source_snapshot")
    if not isinstance(latest_snapshot, dict) or latest_snapshot.get("source_vector_digest") != current_digest:
        raise BrownfieldError(
            "Repository source changed after the final checkpoint; repeat validation and checkpoint the current snapshot"
        )

    current_checks = {
        check
        for checkpoint in checkpoints
        if isinstance(checkpoint, dict)
        and isinstance(checkpoint.get("source_snapshot"), dict)
        and checkpoint["source_snapshot"].get("source_vector_digest") == current_digest
        for check in checkpoint.get("checks", [])
        if isinstance(check, str)
    }
    required_checks = run.get("envelope", {}).get("required_checks", [])
    missing_checks = [check for check in required_checks if check not in current_checks]
    if missing_checks:
        raise BrownfieldError(
            "Required checks were not recorded against the current source snapshot: "
            + ", ".join(missing_checks)
        )

    violations = source_envelope_violations(root, manifest, run, current)
    if violations:
        raise BrownfieldError("Run source changes violate its authorization envelope:\n- " + "\n- ".join(violations))
    return current


def cmd_finish(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, manifest, _, state = load_control(root)
    run_id, run_path, run = active_run(memory, state, args.run)
    if allowed_next_stage(run) != "COMPLETE":
        raise BrownfieldError(f"Run must reach MERGING before finish; current stage is {run['stage']}")
    pending = pending_contributions(memory, run_id)
    if pending:
        raise BrownfieldError(f"Accept or reject pending contributions before finish: {', '.join(pending)}")
    validation = validate_memory(root, strict=True)
    if validation["errors"]:
        raise BrownfieldError("Memory validation failed:\n- " + "\n- ".join(validation["errors"]))
    summary = load_terminal_summary(args.summary_file, label="Run summary")
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        state = read_json(memory / "state.json")
        active_run(memory, state, run_id)
        run = read_json(run_path)
        if allowed_next_stage(run) != "COMPLETE":
            raise BrownfieldError("Run stage changed concurrently")
        pending = pending_contributions(memory, run_id)
        if pending:
            raise BrownfieldError(f"Accept or reject pending contributions before finish: {', '.join(pending)}")
        validation = validate_memory(root, strict=True)
        if validation["errors"]:
            raise BrownfieldError("Memory validation failed:\n- " + "\n- ".join(validation["errors"]))
        now = utc_now()
        final_snapshot = verified_finish_snapshot(root, manifest, run)
        run["stage"] = "COMPLETE"
        run["status"] = "COMPLETE"
        run["updated_at"] = now
        run["completed_at"] = now
        run["final_snapshot"] = final_snapshot
        run["final_memory_revision"] = state["memory_revision"]
        atomic_write_text(safe_child(memory, f"runs/{run_id}/summary.md"), summary)
        atomic_write_json(run_path, run)
        state["active_run_id"] = None
        state["last_completed_run_id"] = run_id
        state["last_snapshot"] = final_snapshot
        state["updated_at"] = now
        atomic_write_json(memory / "state.json", state)
        render_views(root)
    return {"status": "COMPLETE", "run_id": run_id, "memory_revision": state["memory_revision"], "warnings": validation["warnings"]}


def cmd_abort(args: argparse.Namespace) -> dict[str, Any]:
    """Close an unaccepted run without certifying its source or discarding evidence."""
    root = project_root(args.root)
    memory, manifest, _, state = load_control(root)
    run_id, run_path, run = active_run(memory, state, args.run, allow_partial_abort=True)
    required_checks = run.get("envelope", {}).get("required_checks", [])
    if args.failed_required_check not in required_checks:
        raise BrownfieldError("Failed check must exactly match one required-check label in the active run")
    transactions = sorted((memory / "runtime" / "transactions").glob("*.json"))
    if transactions:
        raise BrownfieldError("Incomplete memory transaction exists; recover it before aborting the run")
    summary = load_terminal_summary(args.summary_file, label="Abort summary")
    validation = validate_memory(root, strict=True)
    validation_errors = [error for error in validation["errors"] if error != partial_abort_error(run_path)]
    if validation_errors:
        raise BrownfieldError("Memory validation failed before abort:\n- " + "\n- ".join(validation_errors))

    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        state = read_json(memory / "state.json")
        _, _, run = active_run(memory, state, run_id, allow_partial_abort=True)
        required_checks = run.get("envelope", {}).get("required_checks", [])
        if args.failed_required_check not in required_checks:
            raise BrownfieldError("Run required checks changed concurrently")
        transactions = sorted((memory / "runtime" / "transactions").glob("*.json"))
        if transactions:
            raise BrownfieldError("Incomplete memory transaction exists; recover it before aborting the run")
        validation = validate_memory(root, strict=True)
        validation_errors = [error for error in validation["errors"] if error != partial_abort_error(run_path)]
        if validation_errors:
            raise BrownfieldError("Memory validation failed before abort:\n- " + "\n- ".join(validation_errors))

        summary_relative = f"runs/{run_id}/abort.md"
        summary_target = safe_child(memory, summary_relative)
        abort_event_path = safe_child(memory, f"runs/{run_id}/events/run-aborted-{run_id}.json")
        if summary_target.exists() and summary_target.read_text(encoding="utf-8") != summary:
            raise BrownfieldError("A partial abort already recorded a different summary; recover it without replacement")
        if abort_event_path.exists():
            if not summary_target.is_file():
                raise BrownfieldError("Partial abort event exists without its summary; manual evidence recovery is required")
            event = read_json(abort_event_path)
            summary_record = event.get("abort_summary") if isinstance(event, dict) else None
            snapshot_record = event.get("source_snapshot") if isinstance(event, dict) else None
            valid_snapshot = isinstance(snapshot_record, dict) and all(
                isinstance(snapshot_record.get(field), str)
                and re.fullmatch(r"[a-f0-9]{64}", snapshot_record[field])
                for field in ("vector_digest", "source_vector_digest")
            )
            valid_violations = isinstance(event.get("source_envelope_violations"), list) and all(
                isinstance(item, str) and item for item in event["source_envelope_violations"]
            )
            if not (
                event.get("kind") == "RUN_ABORTED"
                and event.get("run_id") == run_id
                and isinstance(event.get("at"), str)
                and event.get("failed_required_check") == args.failed_required_check
                and summary_record
                == {"path": summary_relative, "sha256": hash_file(summary_target)}
                and valid_snapshot
                and valid_violations
                and event.get("memory_revision") == state["memory_revision"]
                and event.get("successor_required") is True
            ):
                raise BrownfieldError("Partial abort evidence is malformed or conflicts with this request; refusing replacement")
            reject_sensitive("run abort event", event)
        else:
            now = utc_now()
            source_snapshot = snapshot_vector(root, manifest)
            violations = source_envelope_violations(root, manifest, run, source_snapshot)
            event = {
                "kind": "RUN_ABORTED",
                "run_id": run_id,
                "at": now,
                "failed_required_check": args.failed_required_check,
                "abort_summary": {"path": summary_relative, "sha256": ""},
                "source_snapshot": source_snapshot,
                "source_envelope_violations": violations,
                "memory_revision": state["memory_revision"],
                "successor_required": True,
            }
            reject_sensitive("run abort event", event)
            if not summary_target.exists():
                atomic_write_text(summary_target, summary)
            event["abort_summary"]["sha256"] = hash_file(summary_target)
            reject_sensitive("run abort event", event)
            atomic_write_json(abort_event_path, event)

        now = event["at"]
        violations = event["source_envelope_violations"]
        run["status"] = "ABORTED"
        run["updated_at"] = now
        run["completed_at"] = now
        run["final_snapshot"] = None
        run["final_memory_revision"] = state["memory_revision"]
        atomic_write_json(run_path, run)
        state["active_run_id"] = None
        state["updated_at"] = now
        atomic_write_json(memory / "state.json", state)
        render_views(root)
    return {
        "status": "ABORTED",
        "run_id": run_id,
        "failed_required_check": args.failed_required_check,
        "source_envelope_violations": violations,
        "successor_required": True,
    }


def cmd_recover(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.root)
    memory, _, _, state = load_control(root)
    transactions = sorted((memory / "runtime" / "transactions").glob("*.json"))
    if not transactions:
        active = state.get("active_run_id")
        if active:
            run_path = safe_child(memory, f"runs/{active}/run.json")
            run = read_json(run_path)
            abort_summary_path = run_path.parent / "abort.md"
            abort_event_path = run_path.parent / "events" / f"run-aborted-{active}.json"
            if run.get("status") == "ACTIVE" and (abort_summary_path.exists() or abort_event_path.exists()):
                if not abort_summary_path.is_file() or not abort_event_path.is_file():
                    raise BrownfieldError(
                        "Partial abort artifacts are incomplete; rerun abort with the original exact check and summary"
                    )
                event = read_json(abort_event_path)
                if not isinstance(event, dict) or not isinstance(event.get("failed_required_check"), str):
                    raise BrownfieldError("Partial abort event is malformed; refusing automatic recovery")
                recovered = cmd_abort(argparse.Namespace(
                    root=str(root),
                    run=active,
                    failed_required_check=event["failed_required_check"],
                    summary_file=str(abort_summary_path),
                    reclaim_lock=args.reclaim_lock,
                ))
                recovered["status"] = "RECONCILED_PARTIAL_ABORT"
                return recovered
            if run.get("status") == "COMPLETE":
                with coordinator_lock(memory, active, reclaim=args.reclaim_lock):
                    state["active_run_id"] = None
                    state["last_completed_run_id"] = active
                    state["updated_at"] = utc_now()
                    atomic_write_json(memory / "state.json", state)
                    render_views(root)
                return {"status": "RECONCILED_COMPLETED_RUN", "run_id": active}
            if run.get("status") == "ABORTED":
                expected_state_error = f"state references run {active}, but that run is not ACTIVE"
                validation = validate_memory(root, strict=True)
                unexpected = [error for error in validation["errors"] if error != expected_state_error]
                if unexpected:
                    raise BrownfieldError(
                        "Cannot reconcile malformed aborted run:\n- " + "\n- ".join(unexpected)
                    )
                with coordinator_lock(memory, active, reclaim=args.reclaim_lock):
                    state = read_json(memory / "state.json")
                    if state.get("active_run_id") != active:
                        raise BrownfieldError("Active run pointer changed concurrently")
                    run = read_json(run_path)
                    if run.get("status") != "ABORTED":
                        raise BrownfieldError("Aborted run status changed concurrently")
                    state["active_run_id"] = None
                    state["updated_at"] = utc_now()
                    atomic_write_json(memory / "state.json", state)
                    render_views(root)
                return {"status": "RECONCILED_ABORTED_RUN", "run_id": active}
        return {"status": "NOTHING_TO_RECOVER"}
    if len(transactions) > 1 and not args.transaction:
        raise BrownfieldError("Multiple transactions need recovery; select one with --transaction")
    if args.transaction:
        matches = [path for path in transactions if path.stem == args.transaction or path.name == args.transaction]
        if len(matches) != 1:
            raise BrownfieldError(f"Expected one transaction matching {args.transaction!r}")
        transaction_path = matches[0]
    else:
        transaction_path = transactions[0]
    transaction = read_json(transaction_path)
    errors = transaction_errors(memory, transaction)
    if errors:
        raise BrownfieldError("Invalid memory transaction:\n- " + "\n- ".join(errors))
    run_id = transaction["event"]["run_id"]
    with coordinator_lock(memory, run_id, reclaim=args.reclaim_lock):
        _apply_transaction(root, memory, transaction_path, transaction)
    return {"status": "TRANSACTION_COMPLETED", "transaction": transaction["transaction_id"]}


def cmd_validate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    result = validate_memory(project_root(args.root), strict=args.strict)
    return result, 1 if result["errors"] else 0


def add_common_root(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="Project root containing .brownfield")


def add_reclaim(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--reclaim-lock", action="store_true", help="Reclaim an expired lock only after verifying its owner is gone")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize portable project memory without touching source files")
    add_common_root(init)
    init.add_argument("--name")
    init.add_argument("--authority-branch")
    init.set_defaults(handler=cmd_init)

    status = commands.add_parser("status", help="Classify memory as new, ready, stale, resumable, or recovery-required")
    add_common_root(status)
    status.set_defaults(handler=cmd_status)

    snapshot = commands.add_parser("snapshot", help="Print the current multi-repository source snapshot")
    add_common_root(snapshot)
    snapshot.set_defaults(handler=cmd_snapshot)

    begin = commands.add_parser("begin", help="Create an immutable run envelope and baseline")
    add_common_root(begin)
    begin.add_argument("--mode", default="DISCOVERY")
    begin.add_argument("--objective", required=True)
    begin.add_argument("--scope", required=True)
    begin.add_argument("--coordinator", default="coordinator")
    begin.add_argument("--authorize-source-writes", action="store_true")
    begin.add_argument("--allow-path", action="append")
    begin.add_argument("--forbid-path", action="append")
    begin.add_argument("--risk-ceiling", choices=["LOW", "MODERATE", "HIGH"], default="LOW")
    begin.add_argument("--max-tasks", type=int, default=10)
    begin.add_argument("--max-agents", type=int, default=4)
    begin.add_argument("--required-check", action="append")
    begin.add_argument("--stop-when", action="append")
    add_reclaim(begin)
    begin.set_defaults(handler=cmd_begin)

    record = commands.add_parser("record-template", help="Create a typed record skeleton")
    record.add_argument("--record-type", choices=sorted(RECORD_TYPES), required=True)
    record.add_argument("--title", required=True)
    record.add_argument("--statement", required=True)
    record.add_argument("--classification", required=True)
    record.add_argument("--actor", required=True)
    record.add_argument("--run", required=True)
    record.set_defaults(handler=cmd_record_template)

    contribution = commands.add_parser("contribution-template", help="Create a one-record contribution skeleton for the active run")
    add_common_root(contribution)
    contribution.add_argument("--run")
    contribution.add_argument("--agent", required=True)
    contribution.add_argument("--task", required=True)
    contribution.add_argument("--record-type", choices=sorted(RECORD_TYPES), required=True)
    contribution.add_argument("--title", required=True)
    contribution.add_argument("--statement", required=True)
    contribution.add_argument("--classification", required=True)
    contribution.add_argument("--risk", choices=["LOW", "MODERATE", "HIGH"], default="LOW")
    contribution.set_defaults(handler=cmd_contribution_template)

    stage = commands.add_parser("stage", help="Atomically stage an immutable agent contribution")
    add_common_root(stage)
    stage.add_argument("--run")
    stage.add_argument("--input", required=True)
    add_reclaim(stage)
    stage.set_defaults(handler=cmd_stage)

    merge = commands.add_parser("merge", help="Promote a reviewed contribution with optimistic concurrency checks")
    add_common_root(merge)
    merge.add_argument("--run")
    merge.add_argument("--contribution", required=True)
    merge.add_argument("--reviewed-by", required=True)
    add_reclaim(merge)
    merge.set_defaults(handler=cmd_merge)

    reject = commands.add_parser("reject", help="Record a durable rejection without deleting the proposal")
    add_common_root(reject)
    reject.add_argument("--run")
    reject.add_argument("--contribution", required=True)
    reject.add_argument("--rejected-by", required=True)
    reject.add_argument("--reason", required=True)
    add_reclaim(reject)
    reject.set_defaults(handler=cmd_reject)

    refresh = commands.add_parser("refresh", help="Detect or apply evidence-based staleness")
    add_common_root(refresh)
    refresh.add_argument("--run")
    refresh.add_argument("--apply", action="store_true")
    add_reclaim(refresh)
    refresh.set_defaults(handler=cmd_refresh)

    context = commands.add_parser("context", help="Build a bounded, explicit context package")
    add_common_root(context)
    context.add_argument("--mission", required=True)
    context.add_argument("--record", action="append")
    context.add_argument("--query")
    context.add_argument("--max-chars", type=int)
    context.add_argument("--output")
    context.set_defaults(handler=cmd_context)

    render = commands.add_parser("render", help="Rebuild deterministic index, freshness, and handoff views")
    add_common_root(render)
    add_reclaim(render)
    render.set_defaults(handler=cmd_render)

    checkpoint = commands.add_parser("checkpoint", help="Advance one durable run stage")
    add_common_root(checkpoint)
    checkpoint.add_argument("--run")
    checkpoint.add_argument("--stage", choices=RUN_STAGES[:-1], required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--check", action="append")
    add_reclaim(checkpoint)
    checkpoint.set_defaults(handler=cmd_checkpoint)

    finish = commands.add_parser("finish", help="Validate, render, summarize, and close a run")
    add_common_root(finish)
    finish.add_argument("--run")
    finish.add_argument("--summary-file", required=True)
    add_reclaim(finish)
    finish.set_defaults(handler=cmd_finish)

    abort = commands.add_parser("abort", help="Close a failed active run without certifying its source")
    add_common_root(abort)
    abort.add_argument("--run")
    abort.add_argument("--failed-required-check", required=True)
    abort.add_argument("--summary-file", required=True)
    add_reclaim(abort)
    abort.set_defaults(handler=cmd_abort)

    recover = commands.add_parser("recover", help="Complete an interrupted memory transaction or reconcile a terminal run")
    add_common_root(recover)
    recover.add_argument("--transaction")
    add_reclaim(recover)
    recover.set_defaults(handler=cmd_recover)

    validate = commands.add_parser("validate", help="Validate layout, records, links, safety, and freshness stamps")
    add_common_root(validate)
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(handler=cmd_validate)
    return parser


def emit(value: Any, as_json: bool) -> None:
    if isinstance(value, str) and not as_json:
        print(value, end="" if value.endswith("\n") else "\n")
        return
    if as_json or isinstance(value, (dict, list)):
        print(canonical_json(value), end="")
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
        exit_code = 0
        if isinstance(result, tuple):
            result, exit_code = result
        emit(result, args.json)
        return exit_code
    except BrownfieldError as exc:
        if args.json:
            emit({"error": str(exc)}, True)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
