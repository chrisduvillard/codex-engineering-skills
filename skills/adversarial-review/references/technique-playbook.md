# Dynamic technique playbook

Read only the sections selected by the attack ledger. Prefer the project's existing, maintained tools and version-matched documentation. Record exact versions; the named tools below are examples, not installation recommendations. A technique is useful only when its oracle can detect the defect of interest and its harness reaches the intended surface.

## Contents

- [Boundary and combinatorial tests](#boundary-and-combinatorial-tests)
- [Property-based and stateful testing](#property-based-and-stateful-testing)
- [Coverage-guided or structured fuzzing](#coverage-guided-or-structured-fuzzing)
- [Metamorphic testing](#metamorphic-testing)
- [Differential testing](#differential-testing)
- [Deterministic fault injection](#deterministic-fault-injection)
- [Concurrency and schedule exploration](#concurrency-and-schedule-exploration)
- [Runtime sanitizers](#runtime-sanitizers)
- [Selective mutation testing](#selective-mutation-testing)
- [Threat-driven manual and dynamic review](#threat-driven-manual-and-dynamic-review)
- [Research basis and limits](#research-basis-and-limits)

## Boundary and combinatorial tests

1. Convert predicates and contracts into explicit partitions and nearest-neighbor values.
2. Build a decision table whose rows state input/state, expected branch, and expected effect.
3. Cover interactions with a covering array instead of the entire Cartesian product. Choose interaction strength from actual coupling and risk; pairwise is a starting point, not a universal completion threshold.
4. Instrument coverage only to reveal missed branches/conditions. Add an oracle before calling execution meaningful.

NIST describes t-way covering arrays as compact coverage of parameter interactions and discusses their costs and limits in [SP 800-142](https://doi.org/10.6028/NIST.SP.800-142).

## Property-based and stateful testing

Use when a wide structured domain or operation sequence shares semantic invariants.

1. State properties independently of the implementation: round-trip, model equivalence, conservation, bounds, idempotence, monotonicity, representation independence, or an invariant after every action.
2. Generate valid and invalid structures directly. Avoid heavy filtering, assumptions, skips, or early returns; report/category counts so evidence proves target partitions were reached.
3. Seed exact boundaries and historical failures in addition to generated cases.
4. Use rule-based state machines for reusable objects and workflows. Keep a simple model when possible and check invariants after every step.
5. Record seed/settings, shrink the failure, and persist the minimal case only when test modification is authorized.

Hypothesis documents generated edge cases and shrinking in its [main guide](https://hypothesis.readthedocs.io/en/latest/) and generated action sequences in [stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html). Apply the same principles with the repository's language-native framework.

## Coverage-guided or structured fuzzing

Use for parsers, decoders, protocols, serialization, native boundaries, and large byte/string spaces.

1. Make a narrow, fast, deterministic harness. Reset state, join spawned work, bound each case, and treat invalid input as ordinary unless the contract says otherwise.
2. Seed a small diverse corpus of valid, invalid, boundary, and historical cases. Add dictionaries or grammar/structure-aware generation when syntax gates deeper behavior.
3. Give the fuzzer assertions, differential/metamorphic oracles, and applicable runtime detectors. A crash-only harness misses semantic defects.
4. Track whether changed/high-risk branches are reached and whether corpus growth plateaus. Improve the harness, seeds, dictionary, or mutator before merely extending time.
5. Minimize and deterministically replay each failure. Record corpus, seed, build flags, runtime, and case budget.

LLVM's [libFuzzer documentation](https://llvm.org/docs/LibFuzzer.html) covers coverage guidance, corpora, dictionaries, deterministic targets, and sanitizer combinations; it also notes that feature development has stopped and the Clang version must match. Use it only when already configured and compatible, or choose the project's maintained equivalent. Go's [fuzzing documentation](https://go.dev/doc/security/fuzz/) similarly requires fast isolated targets and records minimized failures as regressions. Both can write corpora or crash artifacts, so redirect outputs or use a disposable snapshot.

## Metamorphic testing

Use when exact outputs are expensive or unavailable but necessary relationships are known.

1. Define the source input, a justified transformation, preconditions, and the required relationship between outputs.
2. Attack with several independent relations where possible: round-trip/inverse, idempotence, permutation or representation invariance, neutral elements, scale/translation, partition/recombine, or monotonic order.
3. Specify canonicalization and numeric tolerances. Test the relation itself on known examples; an invalid relation creates false findings.
4. Use violations to seed nearby property or fuzz exploration. Remember that a relation detects only defects that violate that relation.

NIST discusses metamorphic negative/security testing and the oracle problem in [Metamorphic Testing for Cybersecurity](https://www.nist.gov/publications/metamorphic-testing-cybersecurity).

## Differential testing

Use when an independent model, older/newer version, backend, algorithm, optimization, thread count, or configuration should agree.

1. Feed identical defined, deterministic inputs to both sides.
2. Compare canonical semantic results and contractual error classes, not incidental formatting or timing.
3. Exclude undefined, unspecified, ambiguous, or environment-dependent cases unless their handling is itself specified.
4. Minimize disagreements and adjudicate them against the contract. A disagreement proves inconsistency, not which side is wrong.
5. Prefer a simple independent model; implementations sharing dependencies may share the same defect.

The original Csmith work illustrates differential testing with generated inputs constrained to have one defined interpretation: [Finding and Understanding Bugs in C Compilers](https://users.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf).

## Deterministic fault injection

Use for I/O, dependency, clock, queue, transaction, and multi-effect workflows.

1. List each externally visible boundary and the points before, during, and after it.
2. Inject refusal, timeout, malformed/partial response, conflict, retry exhaustion, cancellation, and recovery at one point at a time.
3. Assert returned error, durable state, rollback/cleanup, idempotency, retry budget, and emitted effects.
4. Add combinations only where state can persist from one failure into another.
5. Use fakes, local fixtures, virtual clocks, and bounded subprocesses; never induce faults in live services during a review.

## Concurrency and schedule exploration

Use for shared mutable state, async workflows, cancellation, queues, and locks.

1. Reduce to the smallest competing operations and define safety plus bounded-liveness invariants.
2. Control nondeterministic scheduling, time, messages, failures, and cancellation where tooling permits.
3. Explore short schedules first, then increase threads, steps, or preemption bounds after smaller spaces converge. Use more than one schedule strategy.
4. Preserve a deterministic replay trace. Reset static/global state between iterations.
5. Pair controlled exploration with a race detector and bounded stress. Each technique has blind spots; uncontrolled operations may be invisible to the scheduler.

Microsoft Coyote documents [controlled scheduling, bounds, and replay](https://microsoft.github.io/coyote/get-started/using-coyote/), and Rust Loom documents [permutation exploration and state-space limits](https://docs.rs/loom/latest/loom/). Treat them as workflow examples; use an already-configured, maintained, version-compatible equivalent for the project.

## Runtime sanitizers

Choose by risk and run incompatible/heavy detectors separately. Before interpreting a report, verify platform support and instrumentation completeness against documentation matching the installed compiler:

- [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): bounds, lifetime, use-after-free, and related memory errors.
- [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html): undefined arithmetic, pointer, alignment, and type behavior.
- [MemorySanitizer](https://clang.llvm.org/docs/MemorySanitizer.html): uninitialized reads; require a supported platform and fully instrumented program, dependencies, and C library for defensible results.
- [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html): data races with substantial time/memory overhead; uninstrumented modules create false-negative and possible false-positive blind spots.

Exercise focused tests, generated cases, fuzz corpus, and end-to-end paths in instrumented builds. Record compiler/runtime versions, flags, symbolizer, suppressions, and which dependencies were instrumented. Mark an incomplete run `INCONCLUSIVE`, or `BLOCKED` when the instrumentation precondition prevents execution; never promote it directly to a finding. Preserve symbols and minimize the first report before interpreting later failures. Sanitizers say nothing about unexecuted paths and their runtimes are not production hardening.

## Selective mutation testing

Use after the ordinary suite is green, scoped to changed or high-risk behavior.

1. Run an existing mutation tool against a narrow target in an isolated copy/mode.
2. Triage each survivor: add a behavior-level assertion/property if behavior should differ; classify it equivalent/irrelevant with evidence if not; or identify redundant code.
3. Let the operator choose the next attack: changed conditional → adjacent boundaries; removed call → side-effect oracle; changed return → output invariant; changed constant → scale/threshold cases.
4. Do not optimize a global score. Equivalent mutants and cost make 100% neither necessary nor proof of quality.

PIT explains why mutation measures assertion strength beyond line coverage and recommends frequent [changed-code mutation testing](https://pitest.org/).

## Threat-driven manual and dynamic review

Use for authentication, authorization, cryptography, secrets, trust boundaries, business logic, and high-consequence effects.

1. Map assets, actors, entry points, data flows, roles, and trust boundaries.
2. State attacker goals and abuse sequences; trace untrusted sources through transformations and controls to sensitive sinks.
3. Test controls at every reachable entry point, state transition, tenant/owner boundary, retry/replay route, and failure mode.
4. Use catalogues such as ASVS, CWE, CAPEC, or language-specific CERT rules to expand a concrete hypothesis, never as proof or a blind checklist. Record the release/date and exact rule or entry ID.
5. Escalate a diff review into the reachable architecture when a change affects a security control, trust boundary, dependency, shared parser, or cross-cutting state owner.

See the [OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html), [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html), version-pinned [OWASP ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0), [MITRE CWE Developer View](https://cwe.mitre.org/data/definitions/699.html), [MITRE CAPEC Mechanisms of Attack](https://capec.mitre.org/data/definitions/1000.html), and the current [SEI CERT Coding Standards index](https://cmu-sei.github.io/secure-coding-standards/).

## Research basis and limits

- [NIST IR 8397](https://doi.org/10.6028/NIST.IR.8397) states that executing every possible input is generally impossible and recommends a portfolio including threat modeling, negative/boundary/combinatorial testing, structural coverage, historical regressions, fuzzing, and component analysis. It also warns that high code coverage alone guarantees little.
- [NIST SSDF SP 800-218](https://doi.org/10.6028/NIST.SP.800-218) directs teams to choose executable tests for gaps left by prior review, scope/design/run/document them, record and triage issues, add vulnerability regressions, fuzz input handling, and find root causes.

Therefore report a bounded attack model and residual blind spots, never universal correctness.
