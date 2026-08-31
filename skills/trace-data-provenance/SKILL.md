---
name: trace-data-provenance
description: Trace one datum, field, metric, score, or signal across source, ingestion, normalization, storage, derivation, and delivery. Diagnose the earliest boundary where identity, time, units, missingness, or lineage breaks.
---

# Trace Data Provenance

Establish whether one concrete output can be reconstructed from authoritative inputs without an unproven semantic jump. Treat code as evidence of possible behavior and runtime artifacts as evidence of actual behavior.

## Route the request

- For a trace or audit, remain read-only and report the first unproven or violated boundary.
- For a diagnosis, trace a failing specimen and identify the earliest boundary that corrupts or loses its meaning.
- For a comparison, trace both specimens independently until their paths or boundary contracts diverge.
- For a requested repair, complete the trace first, then implement the smallest correction at the boundary that owns the broken semantic.

Do not infer authorization to deploy, run production backfills, mutate external systems, or alter live data from permission to inspect or edit source code.

## Pin a specimen and its intended meaning

1. Read repository instructions, glossaries, ADRs, schemas, and relevant domain documentation.
2. Define the narrowest reproducible specimen:
   - entity or instrument identity;
   - field or metric name;
   - observed value and expected value, if known;
   - observation, event, session, or as-of time;
   - environment, run, report, request, or artifact identifier;
   - code revision, deployed version, and configuration version when historical behavior matters.
3. State the intended semantic separately from the observed implementation. Treat approved requirements and source-provider contracts as intent; treat user claims about current behavior as assertions until verified.
4. If no specimen is supplied, select the smallest representative real case available and label the choice. Ask only when choosing a specimen could materially change the conclusion.

Never combine a historical output with current code or configuration without identifying that limitation.

## Build the trace

Start sink-first when explaining a visible output; start source-first when auditing an ingestion contract. Search actual field names, identifiers, models, schemas, migrations, queries, configs, job definitions, tests, serializers, reports, and operational scripts. Include caches, queues, retries, recovery paths, manual overrides, and backfills when they can change the value.

Bound reconnaissance before searching broadly:

- Trace one pinned specimen, one primary source path, and one requested sink first.
- Stop expanding consumers once the requested output is explained or the earliest material boundary becomes `CONTRADICTED` or `UNPROVEN`.
- Follow side paths only when they can alter the specimen through fallback, override, retry, cache, recovery, or backfill behavior.
- Sample representative tests and call sites; do not inventory every file that mentions the field.
- Delegate only disjoint boundary ranges with explicit endpoints, then synthesize them into one trace. Do not recursively widen the audit.

Map every relevant boundary:

`provider/raw input → fetch → parse/validate → canonicalize → persist → select/join → derive/score → serialize/report/alert`

For each boundary, record:

| Contract dimension | Prove |
| --- | --- |
| Identity | Provider key, canonical key, aliases, contract or entity mapping, and join keys remain unambiguous. |
| Time | Event, observation, publication, retrieval, settlement, session, and as-of timestamps are distinguished; timezone, DST, calendar, and cutoff rules are explicit. |
| Units | Currency, scale, sign, price basis, quantity type, precision, and rounding are preserved or deliberately converted. |
| Value transform | Parsing, filters, formulas, windows, aggregation, deduplication, ranking, and scoring match the intended semantic. |
| Missingness | Null, zero, absent, stale, provisional, invalid, and incomplete states remain distinct. |
| Selection | Source priority, fallback, quarantine, override, cache, and conflict-resolution behavior is visible and deterministic. |
| Persistence | Schema type, keys, constraints, upsert behavior, migrations, and version fields preserve the contract. |
| Provenance | Source ID or URL, raw-artifact reference or digest, retrieval/run ID, transform/config version, and quality state survive far enough to explain the output. |
| Historical path | Live, retry, recovery, replay, and backfill paths produce equivalent semantics or document intentional differences. |

Record each edge as `input → operation → output`, with an evidence locator and a status of `PROVEN`, `CONTRADICTED`, or `UNPROVEN`.

## Apply an evidence standard

Prefer evidence in this order:

1. Raw or persisted artifacts and observed runtime queries for the pinned specimen.
2. Deterministic reproductions, focused tests, or fixture replays.
3. Executed code, configuration, schema, and migration paths tied to the relevant version.
4. Current authoritative documentation or provider contracts.
5. Names, comments, and conventions only as leads, never proof.

Require both sides of a boundary. An identical downstream number does not prove lineage, and a code path does not prove it ran. Preserve contradictions instead of choosing the most convenient source. Sanitize secrets and sensitive raw records in notes and outputs.

## Challenge the trace

Test the failure modes most likely to create plausible but wrong output:

- alias collisions, contract rolls, entity remaps, and join fan-out or drop;
- timezone shifts, session-date confusion, DST, holidays, late publication, and look-ahead leakage;
- unit, currency, sign, scale, precision, or rounding drift;
- null-to-zero coercion, stale-value reuse, partial coverage, and silent fallback;
- retry duplication, non-idempotent upserts, cache staleness, and race-dependent selection;
- live-versus-backfill drift, schema evolution, configuration drift, and incomplete migrations;
- aggregation-window, denominator, ranking-universe, and versioned-formula changes;
- provenance fields being discarded before reporting or alerting.

Use negative evidence carefully: a search with no result is not proof until the search scope and generated or dynamic paths are accounted for.

## Repair only a proven defect

When the user asks for a fix:

1. Capture a failing specimen or characterization test before changing behavior.
2. Fix the earliest boundary that owns the incorrect semantic. Avoid compensating downstream unless the owning boundary cannot safely change.
3. Preserve raw evidence and provenance. Never make a bad value look correct only at presentation time.
4. Keep code repair, schema migration, historical data correction, and production rollout as separate scopes. Do not imply that old records are repaired merely because new code is correct.
5. Verify the focused boundary, the end-to-end specimen, adjacent regression cases, and the relevant replay or backfill path. Run broader checks in proportion to risk.
6. Re-run the trace against the post-change revision and report any boundary that remains unproven.

## Report the result

Lead with one status:

- `PROVEN END TO END`
- `PROVEN WITH LIMITATIONS`
- `CONTRADICTED`
- `BLOCKED BY MISSING EVIDENCE`

Then provide:

1. The pinned specimen and intended semantic.
2. A compact trace table: stage, input, operation, output, identity/time/unit, evidence, and status.
3. The earliest violated or unproven boundary and its downstream impact.
4. Confirmed findings, inferences, and unknowns as separate categories.
5. For repairs, changed files, before/after behavior, verification performed, historical-data implications, rollback, and residual risk.
6. The single highest-value next evidence or action if the trace is incomplete.

Keep the report inline unless the user requests a persistent artifact or the investigation is large enough to require one. Do not declare provenance complete when any material edge is `UNPROVEN`.
