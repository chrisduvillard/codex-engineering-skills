# Persistent State Model

## Contents

- [Use three truth layers](#use-three-truth-layers)
- [Use this project layout](#use-this-project-layout)
- [Separate canonical and derived state](#separate-canonical-and-derived-state)
- [Use one record contract](#use-one-record-contract)
- [Record evidence and provenance](#record-evidence-and-provenance)
- [Track freshness by dependency](#track-freshness-by-dependency)
- [Handle Git and memory-only commits](#handle-git-and-memory-only-commits)
- [Scope multi-repository and branch knowledge](#scope-multi-repository-and-branch-knowledge)
- [Represent migrations explicitly](#represent-migrations-explicitly)
- [Validate and compact safely](#validate-and-compact-safely)

## Use three truth layers

Keep these layers distinct:

1. Treat source, tests, configuration, runtime observations, and external systems as evidence of
   **implemented behavior**. Never let a memory record override them.
2. Treat the current Project Constitution and unsuperseded user requirements as authority for
   **intended behavior**. Do not treat user beliefs about existing behavior as implementation facts.
3. Treat `.brownfield/` as the evidence-backed **current belief model** that relates implementation
   to intent. Preserve uncertainty and contradictions instead of forcing agreement.

Register existing project authorities such as glossaries, ADRs, architecture documents, and
repository instructions in `manifest.json`. Link to them; do not copy them into competing sources
of truth.

## Use this project layout

Create the memory root in the coordinating repository, or in a dedicated memory repository for a
multi-repository system:

```text
.brownfield/
├── manifest.json
├── policy.json
├── state.json
├── constitution.md
├── model/
│   ├── overview.md
│   ├── architecture.md
│   ├── capabilities.md
│   ├── components/
│   ├── flows/
│   ├── data/
│   ├── testing/
│   └── infrastructure/
├── records/
│   ├── requirements/<id>.json
│   ├── claims/<id>.json
│   ├── decisions/<id>.json
│   ├── questions/<id>.json
│   ├── findings/<id>.json
│   ├── contradictions/<id>.json
│   ├── investigations/<id>.json
│   ├── migrations/<id>.json
│   ├── tasks/<id>.json
│   └── user-events/<id>.json
├── runs/<run-id>/
│   ├── run.json
│   ├── baseline.json
│   ├── summary.md
│   ├── abort.md
│   ├── events/<event-id>.json
│   ├── assignments/<assignment-id>.json
│   ├── contributions/<agent-id>-<submission-id>.json
│   └── verification/<verification-id>.json
├── schemas/
├── generated/
│   ├── index.json
│   ├── freshness.json
│   └── HANDOFF.md
└── runtime/
    ├── locks/
    ├── transactions/
    ├── context/
    └── artifacts/
```

Version-control all small canonical state. Ignore `runtime/`, secrets, caches, and large raw output.
Commit generated views only when rapid onboarding from a fresh clone is valuable; always stamp them
as derived. Store durable summaries and content hashes for excluded artifacts.

Create `abort.md` only for an `ABORTED` run. Keep it separate from the successful-run summary and
pair it with the immutable `events/run-aborted-<run-id>.json` record written by the lifecycle CLI.
The abort artifacts preserve the exact failed required-check label, sanitized summary locator and
digest, captured source snapshot, envelope violations, terminal memory revision, and the requirement
for a fresh successor run. Validate these files as a pair; do not treat either as certification or as
an accepted final snapshot.

## Separate canonical and derived state

Treat these files as canonical:

- `manifest.json`, `policy.json`, `state.json`, and `constitution.md`.
- Curated current model documents and record-per-entity JSON files.
- Embedded evidence metadata, decisions, meaningful investigations, and sanitized exact user events.
- Active and terminal run state, immutable contributions, per-event merge decisions, abort artifacts,
  and verification summaries required for recovery.

Treat indexes, freshness reports, handoffs, dashboards, search databases, embeddings, and context
packages as derived. Make every derived artifact declare its memory digest and repository snapshot.
Refuse to present a mismatched artifact as current. Rebuild it from canonical state.

Keep current truth in current records. Preserve superseded truth, failed investigations, and raw
user history separately. Do not require a new agent to replay the whole event history to discover
the current model.

## Use one record contract

Store one JSON file per entity to keep diffs narrow and concurrent proposals independent. Give each
record a stable, collision-resistant ID and include:

```json
{
  "schema_version": 1,
  "id": "clm-20260811120000-abcdef1234",
  "record_type": "claim",
  "record_revision": 1,
  "classification": "INFERENCE",
  "title": "Short discoverable title",
  "statement": "One bounded assertion",
  "knowledge_status": "CURRENT",
  "workflow_status": "CONFIRMED",
  "confidence": "MEDIUM",
  "scope": {
    "repositories": ["primary"],
    "components": [],
    "environment": null,
    "phase": null
  },
  "sensitivity": "INTERNAL",
  "evidence": [],
  "depends_on": {"records": [], "sources": []},
  "freshness_policy": {"kind": "ON_CHANGE", "ttl_days": null},
  "verification": {"snapshot": null, "method": null, "verified_at": null, "verified_by": null},
  "supersedes": [],
  "related_records": [],
  "details": {},
  "created_at": "2026-08-11T12:00:00Z",
  "updated_at": "2026-08-11T12:00:00Z",
  "created_by": "discovery-agent",
  "origin_run": "run-20260811115900-abcdef1234",
  "history": [{
    "at": "2026-08-11T12:00:00Z",
    "event": "CREATED",
    "run_id": "run-20260811115900-abcdef1234",
    "actor": "discovery-agent",
    "reason": "Directly observed during bounded discovery"
  }]
}
```

Use `FACT`, `USER_REQUIREMENT`, `DECISION`, `INFERENCE`, `ASSUMPTION`, `HYPOTHESIS`, or `UNKNOWN`
for `classification`. Use `CURRENT`, `STALE`, `INVALIDATED`, `UNCERTAIN`, or `HISTORICAL` for the
shared knowledge state. Add type-specific lifecycle fields for findings, tasks, contradictions, and
migrations. Keep each assertion narrow enough to invalidate independently.

## Record evidence and provenance

Give every material assertion evidence proportional to its impact. Record:

- Evidence kind: code, test, runtime, documentation, user event, decision, or external source.
- Relationship: supports, refutes, or qualifies.
- Repository ID, path, symbol, line hint, commit, and blob/content digest where applicable.
- Command, exit status, environment digest, timestamp, and retained artifact digest for observations.
- Exact user-event ID for requirements; preserve each sanitized meaningful question and answer as
  one immutable `records/user-events/<id>.json` file.
- Capture time, originating run, redaction state, and collection limitations.

Prefer symbols and content digests over line numbers. Store bounded redacted excerpts only when they
are necessary to preserve meaning. Never store secret values. Mark missing or deleted evidence as
stale or historical; never silently remove the claim it once supported.

## Track freshness by dependency

Record a snapshot vector containing each repository's branch, commit, source-tree digest,
dependency/configuration digests, and dirty-path content hashes. Make every current record declare
source selectors and record dependencies.

On resume or refresh:

1. Compare content and Git history with the last snapshot.
2. Mark records stale when a selected file, symbol, schema, command input, environment, or upstream
   record changed.
3. Propagate staleness through explicit record dependencies.
4. Create a reconnaissance task for changed paths that map to no component or claim.
5. Revalidate affected scopes before restoring `CURRENT`.
6. Rebuild all derived artifacts whose input digest changed.

Apply class-specific rules. Invalidate code claims on relevant source changes. Invalidate test and
runtime claims on source, command, environment, or TTL changes. Invalidate absence claims when
anything is added within the inspected scope. Supersede user intent only with a later explicit user
event. Preserve decisions historically while marking their current applicability uncertain.

Treat dependency selectors as conservative hints, not proof of unaffected behavior. If change
impact cannot be established, mark the affected boundary uncertain and investigate it.

## Handle Git and memory-only commits

Track repository revision and source content independently. Advance the recorded commit after a
commit that changes only `.brownfield/`, but keep code-backed claims current when their dependency
blob hashes are unchanged. Invalidate generated memory views because the canonical memory digest
changed.

When a commit mixes source and memory changes, invalidate from the changed source set and then
verify that accepted memory updates describe the resulting source snapshot. When the prior commit
is not an ancestor, the clone is shallow, or history was rewritten, compare content hashes instead
of assuming a full rebuild is necessary.

Identify uncommitted evidence by content digest. After a later commit, replace only its revision
locator; do not change the underlying conclusion without revalidation. Never call uncommitted
memory portable until it is version-controlled or otherwise durably checkpointed.

## Scope multi-repository and branch knowledge

Assign every repository a stable ID, root locator, authority branch, and snapshot in
`manifest.json`. Scope every source locator and record to one or more repository IDs. Record the
exact revision vector; never imply that separately observed repositories formed an atomic state.

Maintain one canonical current model for the designated integration snapshot. Store feature-branch
and worktree conclusions as run overlays. Promote them only after integration and revalidation.
When branches diverge, compare dependency content rather than branch names; preserve incompatible
claims as scoped alternatives until one becomes canonical.

Place `.brownfield/` in a dedicated memory repository when no single source repository owns the
system. Keep only a small, stable locator in participating repositories if needed. Do not duplicate
the memory tree across repositories.

## Represent migrations explicitly

Create a migration record for architectural, data, API, or long-lived replacement work. Declare
its old and new boundaries, compatibility invariants, phases, cutover criteria, rollback path, and
affected record IDs. Scope claims to `old`, `new`, or `both` while implementations coexist. Retire
old claims only after cutover evidence exists.

Version the memory schema in `manifest.json`. Run schema migrations as dry-run transformations,
retain a pre-migration backup, validate all references, and persist the result as a migration record
plus an immutable run event. Never let an agent silently reinterpret older records.

## Validate and compact safely

Validate schema versions, IDs, references, state transitions, dependency selectors, evidence
locators, generated digests, repository scopes, and secret redaction at every merge and checkpoint.
Flag duplicate current assertions and unsupported high-confidence claims.

Compact only operational noise. Retain exact user Q&A, decisions and rationale, meaningful failed
investigations, supersession links, and evidence summaries. Collapse completed run journals into a
small summary after recovery is no longer possible or needed. Rebuild indexes after compaction and
prove that current records still resolve to their evidence and history.
