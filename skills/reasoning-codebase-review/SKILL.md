---
name: reasoning-codebase-review
description: Orchestrate a read-only multi-agent review of an existing codebase using independent reasoning methods such as pre-mortem analysis, first principles, inversion, red-team versus blue-team, Socratic questioning, constraint removal, stakeholder mapping, and analogical reasoning. Use when the user explicitly invokes this skill or asks for multiple agents, parallel reviewers, an assumption challenge, architectural pressure test, or several independent reasoning perspectives on a repository. Produce evidence-backed findings, disagreements, and bounded residual risk. Do not implement fixes unless separately requested.
---

# Reasoning Codebase Review

Pressure-test a codebase through independent reasoning lenses, then challenge the resulting claims before accepting them. Treat explicit invocation as authority to spawn read-only subagents for this review only.

Do not ask agents to reveal private chain-of-thought. Ask for observable claims, questions tested, repository evidence, counterevidence, and conclusions.

## Operating contract

- Keep the review read-only. No reviewer edits product code, tests, configuration, or documentation.
- Preserve dirty work and distinguish current changes from the baseline under review.
- Read repository instructions before assigning work. Pass every applicable instruction to each reviewer.
- Use repository evidence as the source of truth. A method generates hypotheses; it never proves them.
- Execute project code only when provenance is trusted and the repository's normal verification is safe. Otherwise remain source-only and record that limitation.
- Never call a sampled review "clean." Report inspected and uninspected surfaces.
- If the user also asks for fixes, finish and present the review first. Treat implementation as a separate phase with separately bounded authority.

## Load the references

- Read [references/reasoning-methods.md](references/reasoning-methods.md) before selecting or assigning methods.
- Read [references/agent-briefs.md](references/agent-briefs.md) immediately before spawning investigators or challengers.

## 1. Pin the review target

Resolve and record:

- repository root, current revision, branch, and working-tree state;
- target: whole codebase, subsystem, branch, diff, or explicit paths;
- comparison point when the request concerns a change;
- intended behavior from authoritative specifications, tests, schemas, and public contracts;
- repository instructions, normal checks, and any execution constraints.

Default a bare request to the current checkout as a whole-codebase architecture and risk review. If the repository is too large for exhaustive reading, choose a risk-based sample and name the sampling rule before delegation. Ask only when the target or authority cannot be resolved safely.

## 2. Build a shared evidence map

Orient once so independent agents do not each rediscover the entire repository. Inspect:

- runtime and build entry points;
- module and dependency boundaries;
- state, storage, queues, caches, and migrations;
- authentication, authorization, secrets, and other trust boundaries;
- external APIs and irreversible side effects;
- central domain types and invariants;
- test layout, CI checks, and observability;
- recent or concentrated churn when history is relevant.

Turn this into a compact context package: target, baseline, repository rules, system map, high-risk anchors, known unknowns, and commands already run. Include facts and paths, not preliminary findings. Keep a coverage ledger of surfaces assigned, inspected, skipped, or blocked.

Run shared baseline checks once at the coordinator level and pass their exact results to reviewers. Do not pay for multiple full-suite runs unless a reviewer needs a distinct targeted reproduction.

## 3. Select and cluster methods

Honor every method named by the user. For a general run, use these eight:

1. Pre-mortem analysis
2. First principles
3. Inversion
4. Red team versus blue team
5. Socratic questioning
6. Constraint removal
7. Stakeholder mapping
8. Analogical reasoning

Add at most two catalog methods when the evidence map exposes a specific need. Do not inflate the review by running every available method.

Cluster the default investigator wave as follows, adjusting to the codebase:

- **Failure analyst:** pre-mortem, inversion, and constraint removal.
- **Ground-truth analyst:** first principles and Socratic questioning.
- **Systems analyst:** stakeholder mapping and analogical reasoning.

Red-team versus blue-team is the challenge wave, not another independent memo.

## 4. Run the independent investigator wave

