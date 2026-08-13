# Agent Briefs

Use these as structures, not scripts to copy blindly. Resolve every placeholder and pass absolute paths. Keep reviewers read-only.

## Context package

Every reviewer receives:

- **Objective:** the single concern cluster to investigate.
- **Repository and revision:** absolute root, revision, branch, dirty-state note.
- **Scope:** target paths or subsystem and allowed dependency traversal.
- **Baseline:** comparison point when reviewing a change.
- **Repository rules:** applicable instructions and safe verification commands.
- **System map:** concise entry points, boundaries, invariants, and high-risk anchors.
- **Methods:** assigned method names and their cards from `reasoning-methods.md`.
- **Evidence budget:** maximum supporting paths, commands, candidates, and passes.
- **Evidence rule:** cite exact files and lines; distinguish observed facts from inference.
- **Stop rule:** if the premise is false or evidence is unavailable, report the gap and stop instead of improvising.

Do not include the coordinator's suspected defects or another reviewer's output in an investigator brief.

## Investigator brief

```text
Review the supplied codebase read-only using only the assigned reasoning-method cluster.

Inspect the named anchors first. Follow callers, dependencies, tests, schemas, and specifications only as needed to establish or falsify a concrete claim. Do not edit files. Do not propose broad refactors. Do not reveal private chain-of-thought.

Honor the supplied evidence budget. Use the coordinator's baseline results; do not rerun the full suite unless a distinct targeted reproduction requires it. Complete one inspection and verification pass, then return.

Return:
1. Checked scope: paths, symbols, searches, and commands actually inspected.
2. Candidate findings (maximum five unless the brief says otherwise): stable ID, title, method, exact location, trigger or violated invariant, repository evidence, named stakeholder consequence, counterevidence sought, confidence, and smallest next check.
3. Falsified hypotheses (maximum three): plausible concerns you checked and rejected, with the evidence that rejected them.
4. Unknowns (maximum three): missing evidence or unsafe-to-run checks that materially limit confidence.

Speculation without a reachable path is not a finding. An empty candidate list is valid when accompanied by checked scope.
```

## Red challenger brief

```text
Act as the red challenger for the supplied candidate claims. Work read-only and independently from the investigators' conclusions.

For each claim, try to demonstrate a reachable failure, contradiction, exploit, or stakeholder harm from repository evidence. Strengthen only claims you can ground. Identify new failure paths when they are directly reachable from the supplied scope, but do not expand into a general review. Inspect only cited paths and direct callers or defenses. Complete one pass. Do not edit files and do not reveal private chain-of-thought.

Return one entry per claim: claim ID, verdict (supported / weakened / contradicted / untested), exact evidence, best trigger, concrete consequence, and remaining unknown. Return any new candidate separately in the investigator finding shape.
```

## Blue challenger brief

```text
Act as the blue challenger for the supplied candidate claims. Your job is to falsify false positives, not to defend the project rhetorically.

For each claim, search for guards, validation, callers, tests, schemas, operational controls, or explicit intent that already handles it. Read the alleged defense before citing it and explain whether it actually observes the claimed failure. Inspect only cited paths and direct callers or defenses. Complete one pass. Do not edit files and do not reveal private chain-of-thought.

Return one entry per claim: claim ID, verdict (handled / partially handled / unhandled / untested), exact counterevidence, defense limitations, and the smallest check that would settle uncertainty.
```

## Coordinator normalization

Normalize investigator output before the challenge wave:

```text
ID: RCR-001
Title: concise behavioral claim
Methods: method names and corroborating investigators
Location: file:line or named architectural boundary
Trigger/invariant: the condition being tested
Evidence: observed repository facts
Stakeholder consequence: who is affected and how
Counterevidence already checked: guards/tests/specs inspected
Confidence: high / medium / low, with basis
```

Merge only the same claim with the same required action. Similar symptoms with different causes remain separate. Preserve corroboration because independent overlap is useful evidence.

## Coverage and failure handling

- A timed-out or failed agent contributes no verdict; mark its methods and paths incomplete.
- When an agent exceeds its evidence budget, request an immediate bounded return once; then interrupt and mark the gap.
- An empty result without checked scope is a failed review.
- An empty result with precise checked scope is a valid negative result within that scope.
- If an agent writes files, stop using its findings until the coordinator inspects the working tree and separates those writes from the review.
- The coordinator, not a challenger, owns final risk and acceptance.
