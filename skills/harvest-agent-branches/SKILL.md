---
name: harvest-agent-branches
description: Inspect and recover coherent work from stale, divergent, abandoned, or oversized agent branches and worktrees without overwriting newer target changes. Use before a risky wholesale merge.
---

# Harvest Agent Branches

Treat an agent branch as evidence about intended changes, not as a patch that deserves to land whole. Transfer coherent intent onto the current target one reviewable slice at a time.

## Bound the authority

1. Distinguish inspection, local harvesting, publication, deployment, and cleanup.
2. Keep inspection read-only. Treat permission to implement as permission for local branch/worktree changes only; do not infer permission to push, open a PR, deploy, mutate live data, or delete refs.
3. Delete a branch or worktree only when explicitly requested and after establishing durable recovery.
4. Stop for a user decision when it is unclear whether a source feature is still wanted. Do not rescue work merely because it exists.

## Read the target's rules first

Read repository instructions, glossary or context files, ADRs, architecture notes, current plans, and available architecture indexes before classifying changes. Use the repository's vocabulary and preserve its accepted decisions.


## Pin the evidence

Resolve and record before editing:

- source ref and full commit SHA;
- target ref and full commit SHA;
- merge-base SHA;
- every worktree path, branch, HEAD, and dirty state;
- relevant remote or PR recovery ref;
- whether either ref moved during the investigation.

Use read-only Git evidence such as:

```text
git rev-parse --verify 'source-ref^{commit}'
git rev-parse --verify 'target-ref^{commit}'
git merge-base source-sha target-sha
git worktree list --porcelain
git log --left-right --cherry-pick --oneline target-sha...source-sha
git diff --name-status -M -C merge-base..source-sha
git diff --name-status -M -C merge-base..target-sha
```

Inspect status inside every relevant worktree. Never stash, reset, clean, switch, or overwrite a shared checkout. Preserve unrelated dirty and untracked files. Fetch an exact missing ref when needed; avoid pruning unrelated refs.

## Build a path matrix

Inventory the whole branch before choosing a transfer method. Match detail to the request:

- For an initial comparison, cleanup assessment, or request for the first slice, cluster every changed path by concern and inspect the proposed slice path-by-path.
- Before implementing a slice, classify every path in that slice and its dependency closure individually.
- Before declaring the whole branch harvested or deleting it, classify every changed path individually.

Create a compact ledger:

| Path or concern | Source change | Target change since base | Contract role | Decision | Slice |
| --- | --- | --- | --- | --- | --- |

Do not let uninspected paths disappear from the inventory. Include deletions, renames, migrations, generated files, tests, configuration, and documentation.

- Treat a target-untouched path as eligible for whole-file or commit transfer only after confirming the source change is coherent and adjacent contracts did not change.
- For a path changed on both sides, inspect the base, source, current target, and `git log merge-base..target -- path`. Port intent additively onto the target.
- Treat a source-side deletion as a possible regression. Prove zero callers or identify the current replacement before carrying it over.
- Trace both sides of a rename; do not let rename detection hide a delete-and-recreate semantic change.
- Regenerate derived files from their current owner inputs instead of copying stale generated output.

Read the actual diffs, especially deletions. File counts and diff statistics orient the investigation but cannot establish safety.

## Decompose by behavior

Define each slice as one observable capability or root-cause fix. Include its complete dependency closure:

- implementation and public entrypoint;
- callers, adapters, imports, and compatibility shims;
- tests and hand-built fixtures;
- schema migrations and model changes;
- configuration, examples, generated outputs, and operator documentation;
- terminology or architectural decisions that require glossary or ADR updates.

Mark every source change as `harvest`, `superseded`, `skip intentionally`, or `needs user decision`. Do not leave unexplained residue.

When asked for the first slice, choose the smallest independently valuable or enabling behavior with a complete dependency closure and low target overlap. "First" means safest useful landing order, not earliest source commit or smallest raw diff.

Before splitting or moving modules, search test patch targets and imports. Preserve intentional monkeypatch seams at their old public location or replace hidden module-global reads with explicit injection. Do not assume a green test exercised a moved patch target.

For persisted data or wire-format readers, include at least one fixture written by hand in the previous format. Never let every compatibility fixture pass through the new writer under test.

## Choose the least risky transfer

Prefer, in order:

1. Reimplement the source intent against current target abstractions when the target evolved materially.
2. Apply a focused patch or use a no-commit cherry-pick for a coherent commit, then review every resulting line.
3. Transfer a whole file only when target history proves it remained untouched and the file has no stale coupled assumptions.
4. Merge the whole branch only when it is current, cohesive, independently reviewed, and the user explicitly wants that strategy.

Use an isolated worktree pinned to the target SHA unless the current workspace is already a clean, dedicated worktree for this task. Use a fresh `codex/` branch by default. Never develop directly in a shared primary checkout.

Keep slices small enough to review and revert independently. Land prerequisites before dependents. Preserve current target behavior unless the slice explicitly changes it.

## Prove the harvest

Establish a target baseline before modification, run focused checks while iterating, then run the repository's authoritative gate for a substantive slice.

Make every verification result state what it examined: exact SHA, platform, resolved root, files or tests collected, artifacts or rows sampled, and relevant configuration. Treat zero-input, wrong-root, self-matching process, stale-SHA, or new-writer-only checks as no evidence.

Select additional proof by risk:

- Run compatibility tests against previous persisted shapes for reader changes.
- Run database-specific checks when SQLite cannot represent locks, JSON operators, defaults, constraints, or cascades.
- Run platform-specific checks on the real platform for filesystem identity, process, lock, launcher, or path behavior.
- Run contract, golden, architecture-boundary, and end-to-end tests for cross-cutting owners.
- Inspect integrated-target CI after landing when remote publication is authorized; a green source PR does not prove the combined target.


## Preserve recovery before cleanup

Before deleting any source ref:

1. Record its full tip SHA and original ref name.
2. Confirm which slices landed and which were intentionally skipped.
3. Establish a durable recovery route such as a retained branch/tag, an existing PR ref with a documented hosting-retention assumption, or an explicitly authorized bundle. Do not call an unreachable local object durable recovery. If recovery must be indefinite, do not rely on a PR ref alone unless its retention is guaranteed; prefer an authorized tag or archived bundle.
4. Verify the recovery route resolves to the recorded tip.
5. Delete only the exact authorized ref; never use broad patterns.
6. Report what was removed, where the recovery evidence lives, and how long it is expected to remain available.

Do not remove the isolated worktree until it is clean and every useful artifact is committed, copied to an approved location, or intentionally discarded.

## Hand off clearly

Lead with what was actually harvested. Include:

- source, target, and merge-base SHAs;
- landed slices and their commits or changed paths;
- superseded and intentionally skipped material with reasons;
- baseline and verification results with scope counts;
- unresolved conflicts, compatibility risks, and decisions still needed;
- exact recovery refs for any retained or deleted branch;
- confirmation that production, deployment, and unrelated worktrees were untouched unless separately authorized.

Do not describe a partial port as a completed branch harvest while unclassified source changes remain.
