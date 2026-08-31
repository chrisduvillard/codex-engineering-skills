---
name: context-pruner
description: Audit or improve repository AI instructions such as AGENTS.md, CLAUDE.md, Copilot, or Cursor rules. Verify what loads, preserve protected behavior, reduce duplication, and prefer mechanical enforcement.
---

# Context Pruner

Treat always-loaded context as scarce infrastructure. Keep non-obvious rules that prevent expensive mistakes; remove copies of facts an agent can retrieve more accurately at the point of use.

## Operating contract

- Read every applicable instruction file before proposing changes. Existing human-authored rules are the baseline, not disposable raw material.
- Default an audit or assessment request to read-only. An explicit create, adopt, refresh, consolidate, update, or prune request authorizes the corresponding scoped file edits after the ledger rules below are satisfied.
- Preserve dirty work and never overwrite unrelated content, comments, or instructions outside the proposed scope.
- Verify every path, command, version, loading claim, and caveat against repository evidence. Mark human policy and runtime testimony by source rather than pretending the code proves them.
- Keep discoverable facts out unless discovery is expensive, late, unreliable, or costly when missed.
- Prefer a hook, linter, formatter, schema, script, or CI check when it can enforce the rule mechanically.
- Do not delete a human-authored instruction merely because it is long, derivable, quiet lately, or stylistically weak.
- Separate team/repository rules from personal or cross-repository preferences; recommend the latter for global configuration.
- Never commit or publish instruction changes unless separately requested.

## Load the references

- Read [references/admission-rules.md](references/admission-rules.md) before judging any candidate instruction.
- Read [references/change-ledger.md](references/change-ledger.md) before proposing, applying, or reporting edits.
- Read [references/instruction-shape.md](references/instruction-shape.md) before composing root, nested, or linked instruction content.

## 1. Resolve mode, target, and budget

Choose one mode:

- **Audit:** verify loading, evidence, contradictions, duplication, staleness, and budget; do not edit.
- **Create:** build instructions where no meaningful repository-level instructions exist.
- **Adopt:** consolidate meaningful existing instructions into a coherent managed structure.
- **Refresh:** re-verify previously curated context and update only what changed.
- **Prune:** reduce context debt while preserving behavioral coverage through the ledger.
- **Record:** capture one observed costly or recurring agent mistake as a pitfall or mechanical check.

