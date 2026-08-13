# Instruction Shape

Use only sections that contain admitted rules. Omit empty headings.

## Recommended order

1. **Orientation** — at most three sentences: what the repository is and where deeper planning or architecture truth lives. Omit when the repository is self-evident and no pointer changes behavior.
2. **Policy** — human or enforced governance, protected paths, approvals, privacy, security.
3. **Where work starts** — a few entry points, ownership boundaries, and trigger-specific pointers.
4. **Running and verifying** — only correct commands, required versions, and caveats not already obvious from executable config.
5. **Non-default conventions** — deliberate divergence from ecosystem defaults.
6. **Cross-component invariants** — rules that must remain true across distant code.
7. **Observed pitfalls** — recurring or costly mistakes with their corrective action.

## Writing style

- Use terse imperative bullets.
- Put scope and trigger in the same line.
- State a prohibition with the permitted alternative.
- Name the source path when it helps verification.
- Avoid explanatory prose except a short justification clause.
- Do not paste code or long command catalogs.
- Avoid emphasis noise, duplicated cautions, and generic introductions.

Example:

```markdown
## Running and verifying

- Run `uv run pytest tests/unit/test_x.py` while iterating; bare `pytest` uses the wrong environment.
- Start `docker compose up -d postgres` before integration tests; connection errors otherwise hide the real failure.

## Cross-component invariants

- Validate every import row before writing any row; direct writes inside the parse loop break atomicity.
```

## Managed blocks

When adopting or refreshing part of a larger human-owned file, use explicit start and end markers plus a provenance comment containing date and verified revision. Splice only the managed region. Do not claim the whole file is managed when handwritten content remains outside.

## Nested files

Use nested instructions only for substantial subtree-exclusive rules whose loading is verified. Otherwise use root path-qualified bullets. List every nested child from the parent when the harness does not guarantee discovery.

## Linked references

A pointer names an observable trigger and the exact file:

```markdown
- Editing migrations? Read `docs/db-rules.md` first for transaction and rollback constraints.
```

Do not write “consult the relevant docs” or create an index that requires the agent to decide when it is confused.

## Provenance

Include a compact note for curated content:

```markdown
<!-- Agent context verified 2026-08-13 against abc1234. -->
```

On refresh, compare path deletions, renames, config, and policy changes since that revision. Update provenance only after every retained claim is reverified.
