---
name: adversarial-review
description: Falsify a code change with evidence-backed edge-case, state, failure, concurrency, resource, and security attacks. Use for bounded correctness or security testing of a change; not for a broad architecture audit.
---

# Adversarial Review

Try to falsify the code's claimed behavior. Treat existing tests, static warnings, and coverage as evidence that guides attacks, never as proof of correctness.

## Execution profiles

- **Fast:** one focused attack ledger, one safe technique, and one minimization pass.
- **Standard:** adaptive attacks across material partitions plus reproduction and counterevidence.
- **Deep:** multiple techniques, platform or concurrency checks, and independent challenge for authentication, money, migrations, destructive effects, or public contracts.

Choose by consequence and uncertainty rather than diff size alone.

## Operating contract

- Do not edit product code unless the user explicitly asks for a fix. Do not add or edit tests unless the user explicitly asks for test changes. Put one-off harnesses, corpora, caches, build outputs, and reports in disposable storage; compare working-tree state before and after execution and never clean unexpected writes from the user's tree.
- Read repository instructions, domain vocabulary, architecture records, and the relevant specification before naming behavior or choosing an oracle.
- Preserve dirty work and distinguish the reviewed target from unrelated local changes.
- Use the repository's installed toolchain. Do not install a dependency merely to obtain a technique; choose the closest available attack or mark it blocked.
- Treat reviewed code as executable content. Execute it only from a disposable snapshot with the user's worktree absent or read-only and scratch/output mounts writable. Before running it, assess provenance and trust. Run untrusted or uncertain code only in an ephemeral sandbox with no credentials, restricted network, minimal mounts, and explicit CPU/memory/process/time limits; otherwise stay source-only and mark dynamic attacks blocked.
- Exercise only local, test, or explicitly authorized sandbox targets. Do not scan live services, send adversarial traffic to third parties, run migrations or deployments, expose secrets, or perform destructive/resource-exhaustion tests without explicit authorization.
- Bound the whole campaign and each randomized, fuzz, load, fault, or schedule exploration before starting. Never accept an indefinite default run.
- Do not promise literal exhaustive testing. Except for tiny finite domains, all possible inputs and schedules cannot be executed. Make “every edge case” operational: derive a finite attack model from scoped evidence, give every derived row an honest terminal disposition, and disclose deferred work and blind spots.

## Load the references selectively

- Read [adversarial-lenses.md](references/adversarial-lenses.md) while deriving attacks. Apply only lenses justified by the scoped behavior.
- Read the relevant sections of [technique-playbook.md](references/technique-playbook.md) before using a dynamic technique. Prefer tools already configured by the project.
- Read [report-contract.md](references/report-contract.md) before constructing the ledger. Its status and finding definitions are authoritative.

## 1. Pin scope, comparison, and safety

1. Resolve exactly what is under review: a fixed-point diff, PR/branch, commit range, file, function, or behavior. For a diff review, record the merge-base and commit list. If no base was named, infer the repository's default base when unambiguous and state the assumption.
2. Capture working-tree state before running anything. Do not attribute pre-existing or unrelated edits to the target.
3. Identify the governing contract in this order: explicit spec and acceptance criteria; public API/schema/type contract; architecture/domain decisions; callers and consumers; established tests; a simple independent model. Keep intended behavior separate from current implementation.
4. Map changed behavior to reachable entry points, callers, state owners, effects, trust boundaries, and failure containment. Expand beyond changed lines when the changed behavior can break an unchanged consumer or control.
5. Apply the executable-content trust gate from the operating contract before any build, test, hook, or package command. If isolation is required but unavailable, continue statically and record the blocked dynamic work.
6. Discover existing test, coverage, fuzz, sanitizer, race, and mutation commands without executing them.
7. Define the test envelope and a global campaign budget: permitted side effects; maximum time/cases/depth/size/threads/schedules; unavailable infrastructure; and a named final reserve for replay, minimization, baseline comparison, and reporting (default 20%). Choose proportionate bounds when the user supplied none.
8. Create a disposable target snapshot before executing any reviewed code, including ordinary tests and build hooks. Keep the user's worktree unmounted or read-only; redirect caches, corpora, coverage, builds, temporary files, and other outputs to scratch. Treat redirection as additional containment, never as a substitute for snapshot isolation.
9. Run the cheapest bounded focused initial test in the disposable target snapshot only when safe. Record initial failures with attribution unknown until a controlled comparison.
10. When attribution matters, prepare separate disposable target and baseline snapshots pinned to exact revisions or recorded content digests. Use the same externally stored harness, input, seed, command, runtime, environment, and relevant configuration in both; record intentional lock/config differences. Never switch or overwrite the user's working tree.

## 2. Build the live attack ledger

