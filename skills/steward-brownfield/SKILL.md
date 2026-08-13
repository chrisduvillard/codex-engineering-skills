---
name: steward-brownfield
description: Build and maintain a durable, evidence-backed project world model for large or long-lived brownfield software systems, then use it to resume work, perform discovery or audits, plan changes, make bounded improvements, align implementation with documented user intent, and hand work to fresh agents. Use when engineering knowledge must persist across sessions or agents, when a repository needs systematic multi-domain analysis, or when the user requests discovery, audit, conservative fixes, improvement, vision alignment, or bounded autonomous work. Do not use for isolated small edits or ordinary point-in-time code review.
---

# Steward Brownfield Projects

Operate as a persistent engineering institution whose workers are disposable and whose validated
knowledge survives them. Center every run on:

`initialize or resume → refresh affected knowledge → perform mode-scoped work → verify → checkpoint`

Keep the system small. Use portable files, deterministic tooling, repository-native authorities,
and dynamic specialists only where they add value.

## Preserve the invariants

- Understand before modifying.
- Treat source, tests, configuration, and runtime observations as evidence of implemented behavior.
- Treat approved current user intent as authority for intended behavior.
- Treat `.brownfield/` as a fallible, evidence-backed belief model; never let it override stronger evidence.
- Keep facts, user requirements, user assertions, decisions, inferences, assumptions, hypotheses,
  unknowns, freshness, and workflow state distinct.
- Preserve contradictions rather than resolving them by preference or last-writer-wins.
- Keep existing glossaries, ADRs, architecture documents, and repository instructions authoritative
  for their stated scope. Register and cite them instead of duplicating them.
- Let specialists write immutable proposals. Let one coordinator write canonical project memory.
- Protect dirty worktrees and unrelated user work. Never stash, reset, overwrite, or absorb it.
- Scale verification and independent falsification with risk and impact.
- Accept `NO_CHANGE_REQUIRED`, rejected findings, and stopped investigations as valid outcomes.
- Persist conclusions, evidence locators, meaningful failed approaches, and resume state; never
  persist chain-of-thought, secrets, raw production data, or unlimited logs.

## Start every invocation safely

1. Read repository instructions, glossary/context files, ADRs, and native architecture aids before
   naming concepts or running project commands.
2. Resolve this skill's directory and use `scripts/brownfield.py`; do not copy its logic into the
   project. The CLI uses only the Python standard library.
3. Run `status` before any persistent or source write:

   ```bash
   python3 <skill-directory>/scripts/brownfield.py --json status --root <project-root>
   ```

4. Route by classification:
   - `NEW`: establish the memory location, version-control policy, repository scope, and sensitivity
     policy. Initialize `.brownfield/` only if project-memory writes are in scope.
   - `READY`: load the stamped handoff, current model, constitution, and relevant records.
   - `STALE`: start a run, inspect the change set, apply targeted invalidation, and revalidate only
     affected knowledge.
   - `RESUMABLE`: reconcile the active run, contributions, source changes, and checkpoints before
     dispatching new work.
   - `RECOVERY_REQUIRED`: make no canonical or source writes until validation or transaction recovery
     succeeds.
5. Infer the narrowest operating mode that satisfies the request. Default ambiguity to `DISCOVERY`.
   Read [operating-modes.md](references/operating-modes.md) before selecting permissions or risk gates.
6. Begin a run with an explicit objective, scope, risk ceiling, allowed/forbidden paths, verification,
   and stopping conditions. Pass `--authorize-source-writes` only when the request actually grants it.
7. Read [workflow.md](references/workflow.md) for the applicable lifecycle sections. Do not execute all
   phases mechanically when the project is already understood.

Initialize a new memory without changing project source:

```bash
python3 <skill-directory>/scripts/brownfield.py init --root <project-root> --name <project-name>
```

Begin a discovery run:

```bash
python3 <skill-directory>/scripts/brownfield.py begin \
  --root <project-root> \
  --mode DISCOVERY \
  --objective "Build the initial evidence-backed system model" \
  --scope "Repository-wide reconnaissance; no source changes"
```

## Maintain the project world model

Read [state-model.md](references/state-model.md) before initializing memory, changing schemas,
recording important knowledge, invalidating records, handling multiple repositories or branches,
or compacting history.

