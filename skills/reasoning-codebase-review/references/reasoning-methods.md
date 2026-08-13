# Reasoning Method Catalog

Use methods as hypothesis generators and evidence protocols. Their output is a set of testable claims, not a substitute for reading code.

## Core methods

### Pre-mortem analysis

Assume the reviewed system has already failed in production. Write several concrete failure headlines, then work backward through triggering conditions, propagation paths, missing signals, and absent recovery mechanisms. Prefer failures that cross components or ownership boundaries.

Evidence to seek: retry and timeout behavior, recovery procedures, partial writes, migration paths, observability, rollback mechanics, and tests of degraded dependencies.

### First principles

Separate observed facts, explicit constraints, conventions, and assumptions. Reduce the system to its necessary invariants and rebuild the claimed design from those truths. Challenge components that exist only because "that is how this stack usually works."

Evidence to seek: domain types, schemas, protocol contracts, entry points, authoritative requirements, and minimal end-to-end paths.

### Inversion

Ask what design and operating choices would guarantee failure, data loss, security bypass, or unmaintainability. Search the repository for those conditions, then translate confirmed conditions into preventions. Do not report the inverted scenario unless a reachable path exists.

Evidence to seek: single points of failure, unchecked inputs, shared mutable state, permissive defaults, unbounded work, silent errors, and irreversible side effects.

### Red team versus blue team

Give independent reviewers the same claim packet. Red constructs the strongest evidence-backed attack; blue searches for existing defenses and false assumptions. A judge reopens the evidence and decides. Do not let one agent voice both sides when independent agents are available.

Evidence to seek: exploit or failure path, guard placement, defense depth, caller behavior, tests that would fail, monitoring, and documented intent.

### Socratic questioning

Turn consequential claims into questions: What exactly is claimed? What observation supports it? How could it be false? What would change the conclusion? Who relies on it? Apply the questions to specifications and reviewer hypotheses as aggressively as to code comments.

Evidence to seek: words such as "always," "never," "safe," "atomic," and "validated"; comments without enforcement; tests with weak assertions; undocumented assumptions between layers.

### Constraint removal

Classify constraints as physical, contractual, policy, compatibility, budget, or assumed. Remove one assumed constraint at a time and ask whether a simpler or safer architecture becomes possible. Add constraints back only with repository evidence. Report architectural options separately from defects.

Evidence to seek: legacy adapters, duplicated abstractions, feature flags, frozen interfaces, compatibility shims, configuration defaults, and stale documentation.

### Stakeholder mapping

Inspect the same behavior from each affected perspective. Start with end user, operator, maintainer, security/privacy owner, adjacent service, and business or regulatory owner; add domain-specific stakeholders only when evidence supports them. Name whose failure cost is currently externalized.

Evidence to seek: error and recovery UX, operational controls, on-call signals, maintenance seams, privacy boundaries, support workflows, and downstream consumers.

### Analogical reasoning

Find a structurally similar system or failure pattern, map corresponding elements explicitly, import one useful lesson, and state where the analogy breaks. Reject surface-level analogies that do not preserve constraints or causal structure.

Evidence to seek: queues versus ledgers, caches versus replicas, compilers versus pipelines, state machines versus workflows, and other parallels with comparable invariants.

## Optional methods

Add no more than two unless the user requests them.

### Assumption audit

List load-bearing assumptions, rate evidence strength and consequence if false, then inspect the weakest high-impact assumptions first.

### Second-order effects

Trace consequences one and two hops beyond the immediate behavior: retry storms, incentive shifts, operational load, data retention, coupling, and future migration cost.

### Cascading failure simulation

Select one realistic dependency or component failure and trace propagation through timeouts, retries, queues, state transitions, and human operations until the system stabilizes or collapses.

### Map-versus-territory check

Compare diagrams, specifications, generated clients, schemas, and comments with executable wiring and runtime artifacts. Treat divergence as a candidate until current behavior and intended authority are established.

## Selection guide

| Codebase signal | Favor |
|---|---|
| Launch, migration, or operational risk | Pre-mortem, inversion, cascading failure |
| Architecture accreted over years | First principles, constraint removal, assumption audit |
| Strong safety or correctness claims | Socratic questioning, red/blue, map-versus-territory |
| Many teams or user roles | Stakeholder mapping, second-order effects |
| Novel domain or unclear design options | Analogical reasoning, first principles |
| Distributed state and retries | Cascading failure, inversion, pre-mortem |

## Common method failures

- Treating imaginative scenarios as findings without a reachable path.
- Producing eight differently worded versions of the same issue.
- Letting personas replace domain evidence.
- Importing an analogy without naming where it breaks.
- Calling policy or compatibility constraints "assumptions" without authority.
- Asking "why" repeatedly without converting answers into verifiable claims.
- Forcing consensus when the evidence is genuinely incomplete.
