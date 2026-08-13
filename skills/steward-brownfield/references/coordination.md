# Coordination, Review, and Recovery

## Contents

- [Assign explicit roles](#assign-explicit-roles)
- [Start or resume a run](#start-or-resume-a-run)
- [Issue bounded agent contracts](#issue-bounded-agent-contracts)
- [Use immutable proposals and one writer](#use-immutable-proposals-and-one-writer)
- [Coordinate source modifications](#coordinate-source-modifications)
- [Build focused context packages](#build-focused-context-packages)
- [Require risk-scaled adversarial review](#require-risk-scaled-adversarial-review)
- [Resolve conflicts without erasing them](#resolve-conflicts-without-erasing-them)
- [Recover interrupted work](#recover-interrupted-work)
- [Checkpoint and stop deliberately](#checkpoint-and-stop-deliberately)

## Assign explicit roles

Assign one coordinator per memory root. Let it own task assignment, canonical-memory merges, source
integration, policy enforcement, and checkpoints. Let exploration, implementation, and review
agents remain disposable workers.

Create specialists only after reconnaissance identifies a meaningful architectural, domain, or
risk boundary. Prefer complementary scopes. Use duplicate analysis only to challenge a high-impact
conclusion. Never use agent count as a success metric.

Permit many agents to read and propose concurrently. Permit exactly one coordinator to write
canonical memory at a time. Do not let an agent confirm its own high-impact finding or serve as the
only reviewer of its own important change.

## Start or resume a run

Before dispatching work:

1. Read repository instructions and existing authoritative project artifacts.
2. Locate or initialize `.brownfield/` without modifying project source.
3. Inspect open runs, task leases, unresolved merge transactions, repository status, and user work.
4. Capture the repository snapshot vector and pre-existing validation baseline.
5. Write `runs/<run-id>/run.json` with mode, scope, immutable autonomy envelope, budgets,
   snapshot, and stopping conditions.
6. Refresh freshness and reconcile stale or unmapped knowledge.
7. Select the smallest useful task set and specialist organization.

Default a new project to discovery. Never infer source-write permission merely because the skill
was invoked. Inherit the run envelope unchanged in every child agent. Stop rather than widen scope,
risk, permissions, or budgets implicitly.

## Issue bounded agent contracts

Give each agent a contract containing:

- Mission, task ID, questions, scope, dependencies, and definition of done.
- Read scope, source write allowlist, protected and forbidden areas.
- Base repository snapshot, base memory digest, and relevant entity versions.
- Focused context package and known stale or uncertain inputs.
- Required evidence, checks, output schema, and escalation conditions.
- Mode, risk ceiling, resource boundary, and approval gates inherited from the run.

Assign a task to one owner at a time. Record the owner, lease, baseline, attempt number, and state
before dispatch. Let reviewers remain read-only unless separately assigned an implementation task.
Require agents to report uncertainty, negative results, failed approaches, and partial completion.

## Use immutable proposals and one writer

Make each agent write a unique immutable submission. Include:

```json
{
  "contribution_id": "sub-...",
  "task_id": "task-...",
  "base_memory_revision": 7,
  "base_knowledge_digest": "...",
  "base_record_revisions": {"claim-...": 3},
  "operations": [],
  "evidence": [],
  "source_change_ref": null,
  "checks": [],
  "uncertainties": []
}
```

Allow operations to propose create, update, supersede, invalidate, or transition. Do not let a
proposal directly mutate canonical records.

Have the coordinator merge under an exclusive lock:

1. Validate the submission, task ownership, policy, scope, evidence, IDs, and state transitions.
2. Compare its base digest and entity versions with current state.
3. Deduplicate equivalent additions and route incompatible conclusions to a contradiction.
4. Write a merge-intent event containing expected before/after hashes.
5. Stage files, replace each atomically, and append a merge-commit event with the resulting digest.
6. Rebuild affected derived views and release the lock.

Make merge operations idempotent by submission ID. On stale versions, reject or request a rebase;
never apply last-writer-wins. Use the write-ahead hashes to finish or roll back an interrupted
multi-file merge without guessing.

## Coordinate source modifications

Prefer an isolated branch or worktree for each modifying task. Assign non-overlapping write scopes
and integrate patches one at a time. If isolation is unavailable, permit only one source writer.
Never stash, reset, overwrite, or incorporate unrelated user work.

Before applying a proposal, compare its base files and dependency snapshot with the current tree.
Require rebase and renewed analysis when relevant inputs changed. Integrate the smallest coherent
change, run targeted checks, then run broader checks in proportion to risk. Update memory only for
the integrated source state, not for an abandoned branch.

Gate destructive actions, production or deployment changes, secrets, data migrations,
authentication or authorization, public contracts, new dependencies, broad rewrites, and protected
areas on explicit authority. Preserve a rollback path for high-risk work.

## Build focused context packages

Derive context from the agent mission, task links, components, paths, symbols, requirements, and
dependency graph. Include, in order:

1. Applicable constitution rules, user requirements, invariants, and protected areas.
2. Task objective, scope, definition of done, mode, and current repository snapshot.
3. Directly relevant current records, decisions, findings, and evidence locators.
4. Unresolved contradictions, stale inputs, previous attempts, and rejected approaches.
5. One-hop dependencies and deeper history only when the mission requires them.

Enforce a token budget. Prefer current summaries and identifiers over raw history or full logs.
Never hide omitted critical material to fit the budget; shrink the task or escalate instead.

Attach a context manifest containing memory digest, record IDs and versions, repository revisions,
freshness states, omissions, and token estimate. Store packages as derived runtime artifacts. Build
the new-agent handoff from the same retrieval rules, but keep it concise and stamped so a fresh
agent can reject a stale handoff.

## Require risk-scaled adversarial review

Move important findings through proposed, validating, and then confirmed, rejected, or uncertain.
Scale review depth with severity, confidence, blast radius, irreversibility, security, data
integrity, architectural significance, and user impact.

Assign an independent reviewer a falsification mission. Give it the raw artifact, requirement, and
necessary context without the original agent's private reasoning or desired conclusion. Require it
to search for intent, contrary evidence, hidden consumers, edge cases, tests that pass for the wrong
reason, and a less invasive explanation or solution.

Move important changes through implementing, verifying, and then resolved or reopened. Compare
post-change results with the recorded baseline. Treat “no change required” and a rejected finding
as valid outcomes when evidence supports them.

## Resolve conflicts without erasing them

Distinguish mechanical conflicts from semantic contradictions. Rebase or reject mechanical
conflicts. Preserve incompatible semantic claims and create a contradiction record with evidence,
owners, affected records, resolution criteria, and current status.

Apply authority by question, not by a universal precedence rule:

- Use code, tests, configuration, and runtime evidence to determine current implementation.
- Use current unsuperseded user intent to determine desired product behavior.
- Use accepted decisions and ADRs to determine documented rationale.
- Treat tests and documents as fallible evidence when they disagree with behavior or intent.

Ask the user only when resolution materially depends on intent or risk. Preserve the exact answer,
supersede the old requirement explicitly, and update dependent records. Never rewrite history to
make the conflict disappear.

## Recover interrupted work

Treat run and task transitions as durable state. Renew leases only while an agent is active. On
resume:

1. Find open runs, incomplete merge intents, expired leases, unmerged submissions, and task states.
2. Complete or roll back memory transactions from recorded hashes.
3. Compare source status and content hashes with every task baseline.
4. Classify partial source work as recoverable, externally changed, conflicted, or unknown.
5. Move uncertain partial work to investigation or verification before redispatch.
6. Reclaim expired tasks only after confirming no active writer remains.
7. Re-run checks whose inputs changed and preserve still-valid results.

Never mark a task complete from an agent message alone. Require accepted evidence and persisted
state. Never repeat a source operation merely because its completion event is missing; inspect the
tree first. Never recover by reverting unrelated user changes.

## Checkpoint and stop deliberately

Checkpoint after each accepted meaningful result, integrated source change, resolved
contradiction, and verification boundary. Persist task histories, baseline comparison, decisions,
evidence, changed records, remaining uncertainty, and recommended next work. Update the handoff and
freshness stamp.

Commit related memory with the source change when commit authority exists. Use a memory-only commit
for discovery or audit checkpoints when useful. Otherwise leave an explicit uncommitted-memory
warning; local files are crash-durable but not portable to a fresh clone.

Stop when the run envelope is exhausted, risk or scope would expand, user input is required,
important checks fail, diminishing returns dominate, or no permitted high-value work remains. Close
the run with a compact summary and retain meaningful failed investigations. Do not continue merely
to produce more findings, agents, or changes.
