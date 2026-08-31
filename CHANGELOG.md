# Changelog

## [1.0.1] - 2026-08-31

### Security

- Confine Brownfield source selectors to regular files inside configured repositories.
- Reject symlinks, linked parents, reparse points, and path escapes.
- Detect source drift during read-only runs.

### Fixed

- Validate Brownfield structures against bundled JSON Schemas before semantic checks.
- Expand context dependencies transitively and emit dependencies first.
- Reject duplicate record IDs in all read paths.
- Make initialization transactional and Git execution bounded.
- Require current executable verification receipts for completion checks.

### Changed

- Add a central catalog, routing contract, invocation policies, and routing fixtures.
- Add Fast, Standard, and Deep profiles to expensive review workflows.
- Namespace Deep Plan artifacts and serialize canonical progress ownership.
- Remove private project instructions from the generic branch-recovery skill.
- Add PowerShell and repository-scoped installation guidance.
- Expand CI across Ubuntu, Windows, Python 3.11, and Python 3.13.