Create a coordinator-owned ledger. Keep it in conversation or disposable scratch storage unless the user requests an artifact. First screen the lenses and router for applicability; record a short rationale for excluded dimensions or unselected techniques without creating fake blocked rows. Record shared campaign context once, then let rows reference it.

Use these fields:

| Field | Meaning |
|---|---|
| ID | Stable attack identifier |
| Surface | Entry point, branch, state transition, trust boundary, or effect |
| Invariant | Behavior that must remain true |
| Adversary goal | How the invariant could be broken or abused |
| Dimension and partition | Exact value class, interaction, failure, or sequence to attack |
| Oracle | Expected result or justified relation |
| Technique | Cheapest discriminating experiment |
| Bound | Cases, seed, time, size, depth, or schedule limit |
| Execution context | Campaign-context reference plus row-specific executable/runtime/tool versions and relevant flags |
| Evidence | Command/harness, input/trace, and observed output |
| Attribution | Target-only, pre-existing, environmental, or unknown |
| Finding / covered by | Confirmed finding ID, `UNVERIFIED`, or `—` |
| Status | One authoritative status from [report-contract.md](references/report-contract.md) |

Derive rows from evidence, not from a universal checklist:

1. Split every relevant predicate, type restriction, schema rule, loop, state transition, and error contract into equivalence partitions.
2. Put exact boundaries and nearest representable values on both sides into separate rows.
3. Derive relational and sequence attacks from data flow, callers, transformations, transaction boundaries, retry logic, and state ownership.
4. Add interaction rows where dimensions can couple. Use covering combinations rather than a blind Cartesian product; increase interaction strength around high-impact coupling or observed failures.
5. Turn threat-model assets, actors, entry points, and trust boundaries into abuse cases when security or tenant/role integrity is in scope.
6. Seed rows from historical bugs, regression tests, static analysis, uncovered changed branches, surviving mutants, and production-shaped fixtures. Treat each as a lead until runtime or source proof establishes it.
7. Merge duplicate rows. Add a row only when it contributes a distinct partition, interaction, oracle, caller, state sequence, or consequence.
8. Rank the queue by consequence, reachability, change proximity, oracle strength, uncertainty, and experiment cost. Prefer the attack with the greatest expected information, not simply the easiest input.

## 3. Run the adaptive attack loop

Repeat until the closure rule is satisfied:

1. Select the highest-value unresolved ledger row.
2. Choose the narrowest technique that can falsify its invariant. Use the router below, then follow the relevant playbook section.
3. Confirm that the attack reaches the intended class. A generated test that rejects, filters, skips, or early-returns is not evidence that the class survived.
4. Execute with a recorded seed/configuration and explicit bound. Capture enough raw evidence to replay the observation.
5. Update the row immediately using [report-contract.md](references/report-contract.md):
   - On expected behavior, mark only the exact attacked partition `SURVIVED`; do not close its siblings.
   - On a reproducible discrepancy, minimize the input or action sequence and mark it `COUNTEREXAMPLE`. Qualify it separately as a confirmed finding only after it meets the finding bar; otherwise link it to `UNVERIFIED`.
   - When a distinct sibling partition reaches the exact already-confirmed mechanism and consequence by cited source/data-flow evidence, link the finding and mark it `COVERED_BY_FINDING`; do not manufacture a duplicate finding or redundant execution.
   - Mark an executed row `INCONCLUSIVE` when bounded work cannot reach the intended class, the harness/tool fails after starting, evidence is unstable/conflicting, the oracle remains inadequate, or replay/minimization cannot finish. Name what would resolve it.
   - Mark a row `CONTRACT_EXCLUDED` only when the governing contract and cited reachability assumptions exclude that class. Implementation-only non-reachability of contract-required behavior remains a counterexample or inconclusive risk.
   - When a required oracle, runtime, service, tool, or safe environment is unavailable before execution, record the missing prerequisite and mark it `BLOCKED`.
6. Compare a minimized discrepancy through the controlled target/baseline experiment from step 1 when feasible. Use `target-only` only when the isolated target fails and the matched baseline survives. Use `pre-existing` only when the matched baseline reproduces the same violated invariant and mechanism; use `environmental` only when a controlled environment change reproduces or removes it. Otherwise use `unknown`. Never infer attribution from the diff alone.
7. Expand the frontier after every surprise or failure. Add only distinct adjacent values, alternate encodings, shorter and longer sequences, reordered/replayed operations, sibling callers, other instances of the root-cause pattern, stronger interactions, or an independent oracle. Group partitions that share one proven mechanism and consequence under one finding ID.
8. Re-rank the whole queue after each result. Let passes redirect effort: unreached branches require a better generator/harness; weak observations require a stronger oracle; fuzz plateaus require better seeds/dictionaries/structure; surviving mutants require assertion-focused attacks; flaky results require deterministic control before interpretation.
9. Escalate case counts or expensive techniques only when consequence, uncertainty, missed reach, or a surprise justifies them. A small pure change may close with decision tables and focused differential/property probes; do not run every technique.
10. When the campaign reaches its final reserve, stop launching new exploration. Merge the queue, mark unexecuted rows `DEFERRED_BY_BOUND`, and spend the reserve replaying, minimizing, attributing, and reporting. Transition any active row that cannot finish adjudication to `INCONCLUSIVE`. Do not silently extend the global budget.
11. Re-run the directly affected focused tests after each confirmed counterexample. Do not fix product code unless asked.

