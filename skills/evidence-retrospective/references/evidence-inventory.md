# Evidence Inventory

Create the inventory before interpreting the work.

## Boundary record

Record:

- target name and type;
- repository root, revision, branch, and dirty-state note;
- left and right revisions and why they bound the work;
- included and excluded work items;
- unfinished work inside the boundary;
- declared goals and acceptance sources.

For commit ranges, remember that `A..B` excludes `A`. Use `A^..B` when `A` is the first included commit. For branches or merge commits, state whether the comparison is against the merge base, first parent, or another explicit baseline. Do not sum merge diffs with their constituent commits; that double-counts churn.

Inspect the state at the pinned endpoint. If the current checkout contains later commits or dirty changes, use read-only historical commands or a disposable snapshot rather than changing the user's checkout. Record current-state evidence separately when later evolution is itself relevant.

## Inventory table

| Evidence class | Source or range | Available? | Authority/use | Limitation |
|---|---|---:|---|---|
| Goals and acceptance | Spec, issue, story, ADR | | What was intended | |
| Change set | Diff range and commits | | What changed | |
| Work attribution | Tickets, commit references | | Work boundaries | |
| Verification | Tests, CI, review, deployment | | What was checked | |
| Runtime | Logs, metrics, incidents, feedback | | What users/operators observed | |
| Current state | Code, schema, config, docs | | What exists now | |
| Process record | Session/agent logs | | Why a path changed | |
| Prior follow-through | Previous retro and actions | | Whether commitments landed | |

## Evidence states

Use exact language:

- **Available and checked:** source existed and was inspected.
- **Available, not checked:** source existed but fell outside budget or scope.
- **Missing:** expected artifact was not found; this does not prove the activity never happened.
- **Unavailable:** access, retention, or tool limitations prevented inspection.
- **Unsafe to exercise:** the check could cause side effects beyond current authority.

Carry every material limitation into the final coverage section.

## Mechanical pre-pass

Prefer project-native, deterministic tools to collect:

- changed paths and line churn;
- commits, authorship metadata when relevant, merges, and work-item references;
- dependency or schema changes;
- test results and failing checks;
- current file sizes for high-churn candidates;
- generated or binary changes that text statistics cannot measure.

Mechanical output is a lead. Open the affected files, tests, and specifications before converting it into a finding.
