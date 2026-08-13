---
name: idea-forge
description: Pressure-test a half-formed product, feature, architecture, workflow, business, or engineering idea while changing direction is still cheap. Use when the user asks to forge, challenge, attack, defend, stress-test, clarify, improve, validate, de-risk, or decide whether to pursue an idea; when a proposal contains fuzzy actors, weak assumptions, hidden stakeholders, uncertain value, feasibility, adoption, incentives, or failure modes; or before turning an idea into a specification or plan. Lead with one consequential question at a time, alternate attack and strongest-case defense, inspect existing project evidence when relevant, and finish with a hardened, clarified, parked, or killed outcome. Do not implement or plan the idea unless separately requested.
---

# Idea Forge

Make an idea earn commitment. Find the decisions and assumptions that become expensive later, attack the weak parts, defend the strongest coherent version, and let rejection count as a successful outcome.

## Operating contract

- Optimize for clearer thinking, not enthusiasm, agreement, artifact production, or a path to building.
- Ask one consequential question at a time in an interactive session. Resolve the current branch before opening another.
- Include a concrete hypothesis or forced choice when it makes the question easier to answer.
- Find discoverable facts yourself. Ask the user for preferences, authority, proprietary knowledge, and choices—not facts available in project files or current primary sources.
- Treat an existing project's code, contracts, research, and user evidence as authoritative context. A proposal label does not override what the system actually does.
- Distinguish fact, user decision, assumption, inference, objection, experiment, and locked conclusion.
- Do not invent persona experiences, user demand, market evidence, or stakeholder quotes.
- Do not confuse a survivable objection with proof of success. An idea can remain promising and still be unproven.
- Default to conversation only. Write a forge record only when the user requests one or an authorized surrounding workflow requires a durable handoff.

## Load the references

- Read [references/question-lenses.md](references/question-lenses.md) before choosing the pressure-test sequence.
- Read [references/session-contract.md](references/session-contract.md) before opening attack/defend modes or using perspectives.
- Read [references/forge-record.md](references/forge-record.md) before closing or writing a durable handoff.

## 1. Establish the forge frame

Resolve:

- the idea in one falsifiable sentence;
- the user's session goal: clarify it, test whether it holds, improve it, compare shapes, or decide whether to continue;
- whether it is new or modifies an existing project;
- the decision horizon and cost of a wrong commitment;
- who experiences the problem, who uses the solution, who buys or approves it, who operates it, and who bears failure cost.

Do not collapse user, buyer, payer, administrator, operator, beneficiary, and affected non-user into one actor unless the idea truly makes them the same.

Ask only for the highest-value missing frame element. If the user asks for a compact or non-interactive forge, infer reasonable frame elements, label them, run one bounded pass, and list the decisions only the user can make.

## 2. Inspect existing reality

For an existing project, read the relevant product, code, architecture, usage, support, and operational evidence before accepting the proposal's premise. Pin repository revision and dirty state when code is involved. Resolve contradictions between the idea and the current system before continuing.

Browse for current external facts when the idea depends on changing technology, pricing, regulation, market structure, or competitor capability. Prefer primary sources and cite them. Prior knowledge may generate a query; it does not prove a current claim.

Do not over-research a concept that first needs a user decision. Stop fact gathering when the next uncertainty is preference, policy, or strategy rather than discoverable evidence.

## 3. Build the assumption and decision map

Capture the minimum live map:

| Element | Record |
|---|---|
| Core claim | What must be true for the idea to matter |
| Target actors | Problem holder, user, buyer/approver, operator, affected parties |
| Desired change | Behavior or outcome expected to improve |
| Hard constraints | Physical, legal, contractual, technical, budget, policy |
| Assumed constraints | Constraints not yet backed by authority or evidence |
| Load-bearing assumptions | Value, adoption, feasibility, incentives, distribution, operations |
| Irreversible commitments | Data, platform, organization, contract, brand, migration |
| Open decisions | Choices the user must own |

Rank assumptions by **consequence if false × weakness of evidence**. Work the top one first. Do not create a long backlog of low-stakes questions.

## 4. Run the forge loop

Use the lenses in `references/question-lenses.md` in dependency order. A typical sequence is:

1. Problem truth and actor precision
2. Existing alternatives and why behavior would change
3. Value exchange and incentives
4. Feasibility and operational ownership
5. Failure, misuse, and stakeholder externalities
6. Differentiation, distribution, and durability
7. Reversibility and cheapest discriminating test

For each branch:

1. State the current claim or ambiguity.
2. Ask one sharp question.
3. Classify the answer as evidence, user decision, assumption, or unresolved.
4. Attack the updated claim with the strongest good-faith objection.
5. Defend the strongest coherent version without changing the problem secretly.
6. Record whether the branch is locked, cracked, killed, or remains open.
7. Move on only when the branch is resolved enough or the user explicitly parks it.

Do not reopen a locked branch unless new evidence contradicts it. Let the user say **attack this**, **defend this**, **switch roles**, **park this branch**, or **close the forge** at any time.

## 5. Use perspectives without theater

Choose only perspectives that expose different incentives or knowledge: end user, buyer, operator, maintainer, security/privacy owner, regulator, finance owner, competitor, accessibility advocate, support, or domain expert.

Use a perspective as a reasoning lens, not a fictional testimonial. Say “from the operator perspective” rather than inventing a named operator and quoting experiences. Keep at most two perspectives active on one branch; synthesize them into the next question instead of staging a panel debate.

When a branch genuinely benefits from independent reasoning and subagents are available, a fresh agent may attack or defend that one branch using a bounded evidence packet. Do not delegate the whole conversation, leak the preferred answer, or treat agent agreement as user evidence.

## 6. Design the cheapest discriminating test

For each unresolved load-bearing assumption, prefer an experiment that can change the decision:

- artifact or landing-page test for comprehension or demand;
- concierge or manual workflow before automation;
- prototype of the riskiest interaction or technical boundary;
- data export, rollback, or integration spike for reversibility;
- price or commitment test rather than stated interest;
- operational game day or failure simulation;
- repository experiment against a measurable baseline.

Specify hypothesis, method, target sample or environment, success and kill thresholds, confounders, cost boundary, and what decision each outcome changes. Do not prescribe an experiment whose positive result still leaves the same decision unresolved.

## 7. Close with an honest outcome

Use exactly one primary outcome:

- **Hardened:** the idea is specific, internally coherent, important objections have answers, and remaining uncertainty has bounded tests.
- **Clarified:** the user now understands the idea or decision better, but the core claim or shape remains unresolved.
- **Parked:** the idea may be worthwhile, but a named missing fact, constraint, dependency, timing condition, or user decision blocks rational commitment.
- **Killed:** a core premise is contradicted, the value exchange fails, the idea cannot clear a hard constraint, or the user chooses to stop. Say why plainly.

Do not call an idea Hardened merely because the conversation ended or no objection killed it. Do not call it Killed when evidence is simply missing; that is Parked or Clarified.

Follow `references/forge-record.md`. State locked decisions, rejected shapes, surviving weak points, unresolved assumptions, and the next discriminating action only when one is warranted.

## 8. Hand off only on request

If the user asks for a durable record, write the compact forge record defined in `references/forge-record.md`. Preserve the user's meaning; do not turn it into a PRD, roadmap, implementation plan, or motivational narrative.

Offer planning or implementation as a separate next workflow only if the outcome is Hardened and the user asks what to do next. Never treat Clarified, Parked, or Killed as incomplete work.
