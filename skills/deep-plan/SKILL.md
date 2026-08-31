---
name: deep-plan
description: Investigate a repository and turn a broad or uncertain engineering request into a risk-ordered, executable plan with self-contained prompts and exact verification. Not for a small, fully specified edit.
---

# Deep Plan

Turn uncertain engineering work into a plan a fresh agent can execute without silently expanding
scope. Investigate first, order by risk, and preserve one coordinator-owned progress record.

## Operating contract

- Do not implement product code while planning.
- Source files remain unchanged. Planning may write only the namespaced artifacts below.
- Read repository instructions, architecture, tests, schemas, CI, and neighboring conventions first.
- Preserve dirty work. Never stash, reset, clean, stage, or absorb unrelated changes.
- Separate repository facts, user decisions, assumptions, inferences, and open questions.
- Do not manufacture phases or cleanup work.

## Execution profiles

Choose by consequence and uncertainty, not line count alone.

- **Fast:** one low-risk concern with an obvious contract. Return one prompt and verification inline.
- **Standard:** several coupled files or one material boundary. Create two to four phases.
- **Deep:** authentication, money, migrations, destructive operations, concurrency, public contracts,
  infrastructure, or interacting systems. Add explicit decisions, characterization, independent
  verification, and rollback gates.

Escalate a small high-risk change. Do not inflate a large mechanical change.

## Investigate and frame

Establish repository root, revision, branch, dirty state, applicable instructions, intended observable
outcome, acceptance sources, entry points, affected components and contracts, existing partial
solutions, project-native checks, and material ambiguity. Discover repository facts yourself. Ask only
for a user decision that can materially change the plan.

## Build the risk-ordered plan

Order work as applicable:

1. baseline and reproduce current behavior;
2. settle product, compatibility, data, security, and operational decisions;
3. add characterization or contract tests around the changing boundary;
4. implement the smallest coherent root-cause slice;
5. verify focused behavior and adjacent regressions;
6. independently challenge material-risk work;
7. update documentation, migration, rollout, and rollback surfaces;
8. perform optional cleanup last.

Each phase states its goal, ordering reason, preconditions, dependencies, allowed and forbidden paths,
self-contained prompts, exact checks and expected results, recovery, user decisions, and stopping
conditions.

## Prompt contract

Every implementation prompt includes one observable concern, exact path authority, requirements,
revision, examples to imitate, `[read-only]` or `[writes code]`, edge and failure behavior, focused and
broader checks, evidence to capture, rollback, zero-caller proof before deletion, and a stop rule when
the premise or authority fails. Split by independent reviewability, verification, and reversibility,
not a universal line-count limit.

## Namespaced artifacts

Standard and Deep plans create:

```text
.agents/runs/deep-plan/<run-id>/
├── PLAN.md
├── progress.jsonl
├── evidence.json
└── prompts/
```

Use a collision-resistant UTC run ID. Never overwrite a previous run or root-level `PLAN.md`. Only the
coordinator updates `PLAN.md` and appends canonical `progress.jsonl` events. Parallel workers return
structured events or write agent-specific files; they never append concurrently to one shared file.

A progress event records timestamp, phase, status, bounded summary, exact checks, contradictions, and
the next safe action.

## Close

End with the recommended first phase, credible failure modes, weakest evidence, excluded adjacent
work, user-owned decisions, completion and abort criteria, and the exact artifact path. The plan does
not authorize implementation, publication, deployment, destructive actions, or external messages.
