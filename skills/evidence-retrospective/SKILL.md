---
name: evidence-retrospective
description: Reconstruct completed engineering work from goals, diffs, tests, CI, runtime evidence, and prior commitments. Produce sourced systemic lessons and owned follow-up actions; do not implement remediation.
---

# Evidence Retrospective

Review the evidence a body of work left behind. Surface lessons no single ticket, commit, or coding session could see, then route each lesson into a concrete disposition without inventing motives or blame.

## Execution profiles

- **Fast:** one small completed change, two aggregate views, and at most three sourced findings.
- **Standard:** material aggregate views plus targeted runtime verification.
- **Deep:** independent analysts across a milestone or release, prior-action follow-through, and a verdict when declared criteria exist.

Escalate for migrations, incidents, public contracts, or cross-service work even when commit count is small.

## Operating contract

- Default to read-only analysis and a report in chat. Write a retrospective artifact only when the user requests one or the surrounding workflow already authorizes project documentation.
- Pin the target and baseline before judging it. Preserve dirty work and distinguish post-target changes from the work under review.
- Every finding must cite a file, line, commit, test result, runtime observation, ticket, specification, or recorded decision.
- Treat memory, meeting recollection, and user concerns as leads. They become findings only when evidence supports them; otherwise keep them as questions or perspectives.
- Distinguish **checked and no issue found**, **no evidence found**, **not checked**, and **unsafe to check**.
- Prefer deterministic measurements over impressions, but never turn a metric into a finding without reading the underlying code or behavior.
- Analyze systems and process conditions, not personal blame. Do not infer why someone acted unless a source records it.
- Propose remediation and process changes; do not apply them during the retrospective.

## Load the references

- Read [references/evidence-inventory.md](references/evidence-inventory.md) before gathering evidence or choosing a diff range.
- Read [references/aggregate-views.md](references/aggregate-views.md) before assigning or performing cross-work analysis.
- Read [references/agent-briefs.md](references/agent-briefs.md) before delegating evidence analysis or discussion.
- Read [references/retrospective-record.md](references/retrospective-record.md) before consolidating findings, actions, and any delivery verdict.

## 1. Fix the retrospective boundary

Resolve:

- the completed feature, milestone, release, sprint, epic, migration, incident follow-up, or explicit revision range;
- repository root, current revision, branch, and working-tree state;
- the baseline immediately before the work and the endpoint that contains it;
- the declared goals, acceptance criteria, and affected stakeholders;
- whether work remains unfinished inside the chosen boundary;
- previous retrospective or follow-up commitments, if any.

A user-supplied range wins. Otherwise derive the smallest range containing the work and record how it was derived. If the first relevant commit is `A`, use `A^..B` to include it. When boundaries are uncertain, show the candidate range and narrow the conclusion instead of silently guessing.

When the checkout has moved beyond the endpoint, read historical content with `git show`, an existing safe worktree, or a disposable archive. Do not switch or rewrite the user's current worktree, and do not mistake later fixes for endpoint behavior.

If material work is unfinished, continue only when the user's goal is an interim retrospective or the incomplete status is already explicit. Never describe unfinished delivery as completed.

## 2. Build the evidence inventory

Follow `references/evidence-inventory.md`. Inventory what exists and what is missing before analysis:

- goals, requirements, architecture decisions, tickets, stories, and acceptance criteria;
- full diff, commits, per-work-item attribution, merge behavior, and generated changes;
- tests, CI results, coverage or quality gates, review records, and deployment evidence;
- current code, schemas, migrations, configuration, documentation, and runbooks;
- runtime observations, incidents, logs, metrics, support feedback, and rollback evidence;
- prior retrospective, its action items, and evidence of follow-through;
- agent or session logs when they exist and are in scope.

Record provenance and availability. Do not treat a missing artifact as proof that an activity did not happen.

Run shared mechanical checks once at the coordinator level: diff statistics, changed paths, test baseline, and other safe project-native measurements. Prefer a successful CI run pinned to the exact endpoint over rerunning an unchanged full suite. Do not make every reviewer rerun the same checks.

## 3. Choose aggregate views

Use the full body of work, not isolated commits. Start with:

1. Goal and acceptance reconciliation
2. Architecture and dependency delta
3. Cross-work integration and boundary behavior
4. Duplication and pattern divergence
5. Complexity and ownership concentration
6. Verification and observability gaps

Add security, privacy, data migration, operability, accessibility, cost, or other domain views only when the target makes them material. Read the view definitions and proof requirements in `references/aggregate-views.md`.

## 4. Run bounded evidence analysis

