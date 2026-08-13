# Agent Briefs

Resolve every placeholder, pass absolute repository paths, and keep work read-only.

## Researcher brief

```text
Investigate the assigned decision criterion independently. You are not choosing the overall winner.

Decision: <one sentence>
Candidates: <bounded list, including status quo when applicable>
Assigned criterion/questions: <single concern cluster>
Hard gates and definitions: <authoritative frame>
Repository evidence: <allowed paths and revision>
Freshness and source rules: <from evidence-contract.md>
Budget: <sources, tool calls, one-pass stop condition>

Use current primary sources first and independent sources to challenge consequential claims. Do not rely on training data alone. Do not infer requirements from candidate marketing. Do not edit files or reveal private chain-of-thought.

Return:
1. Checked scope: queries, pages, repository paths, and versions inspected.
2. Claim ledger: maximum five load-bearing claims in the evidence-contract shape.
3. Candidate comparison for this criterion only: gate outcome or relative evidence, with unknowns preserved.
4. Contrary evidence and falsified hypotheses.
5. The smallest next check if the evidence remains decision-relevant and unresolved.
```

## Skeptic brief

```text
Challenge the provisional leader independently and in good faith.

Decision: <one sentence>
Requirements frame: <hard gates and decisive preferences>
Provisional leader: <candidate>
Runner-up: <candidate>
Budget: <sources and tool calls>

You do not receive the supporting narrative. Search for current disconfirming evidence, failed-adoption mechanisms, violated gates, hidden lifecycle or exit costs, and assumptions most likely to break. Cite direct sources and distinguish evidence from inference. Do not edit files or reveal private chain-of-thought.

Return:
1. Strongest evidence-backed case against the leader.
2. Exact condition under which the runner-up wins.
3. Claims contradicted, weakened, or still untested.
4. Cheapest experiment that could overturn the provisional decision.
5. Checked scope and residual unknowns.
```

## Failure handling

- A timed-out or source-free researcher contributes no evidence; mark that criterion incomplete.
- Request one immediate bounded return from a drifting agent, then stop it.
- Reopen every load-bearing source before accepting a claim.
- Do not treat agreement between agents as corroboration when they cite the same publisher.
- The coordinator—not a researcher, score, or skeptic—owns gates, weights, confidence, and the final recommendation.