Resolve the repository root, revision, branch, dirty state, instruction harnesses in use, and exact files in scope. Inventory root and nested `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, Cursor or other configured rule files, imports, and linked guidance. Do not assume naming alone means a file loads.

Measure the total always-loaded context for the target. Honor an explicit project or harness budget. Without one, use these editing goals:

- Create: aim for no more than 80 nonblank lines and 1,200 words across root always-loaded instructions.
- Refresh or prune: do not grow the always-loaded total unless new verified risk outweighs the cost.
- Existing over-budget file: preserve instructions lacking deletion grounds and report the unresolved budget rather than gutting the file.

For a bounded Audit of at most three active instruction files, do not delegate. Use at most five targeted read-only commands and 15 supporting paths. Spend the first command on the instruction inventory and size, reserve at least two commands for loading or enforcement evidence, and use at most one command for history or duplication. Return the loading graph, size, findings, and complete ledger in one pass.

When the audit budget is spent, stop gathering and report immediately. If a command stalls, stop it and use the evidence already gathered. Mark an instruction Unverified rather than delaying the ledger to prove it. A partial evidence state with a complete accounting is better than an unfinished audit.

## 2. Verify the loading graph

Establish which files each active harness actually loads, in what order, at what working directory, and whether nested files are discovered at session start or dynamically. Use current official harness documentation or an observable local loading test when available.

Draw a compact loading graph:

```text
Harness → root instruction → imported/shared rules → path-scoped or nested rules
```

Classify files as always loaded, loaded by observable trigger, loaded only from a particular working directory, manually referenced, shadowed, duplicated, contradictory, or not loaded. A move into a file no active harness can discover is a deletion and needs deletion grounds.

Create a nested instruction file only when all are true:

- rules are exclusive to that subtree and substantial;
- the split materially reduces root context;
- loading is verified for every relevant harness and working-directory pattern;
- the parent points to it when discovery is not guaranteed;
- the user requested or authorized structural edits.

Otherwise retain path-qualified rules in the root file.

## 3. Open the change ledger

Follow `references/change-ledger.md`. Create one entry per independently meaningful existing instruction and one per proposed addition. Start existing entries at retain or rewrite, never delete.

For each entry record:

- current text and source file;
- behavior protected and cost if absent;
- evidence and verification state;
- proposed disposition: retain, rewrite, relocate, automate, or delete;
- destination or enforcement mechanism;
- deletion ground when applicable;
- effect on always-loaded context;
- approval requirement.

Group only truly equivalent entries. Do not hide an existing instruction inside a section-level summary.

## 4. Discover repository evidence

Inspect the smallest evidence set that can settle ledger entries:

- instruction files and their imports;
- manifests, lockfiles, tool-version files, build scripts, CI, linters, hooks, generators, and test configuration;
- architecture and operational documents that explain non-obvious boundaries;
- targeted code paths and schemas for cross-component invariants;
- targeted history since the last verified revision for deleted, renamed, or changed referents;
- recorded mistakes, review findings, support notes, or session logs for observed pitfalls.

Do not turn a repository overview into instructions. Use manifests and code to remove redundant prose and retain only caveats the files cannot express: the obvious command fails, a service must run first, CI performs an extra gate, a generated area must not be edited, or a default convention is deliberately inverted.

When the repository contradicts a human rule, show both sources and resolve the conflict. Do not silently prefer one.

## 5. Interview only the evidence gaps

Ask the user only about governance, security, frozen areas, runtime behavior invisible from source, domain language, off-repository standards, and observed agent mistakes that scanning cannot establish.

Ask recall questions, not a long checklist. Batch at most five tightly related questions; stop when a batch yields no new load-bearing context. Never ask the user to confirm a path, version, command, or convention already verifiable from the repository.

Treat maintainer testimony as evidence with its source and date. A user policy can be authoritative without code support; a technical claim still needs verification.

## 6. Judge every instruction

Apply `references/admission-rules.md`. For a proposed addition, ask:

1. Would its absence plausibly change agent behavior?
2. Would an agent discover the truth before acting, at acceptable cost?
3. Is the statement stable enough for always-loaded context?
4. Can it be enforced or retrieved mechanically instead?
5. Is this the narrowest correct scope and trigger?

Retain policies, non-default conventions, expensive-to-discover caveats, observed pitfalls, cross-component invariants, required versions, and high-value entry pointers. Exclude directory tours, stack inventories, obvious commands, duplicated config, generic best practices, aspirations, changelog prose, and facts likely to rot.

Prefer prohibitions that name the permitted alternative: “Never edit `generated/`; run `make codegen`.” Avoid advice that cannot change an action.

## 7. Propose safely, then edit if authorized

Before editing, show in commentary:

- the complete proposed instruction content or diff;
- before/after always-loaded line and word counts;
- the settled ledger, with every relocate, automate, and delete itemized;
- contradictions repaired and loading behavior verified;
- unresolved evidence gaps.

When the user explicitly asked to create, adopt, refresh, consolidate, update, or prune, continue with supported rewrites, relocations, automation references, and deletions under grounds 1–3 in `references/change-ledger.md`. Pause for line-item approval for any deletion that has only ground 4, any unverified loading relocation, or any choice that materially changes policy.

When editing a managed block, splice only inside its markers. Content outside changes only through an explicit ledger entry. When consolidating multiple live files, leave a verified import or minimal pointer when a harness still expects the old location; never maintain two loaded copies of the same rule.

Do not add a reference to a check until that check exists. An instruction proposed for automation remains until enforcement lands and passes.

## 8. Validate the result

After edits:

- parse or load every instruction file through the available harness mechanism;
- path-check all local references and commands;
- verify imports and nested discovery from relevant working directories;
- search for contradictory or duplicate live rules;
- confirm unrelated content is byte-for-byte unchanged where practical;
- recount always-loaded lines and words;
- inspect the final diff and working-tree state.

If loading cannot be tested, say so and keep rules in a location already proven to load. Never claim a nested or imported structure works from convention alone.

## 9. Report the context delta

Lead with what changed or, for an audit, what should change. Report:

- files and harnesses inspected;
- before/after context size and loading graph;
- retained protections and new verified additions;
- every rewrite, relocation, automation candidate, and deletion with reason;
- contradictions fixed;
- items blocked on policy, evidence, or approval;
- validation performed and residual loading risk;
- provenance revision and date for the next refresh.

For Record mode, state the observed mistake, correction, evidence, recurrence/cost basis, and whether prose or enforcement is the better home. One cheap occurrence becomes a note; a recurring or costly failure can earn an instruction now.