Spawn up to three investigators concurrently, bounded by available slots. Give each the same context package, a distinct method cluster, the relevant high-risk anchors, and the investigator contract from `references/agent-briefs.md`.

Give every investigator an explicit evidence budget and finish condition. For a target of a few files, default to no more than 12 supporting paths, three targeted commands, five candidate findings, three falsified hypotheses, and one verification pass. Scale the budget explicitly for a larger subsystem; never leave it open-ended.

Protect independence:

- Do not give investigators the parent's suspicions or another investigator's findings.
- Let each inspect outside its anchor paths when following a concrete dependency or caller.
- Require exact file and line references, checked scope, counterevidence sought, and confidence.
- Require agents to return candidate findings and falsified hypotheses, not fixes or prose tours.
- Cap each brief to one concern cluster; split a very large subsystem rather than broadening a brief.

Wait for the full wave before synthesis. A failed, timed-out, or empty investigator is a coverage gap, not a clean pass. If subagents are unavailable, run the clusters sequentially and disclose that the perspectives were not independent.

If a reviewer exceeds its budget or drifts outside scope, request an immediate bounded return once. If it still does not return, interrupt it and mark its methods and surfaces incomplete; do not stall the whole review.

## 5. Run the red/blue challenge wave

Normalize candidate findings into claims with stable IDs. Merge only candidates that make the same claim and require the same action; preserve corroborating methods and locations.

After the investigator wave is complete, give a fresh red reviewer and a fresh blue reviewer the same candidate packet and evidence map. Run them concurrently when possible:

- **Red:** try to falsify claimed safety, find reachable failure paths, and strengthen the best case that each candidate matters.
- **Blue:** try to falsify each candidate by finding guards, callers, tests, operational controls, or explicit intent that already handles it.

Neither reviewer inherits the parent verdict. Both must cite repository evidence. New red-team findings enter as candidates and must face the same blue challenge; unsupported reassurance from blue is discarded.

Challenge only the normalized candidates and their directly relevant paths. Cap each challenger to one compact entry per claim and one pass. If only one slot is available, run blue and red sequentially without giving either the other's output.

If a challenger fails, continue but mark every affected claim as incompletely challenged. Do not silently simulate the missing side as an independent agent.

## 6. Judge every surviving claim

The parent is the judge. For each candidate:

1. Reopen the cited code and enough surrounding context to establish reachability.
2. Inspect relevant callers, guards, tests, schemas, and specifications.
3. Compare investigator evidence with red and blue counterevidence.
4. Classify the claim as **accepted**, **qualified**, **unresolved**, or **rejected**.
5. Assign risk only from demonstrated impact and reachability; ignore labels supplied by subagents.

An accepted finding requires:

- an exact location or concrete architectural boundary;
- a trigger or violated invariant;
- evidence that the path is reachable or the assumption is load-bearing;
- a concrete consequence for a named stakeholder;
- the counterevidence checked;
- the smallest next check or mitigation direction.

Reject speculative, duplicate, purely stylistic, or already-handled claims. Keep genuine disagreement visible instead of forcing consensus.

## 7. Report the bounded result

Lead with the result, not the ceremony. Use this structure:

1. **Executive verdict** — the two or three system-level conclusions and whether urgent action is warranted.
2. **Accepted findings** — ordered by demonstrated risk; include location, methods, trigger, evidence, stakeholder consequence, counterevidence, and next action.
3. **Disagreement ledger** — qualified or unresolved claims where red and blue evidence materially differ.
4. **Methods and coverage** — which agents and methods ran, paths inspected, commands executed, and any reviewer failures.
5. **Residual risk** — uninspected surfaces, unsafe-to-run checks, missing specifications, and assumptions the repository could not resolve.
6. **Rejected themes** — counts and a compact summary of notable false positives; do not dump noise.

If no findings survive, say that no findings survived within the inspected scope. Never generalize beyond the coverage ledger.
