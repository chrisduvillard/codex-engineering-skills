# Change Ledger

The ledger proves that pruning did not silently discard protection.

## Entry shape

| Field | Meaning |
|---|---|
| ID | Stable short identifier |
| Source | File and exact current line or section |
| Current instruction | Original user-visible rule |
| Protected behavior | What changes if the rule disappears |
| Evidence | Repository source, policy owner, or observed mistake |
| State | Verified, contradicted, stale, unverified, or policy |
| Disposition | Retain, rewrite, relocate, automate, or delete |
| Destination | File, trigger, or enforcement mechanism |
| Deletion ground | 1–4 when deleting |
| Context delta | Always-loaded lines/words added or removed |
| Approval | Covered by request or line-item required |

Open existing entries at Retain or Rewrite. Settle them only after evidence inspection.

Complete accounting does not require complete verification. When the evidence budget ends, every instruction still receives an entry with state Unverified and disposition Retain; do not keep searching merely to avoid an unresolved ledger row.

## Dispositions

- **Retain:** text and scope already change behavior correctly.
- **Rewrite:** preserve the protection while making the action, scope, or evidence precise.
- **Relocate:** move behind a verified loading path or observable trigger; record the destination.
- **Automate:** propose or use mechanical enforcement. Retain prose until the check exists and passes.
- **Delete:** remove only under one of the grounds below.

## Deletion grounds

1. **Stale or incorrect:** the referent is gone or evidence establishes the rule is false.
2. **Mechanically enforced:** a live hook, validator, linter, formatter, schema, or CI check rejects the violation.
3. **Harmful, contradictory, or duplicate in loaded context:** stronger live authority wins, or the same rule is already loaded once; record the survivor.
4. **Explicit user approval:** the user approves this specific deletion after seeing its protected behavior and risk.

Brevity, derivability, low recent failure rate, aesthetic preference, or discoverability elsewhere are not deletion grounds.

## Approval rules

An explicit edit request covers retain, evidence-preserving rewrite, supported relocation, an automation reference to an existing check, and deletion under grounds 1–3. Require line-item approval for:

- deletion with only ground 4;
- relocation whose loading path is unverified;
- a rewrite that changes policy or relaxes a prohibition;
- moving a team rule into personal configuration;
- replacing human testimony with an inference.

If approval is declined, revert the proposed entry to Retain and report the resulting budget.

## Reporting

Show every existing instruction's destination. Retains and equivalent rewrites may be grouped; itemize every relocation, automation, and deletion. “The file got shorter” is not a ledger outcome.
