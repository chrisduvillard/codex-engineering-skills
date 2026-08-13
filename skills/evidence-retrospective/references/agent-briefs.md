# Agent Briefs

Resolve placeholders, pass absolute paths and pinned revisions, and keep analysts read-only.

## Evidence analyst brief

```text
Analyze the supplied completed body of work through the assigned aggregate view only.

Target and range: <name, left..right, inclusions/exclusions>
Repository rules: <applicable instructions>
Goals/acceptance: <authoritative sources>
Evidence inventory: <available and missing classes>
Assigned view: <one or two views from aggregate-views.md>
Baseline results: <shared commands already run>
Budget: <paths, commands, candidate count, one-pass stop condition>

Read the full relevant range, then follow concrete dependencies or work boundaries only as needed. Do not edit files, infer personal motives, propose broad refactors, or reveal private chain-of-thought.

Return:
1. Checked scope and measurements.
2. Candidate findings (maximum five): ID, observation, exact sources, scope, stakeholder consequence, local/systemic classification, counterevidence, confidence, and smallest next check.
3. Confirmed wins (maximum three): source, observed mechanism worth repeating, demonstrated effect, and boundary of the claim. Do not infer benefit from file presence alone.
4. Falsified hypotheses and unknowns.

An observation without a source is not a finding. A cause without mechanism evidence is a hypothesis.
```

## Evidence-grounded discussion brief

```text
React from the assigned stakeholder or discipline perspective to the supplied sourced findings.

You may challenge a finding, identify a cross-finding pattern, or propose a disposition. Every factual claim must cite the provided evidence or a newly inspected repository source. Do not invent events, motives, or team dynamics. Do not edit files.

Return:
1. Findings supported, challenged, or reframed, with evidence.
2. Systemic mechanism or prevention opportunity.
3. Proposed action or question.
4. Any new observation, clearly marked unverified until the coordinator checks its source.
```

## Failure handling

- A failed or empty analyst narrows the named views; silence is not a clean pass.
- Request one immediate bounded return from a drifting analyst, then stop it.
- When the evidence budget is spent, return immediately; do not add a final sweep.
- Reuse exact-revision CI evidence and shared baseline results instead of rerunning full suites.
- A command that fails before execution may be corrected once; count only the corrected execution and disclose the failed attempt.
- Reopen primary evidence before accepting any agent claim.
- Agreement between agents is not independent corroboration when both rely on the same source.
- The coordinator owns deduplication, causal labels, dispositions, action items, and verdicts.
