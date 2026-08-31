# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Security

- Confine Brownfield source fingerprints to regular files within configured repository roots.
- Reject source drift during read-only Brownfield runs.

### Fixed

- Validate Brownfield memory against the bundled JSON Schemas before semantic checks.
- Expand transitive context dependencies in dependency-first order.
- Replace free-text completion claims with source-linked verification receipts.

### Changed

- Add collection-wide routing metadata, invocation policies, evaluation fixtures, and cross-platform CI.
