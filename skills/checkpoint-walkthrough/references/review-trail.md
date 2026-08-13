# Review Trail

Build a path for comprehension, not a tour of every changed file.

## Select concerns

A concern is a cohesive design intent such as input validation, authorization, state transition, public contract, migration, error recovery, or configuration. It may span layers and files. One file may contribute to several concerns.

Prefer two to five concerns. Use one when the change is genuinely simple. More than seven usually means the change is too broad for one comfortable checkpoint; present the top concerns and name the omitted set.

## Select stops

Choose one to four locations per concern. Prefer:

1. User-facing or public entry point
2. Decision or policy point
3. Boundary crossing or state transition
4. Failure or recovery path
5. Verification that demonstrates the contract

Avoid mechanical imports, generated code, repetitive fixtures, and boilerplate unless they carry the decision. Read the changed file around every stop and follow a caller, callee, schema, or test only when needed to explain the concern.

For a compact historical commit, one batched `git show` of the commit metadata, patch, and selected endpoint files can establish both orientation and substantive context. Do not check out the historical revision or spend a separate command per file.

## Order for comprehension

Start with what activates the behavior. Continue through the core decision and downstream effect. End with defenses and tests. Never require the reviewer to understand a symbol that has not yet been introduced.

## Present each concern

```text
### <Concern: design intent>

<What this achieves. Why this shape, when recorded.>

- <clickable path:line> — <role in this concern, at most 15 words>
- <clickable path:line> — <role in this concern, at most 15 words>

Reviewer question: <the design judgment these stops make answerable>
```

Use “rationale not recorded” rather than inventing why an author chose an approach. If a stop is unchanged context, label it as context.

## Coverage note

End the trail with:

- changed paths intentionally omitted and why;
- generated, binary, vendored, or unreadable content;
- whether stops came from an author-provided review order or were generated;
- any baseline uncertainty.

If the compact budget ends before full context is read, present the best supported stops and mark the remaining paths uninspected. A partial clickable trail is better than no return.
