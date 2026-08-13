---
name: decision-recon
description: Investigate consequential engineering choices and produce an evidence-backed, reversible recommendation. Use when choosing between technologies, vendors, libraries, architectures, migration paths, build-versus-buy options, or competing technical proposals; when asked to research a technical decision, compare candidates, write or validate an ADR, challenge a preferred option, or determine what evidence would settle a disputed choice. Combine repository constraints with current external research, expose uncertainty and lock-in, and identify the conditions under which the recommendation changes. Do not implement the decision unless separately requested.
---

# Decision Recon

Turn a consequential choice into a decision whose evidence, uncertainty, and reversal conditions are visible. Optimize for a recommendation the user can inspect and re-weight, not a verdict they must trust.

## Operating contract

- Keep investigation read-only unless the user separately asks for an artifact file or implementation.
- Treat the current system and the status quo as candidates; never assume change is automatically valuable.
- Separate requirements from claims. Project evidence and the user define requirements. Current external sources establish facts about products, versions, prices, performance, and policy.
- Use prior knowledge only to propose candidates and queries. Do not use it as the sole evidence for a consequential or time-sensitive claim.
- Never hide uncertainty behind a score. Preserve missing, disputed, stale, and incomparable evidence.
- Do not recommend a candidate that fails a hard gate. Do not turn a preference into a hard gate without authority.
- Stop research when the decision is stable under plausible re-weighting or the evidence budget is exhausted; do not collect sources for ceremony.

## Load the references

- Read [references/evidence-contract.md](references/evidence-contract.md) before gathering or judging external evidence.
- Read [references/agent-briefs.md](references/agent-briefs.md) before delegating research or challenge work.
- Read [references/decision-record.md](references/decision-record.md) before synthesizing the final recommendation.

## 1. Frame the decision

Resolve from the request, repository, and user-provided material:

- the decision in one sentence and the named owner or audience;
- the deadline and what happens if no choice is made;
- whether the choice is reversible, costly to reverse, or effectively one-way;
- the current state, baseline behavior, and status-quo cost;
- the decision horizon: pilot, one release, one year, or longer;
- the affected stakeholders and whose costs are easy to overlook.

For repository-bound decisions, record the root, revision, branch, dirty state, applicable instructions, architecture anchors, normal checks, and deployment constraints. Ask only for a missing input that would materially alter the candidate set or hard gates.

## 2. Establish the requirements frame

Agree on the frame before researching candidates:

- **Hard gates:** mandatory compatibility, security, privacy, regulatory, budget ceiling, deployment, data residency, or support constraints.
- **Weighted preferences:** performance, ergonomics, ecosystem, cost, operational burden, maturity, portability, and time to value.
- **Unknown constraints:** plausible requirements that lack authority or evidence.
- **Weights:** use coarse weights such as 1–3 unless the user already owns a more precise model.

Trace each gate and preference to the user, an authoritative project artifact, or repository evidence. Include the status quo and at least one deliberately different option when credible. Do not let candidate marketing define the criteria.

## 3. Build the evidence plan

Choose the smallest topology that can settle the decision:

- **Straightforward:** one focused comparison with a small source budget.
- **Breadth-first:** independent criteria such as security, economics, operations, and developer experience.
- **Depth-first:** one load-bearing uncertainty examined through different methods or source classes.

Create a compact plan containing the candidates, criteria, hard gates, research questions, current-information needs, source budget, freshness requirements, and stop conditions. Browse whenever external facts may have changed. If browsing is unavailable, do not fabricate; state the evidence gap and produce a targeted research plan.

Run shared repository orientation once. Give researchers a requirements packet without the coordinator's preferred answer.

## 4. Gather decision-grade evidence

For a complex decision, spawn up to three independent researchers, bounded by available slots. Split by criterion or method rather than asking every agent to compare everything. For a narrow decision, research sequentially instead.

Require every researcher to follow `references/agent-briefs.md` and return a compact claim ledger. Default each brief to no more than eight sources, ten tool calls, five load-bearing claims, and one follow-up pass. Prefer primary sources: official documentation, release notes, pricing pages, standards, regulator text, original benchmarks, and repository code. Use independent operational evidence to challenge vendor claims.

Record each consequential claim with:

- the exact claim and criterion it affects;
- source URL or repository location;
- publisher, publication date or version, and access date;
- whether the source is primary, independent, or repeating another source;
- status, confidence, freshness, and material counterevidence.

Two domains repeating the same upstream number count as one source. A benchmark without comparable workload, hardware, configuration, version, and metric definitions is context—not proof.

## 5. Screen and compare candidates

Apply hard gates before scoring. Record every eliminated candidate and the evidence-backed reason. Do not smuggle an eliminated favorite back through weighted totals.

For finalists:

1. Compare criterion-level evidence before assigning any score.
2. Separate observed facts from estimates and judgments.
3. Include total cost over the decision horizon: acquisition, integration, infrastructure, operations, training, incidents, migration, and exit.
4. Model lock-in and the cost of leaving, including data export, API seams, proprietary behavior, and organizational learning.
5. Name operational failure modes, ownership burden, and observability or recovery requirements.
6. Score only when a matrix improves transparency. Cite contested cells and mark unknown cells as unknown rather than neutral.

Run a sensitivity check: change the most uncertain weights and estimates within plausible ranges. If the winner changes easily, report a conditional recommendation or propose a pilot instead of false certainty.

## 6. Challenge the leading option

After a provisional leader emerges, give a fresh skeptic only the decision, requirements frame, leading option, and a bounded search budget—not the supporting narrative. Ask for:

- the strongest good-faith case that the leader fails;
- disconfirming current evidence and failed-adoption evidence;
- a load-bearing assumption most likely to break;
- the conditions under which the runner-up wins;
- the cheapest experiment that could overturn the recommendation.

The coordinator reopens every cited source and repository location. Revise the recommendation when contrary evidence changes a hard gate, a decisive criterion, or sensitivity. Do not append objections without judging them.

If no fresh subagent is available or the decision is too narrow to justify one, run one dedicated skeptic pass after setting aside the supporting narrative. Disclose that the challenge was not independent and lower confidence when the missing independence matters.

## 7. Decide and preserve reversibility

The parent owns the verdict. State:

- the recommendation and decision horizon;
- the two or three load-bearing reasons;
- high, medium, or low confidence and the weakest decisive evidence;
- the runner-up and exact conditions under which it wins;
- the strongest argument against the recommendation;
- the cheapest reversibility hedge: pilot boundary, abstraction seam, data export test, rollback, sunset clause, or contract term;
- explicit revisit triggers and the earliest staleness date.

If no candidate clears the hard gates, recommend no decision and identify the smallest change to the frame or candidate set that could unblock it. If evidence cannot distinguish the finalists, recommend the cheapest discriminating experiment.

## 8. Report the result

Follow `references/decision-record.md`. Lead with the decision, then show the requirements, screened candidates, evidence, sensitivity, challenge result, and residual uncertainty. Put citations directly beside externally supported claims.

Write a durable decision record only when the user requests a file or the surrounding workflow already authorizes project documentation. Otherwise deliver the complete record in chat. Never implement the selected option as part of recon.
