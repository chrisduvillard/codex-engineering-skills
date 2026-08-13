# Evidence Contract

Use this contract for every claim that can change the decision.

## Evidence firewall

Keep two evidence domains distinct:

- **Requirements evidence:** user statements, repository code, architecture records, policies, budgets, and project constraints. It defines what the decision must satisfy.
- **External claim evidence:** material retrieved or imported during this run. It establishes facts about candidates and the outside world.

Project preferences cannot prove a vendor claim. External popularity cannot define a project requirement. Prior model knowledge may suggest a query but cannot close a claim whose truth is current, contested, or consequential.

## Claim ledger

Record:

| Field | Meaning |
|---|---|
| Claim | One falsifiable sentence |
| Decision effect | Criterion, gate, or conclusion affected |
| Source | Direct URL or exact repository location |
| Publisher | Independent origin, not the page that repeated it |
| Date/version | Publication date, effective date, or tested version |
| Accessed | Date retrieved this run |
| Source class | Primary, independent secondary, user-provided, or aggregator |
| Status | Verified, supported, disputed, unverified, or overturned |
| Confidence | High, medium, or low, with a short reason |
| Counterevidence | What was sought and what materially disagrees |
| Recheck | Date or event that makes the claim stale |

## Status rules

- **Verified:** an authoritative primary source and, when the claim is contested or decisive, an independent source support the same material conclusion.
- **Supported:** one credible, fresh source supports the claim; no material contradiction was found within budget.
- **Disputed:** credible sources materially disagree. Preserve both; never average them into fake consensus.
- **Unverified:** the claim remains relevant but the evidence budget could not establish it.
- **Overturned:** stronger evidence contradicts the original claim; correct the decision record and retain the reversal in the ledger.

Confidence is per claim, not per section. A polished report does not upgrade weak evidence.

## Source and freshness rules

- Prefer official documentation, source code, release notes, standards, regulator text, filings, current pricing, and original research.
- Follow aggregators to their underlying source. Cite the origin, not the answer engine or roundup.
- Treat syndicated articles and repeated vendor statistics as one publisher.
- Check current versions, dates, editions, regions, tiers, and deprecation status.
- For rapidly changing facts such as price, supported versions, limits, and product availability, use the current primary page and record the access date.
- For benchmarks, require comparable workloads and configurations. Otherwise label the comparison directional or incomparable.
- For anecdotes, seek patterns and failure mechanisms; do not convert popularity into reliability.

## Two-source default

Seek independent corroboration for:

- any claim that eliminates a finalist;
- price or total-cost figures that change the winner;
- security, compliance, durability, availability, or data-loss claims;
- performance or scale numbers separating the top two;
- migration and exit-cost claims;
- the strongest argument against the provisional leader.

If corroboration is unavailable, keep the claim visible as unverified and test whether the decision still holds without it.
