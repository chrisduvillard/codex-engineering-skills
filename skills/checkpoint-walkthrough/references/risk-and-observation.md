# Risk and Observation

## Risk prompts

Select locations where a wrong assumption has high blast radius, not the most complicated code.

Common categories:

- authentication, authorization, session, token, and permission boundaries;
- public APIs, compatibility, serialization, and versioning;
- schemas, migrations, data retention, and rollback;
- billing, metering, pricing, and idempotency;
- validation, sanitization, secrets, cryptography, and privacy;
- concurrency, retries, timeouts, partial failure, and ordering;
- deployment, CI/CD, environment variables, feature flags, and defaults;
- accessibility, error UX, and other high-cost user-visible behavior.

Use this shape:

```text
- <clickable path:line> — [tag] <what assumption matters>
  Reviewer question: <specific question>
  Existing defense: <guard, test, monitor, migration plan, or none found>
```

A risk prompt is not a defect. Use defect language only after a bounded correctness check establishes a reachable problem and consequence.

## Observable verification

Suggest manual observation when it reveals something automated checks may not: interaction quality, rendered UI, CLI clarity, API shape, state transitions, error recovery, rollout behavior, or operator visibility.

Use:

```text
**<Observation name>**
Do: <exact safe action>
Expect: <positive result and important negative behavior>
Covers: <intent or risk prompt>
Safety: <local/test environment and side-effect boundary>
```

Do not duplicate a unit-test command merely to fill the section. It is valid to say there is no useful manual observation.

## Safety screen

Before suggesting or running an observation, identify whether it can:

- modify production or shared state;
- send a message or request to a real person or service;
- create a charge, deployment, account, or external record;
- expose secrets or personal data;
- destroy or irreversibly migrate data.

Keep those checks descriptive until the user separately authorizes the external action and its exact target.
