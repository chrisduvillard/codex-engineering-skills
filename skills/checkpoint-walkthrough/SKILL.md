---
name: checkpoint-walkthrough
description: Guide a human through reviewing a code change from intent and orientation to concern-grouped code stops, blast-radius risk prompts, observable behavior, and an explicit approve, rework, or discuss decision. Use when the user asks for a checkpoint, human review, review trail, guided walkthrough, “walk me through this change,” “what should I look at,” “show me how to test this,” or help understanding a PR, branch, commit, diff, patch, feature, or agent-produced change before making a call. Keep review evidence clickable and distinguish design questions from verified defects. Do not edit, approve, merge, publish, or otherwise act on the decision unless separately requested.
---

# Checkpoint Walkthrough

Turn a change into a review path a human can follow. Orient first, group by design concern rather than file, surface the highest-blast-radius questions, offer ways to observe behavior, and preserve the user's decision authority.

## Operating contract

- Keep the walkthrough read-only. Inspection does not authorize edits, PR review actions, merges, pushes, deployments, or messages.
- Read repository instructions and preserve dirty work. Pin the target, baseline, and endpoint before describing the change.
- Ground intent in the user's description, specification, issue, ADR, or commit history. Mark inferred intent explicitly.
- Read changed files in context, not only diff hunks. Use the diff to locate change; use surrounding code to explain it.
- Organize the human path by cohesive concern, not filename order.
- Keep **risk prompts** distinct from **verified findings**. A risky location is somewhere worth human attention, not evidence that the code is wrong.
- Do not drown the reviewer in exhaustive detail. Select stops with high explanatory value and name what was omitted.
- Use clickable file-and-line references in the host application's supported format. In Codex desktop, use absolute Markdown file links with a line suffix.

## Load the references

- Read [references/review-trail.md](references/review-trail.md) before generating or presenting review stops.
- Read [references/risk-and-observation.md](references/risk-and-observation.md) before the risk and observation phases.
- Read [references/decision-contract.md](references/decision-contract.md) before prompting for or acting on a review decision.

## 1. Resolve the change

Use this cascade and stop at the first authoritative target:

1. Explicit PR, commit, branch, revision range, patch, spec, or path in the request.
2. A target clearly established in the recent conversation.
3. A single repository item explicitly marked ready for review.
4. Current branch and working-tree change, proposed to the user rather than silently assumed.
5. Ask for the target and its intended behavior.

Resolve PR metadata read-only. Record repository root, branch, endpoint, baseline, dirty state, and applicable instructions. A spec baseline wins; otherwise use the PR base or merge base; for a single commit use its parent. If only the current working tree is in scope, separate staged, unstaged, and untracked changes.

Do not guess across multiple plausible targets. If the diff cannot be resolved, provide the evidence you need and stop.

## 2. Reconstruct intent and orientation

Identify the best intent source:

- user description or acceptance source;
- issue, spec, ADR, or PR body;
- commit message;
- diff pattern only as a last resort, labeled **inferred**.

Compute exact, defensible orientation facts: changed files, top-level areas, additions/deletions, migrations, public interfaces, config or dependency changes, and tests touched. Omit a metric you cannot establish; do not estimate “logic lines” or infer quality from churn.

Present:

```text
[Orientation] → Walkthrough → Risk → Observe → Decision

Intent: <source-backed summary>
Target: <endpoint against baseline>
Surface: <exact compact statistics and affected boundaries>
Verification already recorded: <CI/tests/reviews, or not checked>
```

For a compact request or a small change, continue through all phases in one response. For a large or explicitly interactive walkthrough, present orientation and the review trail together, then pause once for the user to inspect or redirect. Do not drip-feed within a phase.

Treat a change of at most 15 paths and 5,000 diff lines as compact unless the user asks for a deep or interactive pass. Do not delegate. Use at most two batched read-only commands and 12 supporting paths: one command must establish the range and expose the substantive diff or historical files; the other may inspect surrounding context or exact-revision verification. Reuse pinned CI evidence instead of rerunning a full suite. Return no more than four concerns, five risk prompts, and four observations in one response.

When a compact budget is spent, stop inspecting and present the walkthrough immediately. If a command stalls, stop it and use the evidence already gathered. Name paths or concerns that remain uninspected; do not delay a useful trail to make it exhaustive.

## 3. Build the concern-grouped review trail

Follow `references/review-trail.md`. Select two to five concerns for a typical change. A concern is a design intent or behavior that may cross several files. Start at the public or user-facing entry point, move through decisions and boundaries, and finish with storage, configuration, tests, or other supporting mechanisms.

For each concern, explain:

- what this part of the change is trying to achieve;
- why the implementation takes this shape, when the evidence records that choice;
- one to four high-value code stops in comprehension order;
- the question the human should be able to answer after reading them.

Never invent rejected alternatives or rationale. Say “the rationale is not recorded” when code shape alone cannot establish why.

## 4. Surface risk prompts by blast radius

Read the full relevant context around candidate risk locations. Use the categories and selection rules in `references/risk-and-observation.md`. Show at most five prompts, highest blast radius first.

Each prompt contains:

- a clickable location;
- a descriptive tag such as auth, public API, schema, billing, security, concurrency, compatibility, config, infrastructure, privacy, or rollback;
- what could matter if the assumption is wrong;
- the concrete question for the reviewer;
- existing defense or verification already found.

Do not assign a severity score during the guided pass. If no material risk spot exists, say so without manufacturing one.

When the user asks to “dig into” an area, switch that bounded area into correctness mode: trace callers and state, check error and edge paths, inspect tests and contracts, and report evidence-backed findings or say none survived within the checked scope.

## 5. Offer observable verification

Suggest two to five human-observable checks only when they add confidence beyond existing automation. Follow `references/risk-and-observation.md`.

For each option, state:

- **Do:** exact safe action, command, request, or interaction.
- **Expect:** observable result and important negative behavior.
- **Covers:** intent or risk question addressed.
- **Safety:** environment, fixtures, credentials, or side-effect boundary.

Do not run production mutations, send external messages, charge money, deploy, or alter shared state without separate authority. If the change is internal with no useful manual observation, say that automated evidence and code review are the appropriate surfaces.

## 6. Ask for the decision

Follow `references/decision-contract.md`. Summarize:

- the change's intent and concern trail;
- material risk prompts and any verified findings;
- verification observed and residual gaps;
- what remains a design judgment for the user.

Then ask for one of:

- **Approve** — the user accepts the change within the reviewed scope.
- **Rework** — the approach or implementation needs change.
- **Discuss** — a concern remains unresolved.

If the user already made the call, do not ask again. Record it and its scope. An approval in chat is not authority to approve a PR, merge, push, release, or deploy. Ask for explicit confirmation immediately before any such external action, even when the user selected Approve.

## 7. Close without expanding authority

For Rework, turn concerns into specific feedback with locations, expected behavior, and decision questions. Do not edit unless the user asks.

For Discuss, answer the question and return to the decision only when the user is ready.

For Approve, acknowledge the bounded decision and state any residual gap. Do not call the change correct, safe, or fully verified beyond the evidence inspected.
