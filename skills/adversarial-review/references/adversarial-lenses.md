# Adversarial lenses

Use this reference to derive ledger rows from the actual scoped behavior. Do not mechanically apply every item. For each relevant lens, identify the code evidence, partitions, oracle, interactions, and safe bound. Mark an item not applicable only when the data flow or contract excludes it.

## Contents

- [Derive partitions mechanically](#derive-partitions-mechanically)
- [Values and representations](#values-and-representations)
- [Relationships and transformations](#relationships-and-transformations)
- [State, sequence, and time](#state-sequence-and-time)
- [External failures and effects](#external-failures-and-effects)
- [Identity, trust, and abuse](#identity-trust-and-abuse)
- [Concurrency and liveness](#concurrency-and-liveness)
- [Resource and complexity attacks](#resource-and-complexity-attacks)
- [Configuration and environment](#configuration-and-environment)

## Derive partitions mechanically

- For `x < k`, attack the largest value below `k`, `k`, and the smallest value above `k`, plus representation extrema that can reach the comparison.
- For compound predicates, vary each term so it independently changes the decision; then attack coupled terms and short-circuit side effects.
- For loops and collections, attack counts `0`, `1`, `2`, the ordinary case, the declared limit, and just beyond it. Include duplicates and permutations when order or uniqueness may matter.
- For enums and tagged unions, attack every declared case, unknown/forward-compatible values at deserialization boundaries, and invalid tag/payload pairings.
- For conversions, attack the source and destination extrema, lossy precision, rounding ties, sign changes, unit mismatches, and round trips.
- For state machines, enumerate legal transitions and generate skipped, repeated, reversed, replayed, interrupted, and concurrent transitions.
- For three or more interacting dimensions, begin with pairwise covering combinations when feasible. Increase strength where the implementation couples more variables, consequence is high, or a lower-strength attack surprises.
- For every accepted input class, derive its closest rejected neighbors; for every rejected class, attempt an equivalent alternate representation.

## Values and representations

### Numbers

- Zero, negative zero, one, minus one, sign changes, exact thresholds, nearest representable neighbors
- Minimum/maximum values, overflow/underflow, narrowing/widening, signed/unsigned conversion
- NaN, infinities, subnormals, decimal/binary precision, accumulated error, cancellation, rounding modes
- Division/modulo by zero or near-zero, non-integral ratios, unit/currency/scale mismatches

### Text, bytes, and paths

- Empty, whitespace-only, leading/trailing whitespace, separators, embedded NUL/control characters
- Valid/invalid/truncated encodings, Unicode normalization, combining characters, case folding, locale, bidirectional text
- Very long tokens, repeated prefixes, delimiter nesting, escape sequences, alternate canonical forms
- Absolute/relative paths, `.`/`..`, repeated separators, symlink or case sensitivity where reachable, reserved names

### Structures and collections

- Empty/singleton/many; missing/extra/null fields; duplicate keys or identifiers
- Sorted, reverse-sorted, unstable, duplicated, or adversarial order
- Deep, wide, cyclic, aliased, shared, or self-referential structures where the type permits
- Mutable inputs reused after calls, partial iterators/streams, lazy evaluation, and one-shot values
- Schema/version skew, unknown fields, legacy representation, and partial migration state

## Relationships and transformations

- Equality versus identity; ownership, aliasing, and copy/view behavior
- Round-trip/inverse, idempotence, commutativity, associativity, conservation, monotonicity, and bounds
- Partition/recombine and batch/single equivalence
- Canonicalization before validation versus after validation
- Equivalent inputs through alternate API routes, encodings, locales, backends, optimization levels, or thread counts
- Reference model or old/new implementation disagreements, excluding undefined behavior unless handling it is the contract

## State, sequence, and time

- Every legal state and transition; invalid transition attempts; stale handles and reused objects
- Duplicate delivery, retries, replay, reordering, omission, cancellation, timeout, and late completion
- Partial success, rollback failure, crash/restart, recovery, idempotency, and exactly/at-least/at-most-once assumptions
- Midnight/month/year boundaries, leap day, daylight-saving gaps/folds, timezone conversion, clock skew/jumps
- Exact expiry, just before/after expiry, stale caches, out-of-order timestamps, and mixed clock sources

## External failures and effects

- Refusal, timeout, slow response, malformed response, empty response, partial read/write, disconnect, and retry exhaustion
- Quota/rate limit, conflict, duplicate acknowledgment, eventual consistency, stale read, and failover
- Disk full, permission denied, missing file, corrupt file, interrupted subprocess, non-zero exit, and unexpected output
- Transaction commit/rollback failure and failures between each pair of externally visible effects
- Logging, metrics, and audit paths that fail or leak sensitive values

## Identity, trust, and abuse

- Missing/expired/revoked credentials; wrong role, owner, tenant, audience, issuer, or scope
- Horizontal and vertical privilege changes; object IDs swapped after authorization; confused-deputy paths
- Validation at one entry point but not its siblings; client-side-only controls; internal endpoints exposed externally
- Injection into interpreters, queries, templates, shells, headers, logs, redirects, paths, and serialization formats
- Canonicalization/encoding disagreement across trust boundaries
- Sensitive data in errors, logs, caches, URLs, telemetry, or timing; insecure defaults/fallbacks
- Forged, duplicated, reordered, or suppressed audit events

For security-focused reviews, map assets, actors, entry points, data flows, and trust boundaries first. Use [OWASP threat modeling/STRIDE](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html), version-pinned [OWASP ASVS](https://github.com/OWASP/ASVS/tree/v5.0.0), [MITRE CWE](https://cwe.mitre.org/data/definitions/699.html), [MITRE CAPEC](https://capec.mitre.org/data/definitions/1000.html), or the applicable [SEI CERT standard](https://cmu-sei.github.io/secure-coding-standards/) only to expand code-grounded hypotheses. Record the release/date, language edition, and exact rule or entry ID used, and link the exact rule when cited; a catalogue hit is not a finding.

## Concurrency and liveness

- Read/write, write/write, check/use, initialization, teardown, and publication interleavings
- Lost update, double execution, stale snapshot, lock inversion, missed wakeup, starvation, deadlock, and livelock
- Cancellation during each await/blocking boundary; timeout racing with success; retry racing with the original request
- Bounded queue, worker, and backpressure behavior; shutdown with work in flight
- Shared/global state reset between generated iterations and independent tests

Use controlled schedules and deterministic replay when possible. Pair schedule exploration with a race detector and bounded real stress because each sees different failures. Record preemption, step, thread, and time bounds.

## Resource and complexity attacks

- Size, count, nesting, fan-out, cardinality, and compression/expansion ratio
- Worst-shaped inputs for sorting, hashing, regex, parsing, allocation, recursion, retries, and graph traversal
- CPU, memory, file descriptor, socket, queue, disk, and log growth under explicit safe limits
- Cleanup after failure, cancellation, timeout, or repeated calls

Never perform an unbounded denial-of-service experiment. Prefer complexity inspection, small scaling curves, timeouts, fakes, and hard local quotas.

## Configuration and environment

- Missing, empty, invalid, duplicate, conflicting, and defaulted configuration
- Feature-flag combinations and rolling-version skew
- Development/test/production mode differences; fail-open versus fail-closed defaults
- Locale, timezone, filesystem semantics, architecture/word size, endianness, and dependency versions when behavior depends on them
- Cold start, warm cache, first/last run, parallel test order, and process restart
