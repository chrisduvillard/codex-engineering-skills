# Skill Routing

Use the narrowest skill that owns the user's decision.

| User intention | Primary skill |
| --- | --- |
| Audit an existing system broadly | `reasoning-codebase-review` |
| Falsify a proposed change or pull request | `adversarial-review` |
| Walk a human through a change | `checkpoint-walkthrough` |
| Review completed work across commits or tickets | `evidence-retrospective` |
| Follow one value through a data pipeline | `trace-data-provenance` |
| Compare consequential engineering options | `decision-recon` |
| Produce an implementation plan | `deep-plan` |
| Pressure-test an early idea | `idea-forge` |
| Reduce repository instruction context | `context-pruner` |
| Recover work from a divergent branch | `harvest-agent-branches` |
| Maintain durable cross-session project knowledge | `steward-brownfield` |

## Composition

```text
idea-forge -> decision-recon -> deep-plan
deep-plan -> implementation -> adversarial-review -> checkpoint-walkthrough
completed work -> evidence-retrospective -> deep-plan
long-running system -> steward-brownfield throughout
```

Do not invoke overlapping review skills merely for ceremony. Compose them only when each step changes
one distinct decision.
