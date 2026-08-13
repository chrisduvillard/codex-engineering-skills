# Aggregate Views

Use only the views material to the target. Each view lists the evidence needed before it can support a finding.

## Goal and acceptance reconciliation

Compare declared goals and acceptance criteria with the final code, tests, documentation, and observed behavior. Classify divergence as unmet requirement, accepted deviation, added behavior, or outdated specification. Do not infer intent from implementation alone.

Proof: criterion or goal source plus exact implementation, verification, or absence evidence.

## Architecture and dependency delta

Compare module boundaries, dependency direction, APIs, storage, schemas, and deployment topology before and after the range. Use language-native dependency tools when already available; otherwise inspect imports and wiring. Look for new cycles, boundary crossings, hidden shared state, or coupling that changes future work.

Proof: before/after graph or exact changed edges plus the repository convention or architecture contract affected.

## Cross-work integration

Inspect seams between tickets, stories, commits, services, migrations, and rollout steps. These are the places no isolated work item validated end to end. Trace shared inputs, state transitions, error handling, compatibility, ordering, and rollback.

Proof: at least two work-item boundaries plus a reachable behavior, test, or missing verification path.

## Duplication and pattern divergence

Find the same problem solved multiple ways or new code diverging from the surrounding error, naming, validation, testing, and lifecycle conventions. Similar text alone is not duplication; establish duplicated responsibility or divergent behavior.

Proof: exact comparable symbols and the existing convention or shared abstraction.

## Complexity and ownership concentration

Rank paths by full-range churn, then inspect current absolute size, responsibilities, coupling, and testability. High churn or size is not itself a defect. Look for a component that accumulated unrelated responsibilities or became a single coordination bottleneck across work items.

Proof: measured candidate ranking plus current code structure and concrete maintenance consequence.

## Verification and observability gaps

Map declared risks and changed behaviors to unit, integration, end-to-end, migration, rollback, monitoring, alerting, and runbook evidence. Distinguish an untested path from one tested elsewhere. A passing suite proves only what it asserts.

Proof: reachable behavior plus the exact verification or observability surface inspected.

## Domain-specific views

Add security, privacy, accessibility, data integrity, performance, cost, or operability only when the work changes that domain. State the applicable contract or stakeholder harm before searching for issues.

## Common mistakes

- Summing merge churn with constituent commits.
- Calling high churn a god class without reading the current file.
- Treating missing session logs as evidence that no design discussion occurred.
- Inferring root cause from sequence alone.
- Repeating ordinary code-review findings without explaining the cross-work pattern.
- Converting one incident into a systemic lesson without a repeatable mechanism.
- Reporting a process lesson with no source.