Use these truth layers:

1. Implemented reality: code, tests, configuration, observed runtime, and external systems.
2. Intended reality: approved constitution and unsuperseded user requirements.
3. Current belief: scoped, evidence-backed project records with explicit uncertainty and freshness.

Record one bounded assertion per typed JSON file. Attach direct evidence proportional to impact and
include repository ID, relative path, symbol/query, content digest, source snapshot, verification
method, and limitations where relevant. Treat line numbers only as navigation. Require at least one
primary source for a high-confidence fact; do not let summaries cite other summaries in a circular
chain.

Use source-content fingerprints rather than commit IDs alone. Exclude `.brownfield/` from source
fingerprints so memory-only commits do not stale code claims. Prefer false-stale to false-current when
impact is uncertain. Never let code changes supersede user requirements; they may instead expose a
contradiction or vision gap.

Keep current model documents concise and semantic: project purpose, capabilities, boundaries,
components, interfaces, data/runtime flows, tests, infrastructure, invariants, constraints, and
uncertainty. Do not substitute a file inventory. Stamp derived indexes, freshness reports, handoffs,
and context packages with their canonical digest and source snapshot; reject stale derived views.

## Understand the user’s intended system

Ask only questions that can materially change behavior, architecture, safety, priority, or
implementation. Classify them as blocking, high-value, or non-blocking; do not ask curiosity
questions. Record any non-blocking assumption before relying on it.

Preserve a sanitized meaningful question-and-answer event and synthesize current intent separately.
When intent changes, supersede the old requirement without erasing it. Treat a user's statement about
existing behavior as `USER_ASSERTION` until verified.

Maintain the Project Constitution as approved intended state. Include product and architecture
principles, invariants, non-goals, constraints, protected areas, UX/performance/security/reliability
requirements, and temporary compromises. Present agent-generated constitution changes as visible
proposals and obtain user approval before treating them as authoritative.

## Create a dynamic engineering organization

Perform reconnaissance before choosing specialists. Allocate by architectural boundary, domain,
coupling, operational risk, and independent-verification need—not lines of code or available slots.
Use parallelism only for genuinely independent read-only work or isolated worktrees.

Read [coordination.md](references/coordination.md) before delegating, accepting agent work, allowing
parallel source edits, building context packages, reviewing important findings or changes, resolving
conflicts, or recovering an interrupted run.

Give every specialist a durable contract containing:

- Mission, questions, scope, task ID, dependencies, and definition of done.
- Base memory revision, exact source snapshot, and relevant entity versions.
- Focused context, known stale inputs, requirements, invariants, contradictions, and prior attempts.
- Read scope, source-write allowlist, protected areas, and inherited run envelope.
- Evidence standard, required checks, output location, and escalation conditions.

If subagents are unavailable, execute the same contracts sequentially. Do not make persistent memory
depend on a specific agent platform.

Build a bounded context package from explicit record IDs and task terms:

```bash
python3 <skill-directory>/scripts/brownfield.py context \
  --root <project-root> \
  --mission "<agent mission>" \
  --record <record-id> \
  --max-chars 24000
```

Have workers stage immutable contributions. Require the coordinator to validate freshness,
sensitivity, evidence, scope, and expected record revisions before merge. Reject stale-base updates;
re-evaluate and stage a new proposal. Preserve competing semantic claims as a contradiction. Never
use last-writer-wins.

For important findings or changes, assign a reviewer a falsification mission using raw artifacts and
necessary context without leaking the desired conclusion. Repeated model confidence is not
independent proof; prefer tests, runtime evidence, static tools, or human approval.

## Audit, prioritize, and improve

Audit risk-first: security, data integrity, correctness, reliability, concurrency, failure handling,
public contracts, migrations, operational paths, performance, test validity, missing functionality,
and deviations from approved intent. Separate severity, confidence, blast radius, and preference.

Persist findings before prioritizing them. Build a dependency-aware task graph that accounts for
user impact, business importance, reversibility, cost, root-cause leverage, and regression risk. Do
not fix in discovery order and do not manufacture work.

Before source changes:

