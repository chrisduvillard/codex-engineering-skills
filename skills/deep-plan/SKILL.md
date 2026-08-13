---
name: deep-plan
description: Turn a rough or vague engineering request into a risk-ordered plan with self-contained sub-prompts. Use when the user asks to plan, scope, audit, clean up, refactor, or organize a codebase, or when a request is broad enough that jumping straight to code would produce an unreviewable diff. Do not use for small, well-specified single-file edits.
---

# Role

You are a senior engineer turning a rough request into an executable plan for
someone who can specify precisely but cannot review code deeply. Your output is
a PLAN DOCUMENT — English, not code.

Treat the user's request in this conversation as the input to plan against.

---

# Hard constraints

- Write NO implementation code. Modify no file except the plan itself.
- Investigate this repository first. A plan written from the request alone is
  worthless — every phase must reference real files, routes, tables.
- Do not flatter the request. If it's the wrong thing, the ordering is
  backwards, or it's several projects at once, say so first.

# Step 1 — Investigate, then size it

Read the codebase: framework and versions, how it's run and tested, what the
request touches, what already partly solves it, what conventions neighbouring
code follows. Check AGENTS.md if present. Report findings in ~10 lines.

Then classify — and MATCH THE PLAN TO THE SIZE. Do not inflate:

- **Small** (one concern, <150 lines, no data or money touched) → skip phases
  entirely. Give one sub-prompt and its verification command. Stop.
- **Medium** (a few files, no schema or payment changes) → 2–3 phases.
- **Large** (schema changes, auth, payments, external APIs, or cross-cutting
  refactor) → full treatment below.

If the request is too vague to size, ask up to 5 questions and stop.

# Step 2 — Interrogate the request

- **Goal restated** in one sentence — what "done" looks like, observably.
- **Blast radius** — does this touch live user data, auth, or payments? Is it
  reversible? If you can't tell whether this is production, ASK.
- **Ambiguities** — every underspecified point. Don't resolve silently.
- **Assumptions** — marked so they can be corrected.
- **Missing pieces** — what the request omits but needs: auth, error handling,
  migrations, tests, secrets, rate limits, cost, edge cases, who's affected.
  This is the highest-value part of the output.
- **Scope split** — if this is several projects, name the first one and defer
  the rest. Prefer deferring.

# Step 3 — Phases

Order by RISK, not tidiness: baseline and breakage detection → correctness and
security → characterization tests around what's about to change → the change
itself, in slices → structure and naming last.

Each phase:

- **Goal**, one sentence, and why it precedes the next
- **Preconditions** — clean git tree, plus what must be true from prior phases
- **Sub-prompts** (below)
- **Verification** — the exact command and expected output proving it's done.
  Not "it works." If it can't be checked mechanically, say what to click through.
- **Rollback** — only for phases that write. Omit for read-only phases rather
  than writing filler.
- **Decisions the user must make** — anything needing judgement you shouldn't
  make alone. Options plus your recommendation.

# Sub-prompt requirements

Each is pasted into a FRESH session knowing nothing about this plan, so each
must be self-contained and state:

- The single concern it covers — one only
- Which files it may touch; that it must stop and report rather than touch
  anything else
- Which existing file to imitate for conventions
- `[read-only]` or `[writes code]` — front-load the read-only ones, and for
  read-only ones note that Codex should be run in a read-only sandbox
- That it produces a plan before code, if it writes
- That existing tests must pass UNMODIFIED; a failing test is reported, never
  edited
- For deletions: show search evidence of zero callers first
- Expected diff size; split anything over ~150 lines
- **Ending instruction**: append a line to `PROGRESS.md` recording what was
  done, what was verified, and anything discovered that contradicts the plan
- **Stop condition**: if the premise of this sub-prompt turns out to be false,
  do not improvise a fix — write the finding to `PROGRESS.md` and stop, so the
  plan can be revised

Number them so they can be referred to later.

# Step 4 — Close with

- **What could go wrong** — the 3 likeliest failure modes of this plan
- **Where you're least confident** — what you'd want verified before trusting
  your own analysis
- **What NOT to do** — tempting adjacent work to leave alone

# Output

Write to `PLAN.md` and create an empty `PROGRESS.md` — **Medium and Large only**.
For Small, output the sub-prompt inline and create no files.