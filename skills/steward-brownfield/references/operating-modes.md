# Operating Modes and Run Boundaries

## Contents

- [Separate permission classes](#separate-permission-classes)
- [Select a mode](#select-a-mode)
- [Mode permissions](#mode-permissions)
- [Define the run envelope](#define-the-run-envelope)
- [Apply risk gates](#apply-risk-gates)
- [Escalate or change modes](#escalate-or-change-modes)
- [Stop deliberately](#stop-deliberately)

## Separate permission classes

Treat these as independent permissions:

- **Inspection:** Read files and history, search, and run non-mutating diagnostics.
- **Project-memory writes:** Create or update the configured persistent memory, proposals,
  checkpoints, indexes, and handoff views. Do not treat these as source-code authorization.
- **Source writes:** Change code, tests, product documentation, configuration, dependencies,
  schemas, migrations, or infrastructure definitions.
- **Operational writes:** Change remote repositories, deployments, cloud resources, databases,
  production data, external services, or communications.

Establish the memory location and version-control policy before the first persistent write. Allow
routine memory checkpoints thereafter in every mode unless the user requested a fully read-only
run. Keep temporary diagnostic output outside user-owned paths and remove only artifacts created
by the current run.

## Select a mode

Infer the narrowest mode that satisfies the request. Default to `DISCOVERY` when the request is
ambiguous. Record the selected mode and run envelope before substantive work. Never interpret a
mode name as permission beyond the user's stated scope.

## Mode permissions

| Mode | Project-memory writes | Source writes | Required behavior |
| --- | --- | --- | --- |
| `DISCOVERY` | Yes | No | Reconcile freshness, explore the system, update supported knowledge, and record uncertainty. |
| `AUDIT` | Yes | No | Investigate defects and risks, persist evidence-backed findings, and avoid implementation. |
| `PLAN` | Yes | No | Resolve enough uncertainty to build a dependency-aware plan with validation and rollback steps. |
| `CONSERVATIVE_FIX` | Yes | Limited | Fix only high-confidence, low-ambiguity, locally reversible defects with a small blast radius. |
| `IMPROVE` | Yes | Yes, within scope | Implement confirmed fixes and evidence-backed improvements; preserve behavior unless a change is justified. |
| `VISION_ALIGNMENT` | Yes | Yes, against approved intent | Move implementation toward the approved Project Constitution; escalate protected, breaking, or irreversible changes. |
| `BOUNDED_AUTONOMOUS` | Yes | Only inside the envelope | Run discovery through verification iteratively, subject to every risk gate and stopping condition below. |

Never allow source writes in `DISCOVERY`, `AUDIT`, or `PLAN`, including “helpful” cleanup. Tests,
documentation, generated files, formatting, and dependency lockfiles are source writes.

In `CONSERVATIVE_FIX`, do not change public contracts, persisted data, authorization behavior,
security boundaries, dependency topology, deployment behavior, infrastructure, migrations, or
protected areas without explicit expansion. Require focused regression tests and a clean baseline
comparison for each fix.

In `IMPROVE`, require a confirmed finding or approved objective. Keep changes incremental and
reversible. Escalate product-policy choices, major architectural changes, compatibility breaks,
and high-risk migrations.

In `VISION_ALIGNMENT`, use only current, explicitly approved intent. Treat agent-generated
constitution amendments as proposals until the user approves them. Do not treat user assertions
about current behavior as verified facts.

In `BOUNDED_AUTONOMOUS`, require an explicit envelope. Do not infer permission for production
actions, destructive operations, broad rewrites, or scope expansion from the word “autonomous.”

Operational writes always require explicit authorization describing the target and allowed
effect. A source-writing mode alone never authorizes deployment, publication, production-data
changes, remote pushes, or external messages.

## Define the run envelope

Record at least:

- Objective and selected mode.
- Included repositories, branches, components, and paths.
- Memory location, repository identity, and persistence policy.
- Allowed and forbidden source changes.
- Protected areas and required approvals.
- Maximum accepted risk and blast radius.
- Allowed operational actions, if any.
- Baseline and required verification depth.
- Isolation strategy: shared read-only checkout, single writer, branch, or worktree.
- Time, agent, tool, and context budgets when material.
- Stopping conditions and conditions that require user input.

Treat missing boundaries conservatively. Keep exploration broad enough to understand dependencies,
but keep modifications inside the smallest justified scope.

## Apply risk gates

Classify risk before each meaningful source or operational change:

- **Low:** Local, reversible behavior with strong evidence, focused tests, and no contract or data
  change.
- **Moderate:** Cross-component behavior, public interfaces, dependency changes, performance-sensitive
  paths, or difficult rollback.
- **High:** Authentication or authorization, secrets, production data, destructive migrations,
  infrastructure, irreversible actions, broad rewrites, or uncertain blast radius.

Proceed automatically only when the mode and envelope admit the classification. Increase the gate
when confidence is low, the baseline is already failing, the worktree contains overlapping user
changes, evidence is stale, or rollback is unclear.

Stop and request direction when:

- Intent is materially ambiguous or current sources of authority conflict.
- A protected area, high-risk action, destructive migration, or production system is involved.
- Required access, credentials, environment, or verification cannot be obtained safely.
- Existing user work overlaps the proposed change and cannot be isolated.
- A critical finding lacks independent evidence or a safe validation path.
- The requested outcome requires expanding repositories, components, or operational effects.

For important changes, require an adversarial reviewer who receives raw evidence and attempts to
disprove the conclusion. Do not count a second agent's confidence as independent proof; prefer
tests, runtime observations, static tools, or human approval where risk warrants them.

## Escalate or change modes

Complete the safe work already inside the envelope before escalating. Present the evidence,
proposed expansion, expected benefit, risk, validation, and rollback strategy. Change the recorded
mode or envelope only after explicit authorization. Never downgrade a risk classification merely
to fit the current mode.

## Stop deliberately

Stop the iteration when any applicable condition holds:

- The scoped objective and required verification are complete.
- No unresolved high-priority, high-confidence finding remains inside scope.
- Remaining work is speculative, subjective, deferred, or below the value threshold.
- Further exploration has diminishing expected value.
- User input, new authority, or a major decision is required.
- Risk, scope, or resource use reaches the run envelope.
- The baseline cannot support a trustworthy comparison.

Treat “no change required” as a valid result. Before stopping, checkpoint accepted knowledge,
unresolved contradictions, task state, exact verification snapshots, and the recommended next
action. Never mark work resolved merely because the run ended.