1. Confirm the mode and run envelope authorize the exact change.
2. Capture branch, commit, dirty paths, relevant checks, known failures, and observed behavior.
3. Identify requirements, dependencies, rollback, regressions, and validation criteria.
4. Isolate modifying agents with worktrees or serialize writers.

Implement the smallest coherent root-cause solution. Prefer deletion, simplification, consolidation,
and reuse over new layers or dependencies. Run focused checks while iterating and broader checks in
proportion to risk. Compare against the baseline and independently review important work.

Never infer operational authority from a source-writing mode. Deployment, publication, remote pushes,
external messages, cloud changes, production data, and destructive actions require explicit target-
specific authorization.

## Checkpoint, finish, or abort

Advance run stages durably: `INITIALIZED → INVESTIGATING → [CHANGING] → VALIDATING → REVIEWING →
MERGING → COMPLETE`. Omit `CHANGING` when source writes are not authorized. At each boundary, persist
accepted/rejected knowledge, relevant evidence, baseline comparison, tests, uncertainty, task state,
and the next safe action.

Before finishing:

1. Accept or explicitly reject every staged contribution.
2. Validate memory strictly and reconcile incomplete transactions.
3. Verify results against the exact current source snapshot.
4. Update the current model, approved constitution if applicable, and durable task/finding states.
5. Rebuild the deterministic index, freshness report, and new-agent handoff.
6. Write a concise run summary containing changes, findings, decisions, tests, residual risk,
   blockers, and next priorities.
7. Run `finish`; do not mark tasks resolved merely because the run ended.

If an exact required check fails and the active run cannot be certified, use the one-way `abort`
transition described in [workflow.md](references/workflow.md). `abort` preserves the last nonterminal
stage, records `ABORTED`, leaves `final_snapshot` null, writes a durable `abort.md` and abort event,
and clears the active-run pointer without advancing the last completed run or accepted snapshot. It
does not certify the work, satisfy the failed check, discard contributions, or revert source. Inspect
the retained state and start a new successor run; never resume, finish, or repurpose the aborted run.

Use `recover` after an interrupted canonical merge or a crash during terminal-state publication. It
completes the recorded write-ahead transaction, or reconciles an already-terminal run with a stale
active-run pointer; it never guesses, reverts source, discards user work, or promotes an aborted
snapshot.

## CLI reference

Use `python3 <skill-directory>/scripts/brownfield.py <command> --help` for exact arguments.

| Command | Purpose |
| --- | --- |
| `status` | Classify new, ready, stale, resumable, or recovery-required state without mutation. |
| `init` | Create the portable `.brownfield/` skeleton and copied schemas; refuse overwrite. |
| `snapshot` | Capture a source vector that excludes memory-only changes. |
| `begin` | Persist the mode, immutable run envelope, baseline, and stopping conditions. |
| `record-template` | Create a typed evidence-record skeleton. |
| `contribution-template` | Create a proposal against the active memory revision and source snapshot. |
| `stage` | Atomically stage a unique immutable contribution; allow concurrent workers. |
| `merge` / `reject` | Let the sole coordinator accept or durably reject a contribution. |
| `refresh` | Report targeted staleness; use `--apply` only inside an active run. |
| `context` | Retrieve task-scoped current knowledge within a character budget. |
| `checkpoint` | Advance exactly one permitted run stage with a concise summary. |
| `render` | Deterministically rebuild derived index, freshness, and handoff views. |
| `recover` | Complete an interrupted memory transaction or reconcile a closed run. |
| `validate --strict` | Fail closed on schema, safety, provenance, link, or transaction problems. |
| `finish` | Refuse closure until contributions, validation, views, and summary are complete. |
| `abort` | Terminally record an exact failed required check without certifying or reverting the run. |

## Read references progressively

- Read [state-model.md](references/state-model.md) for storage, record semantics, evidence, freshness,
  Git behavior, multi-repository scope, migrations, and compaction.
- Read [operating-modes.md](references/operating-modes.md) for permission classes, mode selection,
  risk gates, run envelopes, escalation, and stopping.
- Read [workflow.md](references/workflow.md) for reconnaissance, synthesis, user intent, audit,
  prioritization, implementation, verification, security, growth control, and recovery.
- Read [coordination.md](references/coordination.md) for dynamic specialists, agent contracts,
  immutable proposals, context retrieval, independent review, conflicts, and resumability.
