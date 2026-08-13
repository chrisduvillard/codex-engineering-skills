<div align="center">

# Codex Engineering Skills

### Eight rigorous workflows for the parts of software engineering where “looks right” is not enough.

[![Skills](https://img.shields.io/badge/skills-8-6D5EF7?style=for-the-badge)](#choose-your-skill)
[![Built for Codex](https://img.shields.io/badge/built%20for-Codex-101828?style=for-the-badge)](#installation)
[![Validate](https://img.shields.io/github/actions/workflow/status/chrisduvillard/codex-engineering-skills/validate.yml?branch=main&style=for-the-badge&label=validation)](https://github.com/chrisduvillard/codex-engineering-skills/actions/workflows/validate.yml)

<p>
  Plan uncertain work · preserve system knowledge · recover divergent branches<br>
  trace data · attack correctness · pressure-test assumptions · research decisions · learn from delivery
</p>

</div>

---

Most agent instructions focus on producing code. This collection focuses on producing **justified engineering decisions**: grounded in repository evidence, constrained by explicit authority, and closed with verification.

Each skill is deliberately opinionated. Together they cover eight recurring failure zones in long-lived codebases.

## Choose your skill

| When you need to… | Use | What it changes |
|---|---|---|
| Turn a fuzzy request into work another agent can execute safely | [`$deep-plan`](skills/deep-plan) | Writes a risk-ordered plan, not implementation code |
| Build durable understanding of a large or long-lived codebase | [`$steward-brownfield`](skills/steward-brownfield) | Maintains an evidence-backed project world model |
| Recover useful work from a stale, divergent, or oversized branch | [`$harvest-agent-branches`](skills/harvest-agent-branches) | Ports coherent slices without overwriting newer work |
| Explain where a value came from—or where its meaning broke | [`$trace-data-provenance`](skills/trace-data-provenance) | Traces one specimen across every semantic boundary |
| Try to falsify a change that appears correct | [`$adversarial-review`](skills/adversarial-review) | Runs bounded attacks and reports reproducible findings |
| Pressure-test a system from independent reasoning perspectives | [`$reasoning-codebase-review`](skills/reasoning-codebase-review) | Coordinates investigators, red/blue challenge, and evidence-based judgment |
| Choose between consequential engineering options | [`$decision-recon`](skills/decision-recon) | Separates requirements from current evidence and preserves reversal conditions |
| Learn from a completed body of engineering work | [`$evidence-retrospective`](skills/evidence-retrospective) | Reconstructs goals, diffs, verification, systemic patterns, and follow-through |

## The collection

### 01 · Deep Plan

Turns a rough engineering request into a plan that can survive fresh sessions and shallow review. It investigates the real repository first, sizes the work, exposes ambiguity, orders phases by risk, and produces self-contained sub-prompts with exact verification and stop conditions.

> **Use it when:** the request spans several files, hides product decisions, or could easily become an unreviewable diff.

```text
Use $deep-plan to investigate this repository and turn the request into a risk-ordered execution plan.
```

### 02 · Brownfield Steward

Treats project knowledge as durable infrastructure. It initializes or resumes a versioned world model, refreshes only affected knowledge, coordinates bounded specialist work, and checkpoints evidence so the next agent does not have to rediscover the system from scratch.

> **Use it when:** continuity across sessions matters more than a one-off answer.

```text
Use $steward-brownfield to resume this project safely and recommend the next highest-value step.
```

### 03 · Harvest Agent Branches

Recovers intent from abandoned or divergent agent work without assuming the whole branch deserves to land. It pins source and target evidence, builds a path matrix, decomposes work by behavior, chooses the least risky transfer method, and preserves recovery before cleanup.

> **Use it when:** an old branch contains valuable work, but `merge` is too blunt an instrument.

```text
Use $harvest-agent-branches to salvage coherent work from this branch onto current main.
```

### 04 · Trace Data Provenance

Follows a concrete datum from authoritative input to delivered output. It checks identity, time semantics, units, missingness, fallbacks, lineage, and historical behavior—then identifies the earliest boundary where meaning becomes unproven or incorrect.

> **Use it when:** a metric is wrong, stale, missing, duplicated, inconsistent, or simply impossible to explain.

```text
Use $trace-data-provenance to trace this value end to end and identify the first unsafe boundary.
```

### 05 · Adversarial Review

Attempts to falsify behavioral and security correctness rather than merely confirming the happy path. It derives an attack ledger from actual contracts and code, selects adaptive techniques, minimizes reproductions, and reports bounded residual risk instead of vague reassurance.

> **Use it when:** a parser, workflow, API, or bug fix needs more than an ordinary code review.

```text
Use $adversarial-review to attack this change with adaptive edge-case tests.
```

### 06 · Reasoning Codebase Review

Orchestrates independent reviewers through pre-mortem, first-principles, inversion, Socratic, constraint, stakeholder, and analogical lenses. It then subjects normalized claims to separate red and blue challengers before the coordinator accepts, qualifies, or rejects them.

> **Use it when:** an architecture or codebase needs more than one mental model—and the disagreements matter as much as the findings.

```text
Use $reasoning-codebase-review to pressure-test this codebase through independent reasoning methods.
```

### 07 · Decision Recon

Turns technology, vendor, architecture, migration, and build-versus-buy choices into evidence-backed decisions. It frames hard gates before researching candidates, tracks claim freshness, exposes lock-in and lifecycle cost, tests sensitivity, and challenges the provisional leader before recommending it.

> **Use it when:** the expensive part is choosing—and being able to explain when that choice should change.

```text
Use $decision-recon to compare these options and produce a reversible, evidence-backed recommendation.
```

### 08 · Evidence Retrospective

Reconstructs a release, milestone, sprint, migration, or multi-session feature from the evidence it left behind. It analyzes the whole change for architecture drift, integration seams, duplicated patterns, verification gaps, and follow-through—while keeping missing evidence distinct from missing work.

> **Use it when:** the lessons live across several tickets or commits, and memory is too easy to rewrite after the fact.

```text
Use $evidence-retrospective to review this milestone and propose sourced, owned follow-ups.
```

## Installation

Clone the collection:

```bash
git clone https://github.com/chrisduvillard/codex-engineering-skills.git
cd codex-engineering-skills
```

Then copy every skill into your personal Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

Or copy only the skill you want:

```bash
cp -R skills/adversarial-review ~/.codex/skills/
```

Restart Codex after installation, then invoke a skill explicitly with its `$name`.

## A shared operating philosophy

The eight skills are different tools, but they enforce the same engineering instincts:

- **Evidence before confidence.** Read the repository, contracts, history, and runtime artifacts.
- **Risk before tidiness.** Detect breakage and secure boundaries before restructuring code.
- **Narrow authority.** Inspection does not imply permission to edit, publish, deploy, or delete.
- **Concrete specimens.** Trace one value, replay one failure, or minimize one counterexample.
- **Mechanical closure.** Finish with exact checks, preserved recovery, and explicit residual risk.

## Repository layout

```text
skills/
├── deep-plan/
├── steward-brownfield/
│   ├── assets/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── harvest-agent-branches/
├── trace-data-provenance/
├── adversarial-review/
│   └── references/
├── reasoning-codebase-review/
│   └── references/
├── decision-recon/
│   └── references/
└── evidence-retrospective/
    └── references/
```

Every skill is rooted at a `SKILL.md`. Supporting metadata lives in `agents/`; larger skills may also carry progressive references, scripts, tests, schemas, and templates.

## Validation

The repository checks skill names, parsed frontmatter, local support links, agent metadata, Python syntax, validator regressions, and the Brownfield Steward test suite on pull requests and pushes to `main`.

Run the same checks locally:

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s skills/steward-brownfield/tests -p 'test_*.py'
```

## Inspiration

Reasoning Codebase Review was informed by BMAD-METHOD's [reasoning catalog](https://github.com/bmad-code-org/BMAD-METHOD/blob/c4ec1837b8b7ffbf09a7aebb4891c38f93899f58/src/core-skills/bmad-advanced-elicitation/assets/methods.csv), [independent-agent discussions](https://github.com/bmad-code-org/BMAD-METHOD/blob/c4ec1837b8b7ffbf09a7aebb4891c38f93899f58/src/core-skills/bmad-party-mode/references/mode-subagent.md), and [review orchestration](https://github.com/bmad-code-org/BMAD-METHOD/blob/c4ec1837b8b7ffbf09a7aebb4891c38f93899f58/src/core-skills/bmad-review/SKILL.md). Decision Recon adapts the research firewall, claim verification, selection frame, and staleness discipline from [Deep Recon](https://github.com/bmad-code-org/BMAD-METHOD/blob/c4ec1837b8b7ffbf09a7aebb4891c38f93899f58/src/core-skills/bmad-deep-recon/SKILL.md). Evidence Retrospective generalizes BMAD's [repository-grounded retrospective](https://github.com/bmad-code-org/BMAD-METHOD/blob/c4ec1837b8b7ffbf09a7aebb4891c38f93899f58/src/bmm-skills/ship/bmad-retrospective/SKILL.md) beyond its epic workflow. All three are redesigned around this collection's evidence, authority, and bounded-risk contracts.

## Contributing

Changes should make a skill safer, clearer, or more falsifiable—not merely longer. A strong proposal includes the failure mode it addresses, the evidence behind it, the smallest instruction change that fixes it, and a way to verify the new behavior.

---

<div align="center">
  <sub>Built for engineers who want agents to leave behind evidence, not mystery.</sub>
</div>