For a multi-part target, spawn up to three independent analysts, bounded by available slots. Give each one or two aggregate views, the same evidence inventory, the pinned range, applicable repository instructions, and the contract from `references/agent-briefs.md`. Keep the acceptance decision with the parent.

For a small target of at most five commits and 15 changed paths, do not delegate by default. Inspect no more than ten supporting paths, run at most three targeted commands, select the two highest-value aggregate views, and return at most three candidate findings and three confirmed wins in one pass.

Spend at most one small-target command on orientation and statistics. Reserve at least one command and half the path budget for substantive goals, implementation, tests, or CI evidence. Batch related read-only queries when the tool supports it without obscuring their provenance.

Default each analyst to no more than 15 supporting paths, four targeted commands, five candidate findings, three confirmed wins, and one verification pass. Scale deliberately for a larger release. If subagents are unavailable or the target is small, run the views sequentially and disclose the loss of independent perspectives.

Require analysts to return:

- checked scope and mechanical measurements;
- candidate findings with exact sources, consequence, counterevidence, and confidence;
- evidence-backed wins worth repeating;
- falsified hypotheses and material unknowns.

A reviewer failure narrows coverage; it never counts as a clean result. Request one immediate bounded return from a drifting reviewer, then stop it and record the gap.

Apply the same finish discipline to the coordinator. The moment the path, command, or pass budget is spent, stop gathering and write the partial retrospective. If a command stalls, stop it and use the evidence already recorded. Do not add an unplanned cleanup pass, rerun a full suite already evidenced at the exact endpoint, or delay the report to fill every section.

If a read-only command fails before executing because of syntax, quoting, or transport, correct it once immediately. Count the corrected execution—not the empty attempt—against the command budget, and disclose the failed attempt. Do not use this exception to broaden the search.

## 5. Verify behavior when material

When the work changed runtime behavior, exercise the changed end-to-end paths using trusted, safe, project-native checks. Tests passing is evidence, but not a substitute for observing the flow whose delivery is being judged.

Record the environment, command or walkthrough, input, expected behavior, observed behavior, and limitations. Do not mutate production, send external messages, or trigger irreversible side effects without separate authority. If behavior cannot be exercised safely, state that the verdict lacks runtime verification.

## 6. Consolidate observations into findings

The parent reopens every source and deduplicates candidate findings. A surviving finding requires:

- a stable ID and concise observation;
- exact source references and bounded checked scope;
- a violated goal, systemic risk, or repeatable success mechanism;
- a concrete consequence for a named stakeholder;
- counterevidence sought and confidence;
- whether it is local to one instance or systemic across the body of work.

Separate observation from cause. Call a cause **confirmed** only when the evidence establishes the mechanism. Otherwise label it a hypothesis and name the smallest check that could confirm it.

Preserve confirmed wins with the same rigor as problems. Avoid generic praise; state what worked, where the evidence shows it, and what condition made it repeatable. File presence or commit organization can establish consistency, but not improved discoverability, maintainability, speed, or quality unless outcome evidence supports that effect.

## 7. Route each finding on two axes

Give each finding two independent dispositions:

1. **This instance:** remediate now, defer with trigger, accept as-is, or no action.
2. **Future prevention:** change a specification, work slicing, convention, review gate, test, observability, ownership boundary, or nothing.

Turn actions into small, owned commitments with:

- action, owner role, evidence source, and expected outcome;
- verification or acceptance condition;
- priority or trigger, not an invented time estimate;
- dependency and whether a user decision is still required.

Check prior retrospective actions separately. Report **landed** only with evidence, **in progress** only with evidence of partial work, **no evidence found** when the search found none, and **not checked** when the evidence was unavailable.

## 8. Render any delivery verdict carefully

Render a delivery verdict only when the user asks for one or the target has declared acceptance criteria. Use:

- **Accepted:** all declared criteria are demonstrably met, no blocking finding remains, and no scoped work is unfinished.
- **Accepted with open items:** criteria are met and only named, non-blocking items remain.
- **Not accepted:** a criterion is unmet, a blocking finding remains, or scoped work is unfinished.
- **Not assessed:** criteria or evidence are insufficient for a defensible gate.

Do not invent criteria from the diff and call them declared. A human may override a machine assessment; record the override and its author separately from the evidence-based verdict.

## 9. Report and close

Follow `references/retrospective-record.md`. Lead with what the evidence says about the work as a whole, then present wins, findings, follow-through, actions, any verdict, coverage, and open questions.

If the user asks for a team discussion, run it only after findings are sourced. Give participants the evidence packet and require every new claim to cite evidence before it can alter an action or verdict. If one model plays every perspective, disclose that the discussion was not independent.

Never implement the action items as part of this skill. Hand them to the user's normal planning or development workflow.
