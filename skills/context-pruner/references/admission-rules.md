# Admission Rules

The question is not whether an agent *can* derive a fact. Ask whether it will find the right fact before acting, at acceptable cost and reliability.

## Admit to always-loaded context

- Human or enforced policy the code cannot express: protected branches, frozen paths, privacy, security, compliance, approval gates.
- Non-obvious command caveats: the obvious invocation is wrong, a service or wrapper is required, local tests omit a CI gate, or the full suite is unsuitable for iteration.
- Conventions that deliberately differ from ecosystem defaults.
- Observed recurring or high-cost pitfalls with a source.
- Runtime behavior invisible from source once confirmed by an authoritative operator or evidence.
- Cross-component invariants whose violation in one location breaks another: ownership, transaction order, data flow, compatibility, rollback, generated boundaries.
- Required tool and runtime versions from declaring project files.
- A few entry points or trigger-specific pointers that prevent expensive search.

Prefer a short imperative rule that includes the permitted path. A bare fact earns space only when it explains an action.

## Exclude from always-loaded context

- Repository overview, full directory tree, stack inventory, dependency list.
- Commands whose obvious invocation is already correct and declared in a manifest, Makefile, task runner, or CI.
- Style preferences enforced by a formatter or linter.
- Generic software advice or agent behavior already supplied globally.
- Pasted code, changelog narration, implementation history, or current sprint state.
- Aspirational architecture not true today.
- Fast-changing facts that can be retrieved from an authoritative file at point of use.
- Interesting details with no plausible behavior change.
- Repeated rule text already loaded from another source.

## Triggered context

Move detail behind a pointer only when the trigger is observable:

- editing a named path or file type;
- running a named workflow;
- touching migrations, billing, generated code, security, or another explicit boundary.

Avoid subjective triggers such as “when the task is complex” or “when needed.” A pointer no agent knows when to follow is a deletion disguised as organization.

## Stability and provenance

Record the verified revision and date for curated context. Recheck after significant architecture, tooling, workflow, or policy changes. Diff deletions and renames since the verified revision against every path-qualified rule.

A policy or pitfall is not stale because nothing failed lately; effective rules erase their own failure evidence. Retire it only when the guarded condition is gone, enforcement replaces it, it contradicts stronger live authority, or the user explicitly retires it.

## Enforcement preference

Route mechanically detectable behavior to checks:

- formatting → formatter;
- import or dependency direction → linter or architecture test;
- generated files → generator check or ownership rule;
- schema and metadata shape → validator;
- required test gate → CI;
- dangerous command → wrapper or hook when feasible.

Keep the prose until enforcement exists and passes. Then delete under the mechanically-enforced ground.
