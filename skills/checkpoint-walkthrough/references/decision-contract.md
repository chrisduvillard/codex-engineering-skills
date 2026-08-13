# Decision Contract

The user owns the review decision. Preserve its scope and do not translate it into external action silently.

## Decision packet

Before asking, summarize:

- target and baseline;
- intent and concern groups reviewed;
- risk prompts versus verified findings;
- tests, CI, and observations actually checked;
- omitted or blocked surfaces;
- residual design questions.

In a compact all-in-one response, include this packet and the three decision choices at the end. Do not wait internally for a decision or withhold the walkthrough until the user answers.

## Decision vocabulary

- **Approve:** acceptable within the stated scope and residual gaps.
- **Rework:** a design or implementation concern should change before acceptance.
- **Discuss:** the reviewer needs more evidence or conversation before deciding.

Do not equate Approve with “bug-free,” “safe,” or “fully verified.” Do not turn a risk prompt into a blocking finding unless correctness evidence established it.

## Rework feedback

Tie feedback to:

- exact location or architectural boundary;
- expected behavior or design principle;
- observed evidence or unresolved question;
- smallest change or decision needed;
- verification that would close the concern.

Separate required changes from suggestions.

## External-action gate

The decision itself authorizes no shared-system mutation. Before approving a PR, submitting a review, merging, pushing, releasing, deploying, reverting, closing an issue, or sending feedback externally:

1. Resolve the exact repository, PR, branch, environment, or recipient.
2. Show the action and any message or review body.
3. Obtain explicit user confirmation for that external action.
4. Execute only the confirmed target and report the result.

If the user asked only for a walkthrough, stop after recording the decision and residual gaps.