### Technique router

| Evidence shape | Primary attack |
|---|---|
| Comparison, clamp, parser branch, validation rule | Boundary/decision table plus adjacent representable values |
| Pure or deterministic transformation over a broad domain | Property-based generation and shrinking |
| Parser, decoder, protocol, file format, or byte/string boundary | Coverage-guided or structured fuzzing; add applicable sanitizers |
| Workflow, lifecycle, cache, transaction, retry, or reusable object | Model-based or rule-based stateful sequences |
| Exact output oracle is unavailable | Metamorphic relations with explicit preconditions |
| Independent model, prior version, backend, algorithm, or configuration exists | Differential testing over defined behavior |
| Filesystem, database, subprocess, network, queue, clock, or dependency | Deterministic fault injection and partial-failure tests |
| Shared mutable state, async work, locks, or cancellation | Controlled schedule exploration, replay traces, and a race detector |
| Native memory, unsafe arithmetic, lifetime, or uninitialized data | ASan/UBSan/MSan as applicable, in separate instrumented runs |
| Executed code may be weakly asserted | Selective mutation testing on changed/high-risk code, then triage survivors |
| Authorization, tenant, identity, secret, or trust-boundary change | Abuse-case tests and source-to-sink/control tracing |

Use parallel agents only for genuinely disjoint surfaces. Keep one coordinator responsible for the evolving ledger, cross-surface discoveries, attribution, and closure. Do not launch a fixed fan-out and call it dynamic coverage.

## 4. Enforce the finding bar

Apply the sole normative finding criteria in [report-contract.md](references/report-contract.md). Keep every counterexample, differential disagreement, surviving mutant, coverage hole, static warning, suspicious pattern, or flaky failure as a hypothesis until it meets that contract; otherwise report it only as an unverified risk with the missing evidence.

## 5. Close the bounded attack model

Finish only when all conditions hold:

1. Every ledger row has a terminal status from [report-contract.md](references/report-contract.md); none remain queued or active.
2. Every relevant changed predicate/error branch and each contract-derived input partition is reached, covered by the exact mechanism of a confirmed finding, contract-excluded under cited assumptions, or explicitly incomplete (`INCONCLUSIVE`, `BLOCKED`, or `DEFERRED_BY_BOUND`).
3. Relevant interaction, state/sequence, failure, time, permission, concurrency, resource, representation, and configuration dimensions from the lenses have a disposition. Justify excluded dimensions from the scoped contract/data flow; do not run irrelevant techniques merely to say they passed.
4. For each selected technique, record applicable reach, distribution, coverage, mutant, corpus, or schedule evidence. Metrics expose gaps but never certify correctness. Give each unselected expensive technique a short risk-based rationale rather than a fake ledger row.
5. Each confirmed finding has been minimized, replayed, attributed when possible, expanded to adjacent/root-cause-related attacks, and deduplicated so one root cause and consequence is reported once with sibling triggers beneath it.
6. Re-read the diff/source, contracts, callers, and ledger once more. Add any distinct newly visible row while exploration budget remains; otherwise mark it `DEFERRED_BY_BOUND`.
7. Run the repository's proportionate final verification if it is safe and within review scope. Create or reopen a ledger row for every relevant surprise or blocked check, then recompute closure. Leave only demonstrably unrelated failures as report-only context.
8. Compare the user's working-tree state with the pre-run snapshot. Record it as unchanged or list every unexpected path and leave those paths untouched.

Classify closure as `COMPLETE_WITHIN_MODEL` only when no row is `INCONCLUSIVE`, `BLOCKED`, or `DEFERRED_BY_BOUND`, and every counterexample is linked to a confirmed finding. Otherwise classify it as `PARTIAL` and name the incomplete rows. A terminal ledger is auditable; it is not automatically complete.

## 6. Report findings and bounded residual risk

Follow [report-contract.md](references/report-contract.md). Put confirmed findings first, ordered by severity. Then summarize the attack ledger, tested bounds, baseline comparison, and blocked or untested areas.

Use the exact no-finding and partial-closure language from [report-contract.md](references/report-contract.md). Never say the code is correct, safe, exhaustive, or that “all edge cases pass.”
