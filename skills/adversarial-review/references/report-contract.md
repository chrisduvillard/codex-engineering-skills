# Reporting contract

Read this before promoting a discrepancy to a finding and before writing the final review.

## Status semantics

- `QUEUED`: A distinct attack is identified but not started. Nonterminal.
- `ACTIVE`: The attack is executing or being adjudicated. Nonterminal.
- `SURVIVED`: The intended attack class was reached within the recorded bound and its oracle held. This says nothing about untested siblings.
- `COUNTEREXAMPLE`: A minimized reproducible observation contradicts the row's stated oracle. This is evidence to adjudicate, not automatically a confirmed defect.
- `COVERED_BY_FINDING`: Cited source/data-flow evidence shows that a distinct sibling partition reaches the exact root cause and consequence of an already-confirmed finding. Link that finding ID.
- `CONTRACT_EXCLUDED`: The governing contract plus cited reachability assumptions exclude the class. Implementation-only non-reachability and coverage absence do not qualify.
- `INCONCLUSIVE`: The attack started, but bounded work could not reach the intended class, the harness/tool failed, evidence was unstable/conflicting, the oracle remained inadequate, or replay/minimization could not finish.
- `BLOCKED`: A named missing oracle, tool, runtime, infrastructure, permission, or safe environment prevented execution.
- `DEFERRED_BY_BOUND`: The attack was intentionally not executed because the declared global campaign budget reached its final reserve.

All statuses except `QUEUED` and `ACTIVE` are terminal. Do not silently turn blocked, deferred, skipped, filtered, flaky, or unreached tests into passes.

Track finding qualification separately from attack status. Link each `COUNTEREXAMPLE` to a confirmed finding ID or `UNVERIFIED`; link each `COVERED_BY_FINDING` row to the confirmed finding it shares. If adjudication shows the oracle was invalid, reset the row to `QUEUED` with a corrected oracle, mark it `CONTRACT_EXCLUDED` when the contract and cited assumptions exclude the partition, or close it `INCONCLUSIVE`/`BLOCKED`. Remove only a recorded duplicate.

## Finding acceptance

Require all of the following:

1. Precise root-cause location in reviewed code; for a deletion or omission, cite the exact diff hunk or nearest causal contract/configuration location.
2. Violated contract, invariant, or security property and its source.
3. Attacker/user preconditions and reachable entry path.
4. Smallest practical input or action sequence.
5. Exact expected and actual behavior.
6. Concrete consequence, not a hypothetical label.
7. Reproduction command/harness, exact input, relevant output, runtime/tool version, and seed/trace/configuration. Also require OS/architecture, compiler, dependency-lock revision, artifact digest, and environment flags when behavior or attribution can depend on them.
8. A controlled target-versus-baseline result when claiming a regression: separate pinned snapshots, identical external harness/input/seed/command/runtime/environment/configuration, target fails, and baseline survives. Otherwise call attribution unknown.

If any element is absent, keep the item as an unverified risk and state what evidence is missing. A counterexample, surviving mutant, coverage gap, static warning, catalogue match, differential disagreement, or flaky run is a hypothesis rather than a finding.

Use attribution terms precisely: `target-only` requires the controlled target to fail while the matched baseline survives; `pre-existing` requires the baseline to reproduce the same violated invariant and mechanism; `environmental` requires a controlled environment change to reproduce or remove the result; otherwise use `unknown`. Initial target failures are not automatically pre-existing.

## Severity

Rank by realistic consequence and reachability, not cleverness or remediation cost:

- `P0`: Immediately exploitable or routinely triggered catastrophic compromise, irreversible data/financial loss, or system-wide safety failure.
- `P1`: High-impact security, integrity, availability, or core correctness failure on a realistic path; release-blocking.
- `P2`: Material but bounded failure requiring narrower conditions or affecting a recoverable subset.
- `P3`: Real, reproducible, low-impact edge defect worth correcting but not release-blocking.

Do not assign severity to unverified risks.

## Final review shape

### Findings

Put findings first, highest severity first. For each one use a concise title and include:

- `Location`: file and tight line range
- `Violated invariant`: contract source
- `Minimal trigger`: exact input or sequence
- `Expected / actual`: observable difference
- `Impact`: why it matters and who can reach it
- `Reproduce`: command/harness plus seed or trace
- `Attribution`: target-only, pre-existing, environmental, or unknown
- `Evidence`: shortest useful output excerpt
- `Direction`: smallest remediation direction only when useful; do not implement it unless asked

Report one finding per root cause and consequence. Keep distinct attacked partitions in the ledger, but list sibling triggers under the same finding rather than inflating the defect count.

When the interface supports inline code comments, attach one tight comment per confirmed finding and keep the final summary self-contained.

### Unverified risks

List only credible in-scope hypotheses that remain unresolved. State the evidence already obtained and the exact missing prerequisite. Do not mix these with findings.

### Attack coverage

Summarize rather than dumping every passing case:

- reviewed target, comparison base/merge-base, and bounded-model closure;
- contracts/oracles used;
- surfaces and edge dimensions attacked;
- techniques, commands, seeds/corpora/configurations, applicable toolchain/environment identity, and bounds;
- ledger counts by terminal status;
- target-versus-baseline comparison;
- final verification result;
- closure classification: `COMPLETE_WITHIN_MODEL` or `PARTIAL`.
- post-run user working-tree delta: explicitly unchanged or unexpected paths left untouched.

### Residual risk

Name inconclusive, blocked, and deferred rows; unavailable environments; uninstrumented dependencies; unreached behavior; nondeterminism; and declared input/time/size/thread/schedule/interaction bounds. If any such row exists, say the review remains partial.

## No-finding language

Use this exact lead when no defect meets the finding bar:

> No confirmed defect met the finding bar within the executed attacks and bounds.

Immediately disclose partial closure when applicable, then give the most important tested surfaces and residual blind spots. Never say “all edge cases pass,” “safe,” “correct,” “exhaustive,” or equivalent.

Use this exact lead whenever closure is partial:

> Closure is `PARTIAL`: [incomplete row IDs and reasons].
