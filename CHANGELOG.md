# Changelog

All notable changes follow a simplified Keep a Changelog format. Versions use Semantic Versioning.

## [Unreleased]

- Continue upgrading bibliographic-only and pending academic sources to study-level evidence records.
- Add periodic drift checks for official Episode and platform metadata.

## [0.1.3] - 2026-08-31

### Changed

- Verified 223 additional source identities, raising the queue from 450 to 673 verified records and reducing pending records from 299 to 76.
- Added legacy Nature and ScienceDirect identifier parsing, a provenance-bearing identifier override table, and an NCBI ID Converter fallback for PMC records absent from Europe PMC search.
- Corrected release validation to compare verified queue URLs with linked graph resource URLs; one verified queue record is intentionally not attached to an Episode, so the graph contains 672 verified academic resource nodes.
- Expanded verifier regression coverage to nine tests while preserving bibliographic-only evidence semantics and provider error circuit breaking.

## [0.1.2] - 2026-08-31

### Changed

- Verified 171 additional source identities through Europe PMC, Crossref and available Elsevier responses, raising the verified queue count from 279 to 450 and reducing pending records from 470 to 299.
- Updated the academic verifier to skip identifier-free search pages without consuming the API batch limit, recognize additional Nature and Elsevier identifiers, filter providers and stop querying a provider after repeated API errors.
- Added five verifier regression tests and rebuilt the public knowledge graph with 450 verified academic resource nodes.

## [0.1.1] - 2026-08-31

### Changed

- Verified 31 additional source identities through public bibliographic APIs, raising the verified queue count from 248 to 279 and reducing pending records from 501 to 470.
- Rebuilt the knowledge graph and deterministic public manifest with 279 verified academic resource nodes.
- Added a native PowerShell installation example for Windows users.

## [0.1.0] - 2026-08-31

### Added

- Explicit-only Chinese Huberman perspective Skill with medical and identity boundaries.
- Public source registry, evidence ledger, catalogs and topic knowledge graph.
- 425 Episode records, 424 YouTube records, 34 Bilibili leads and 749 academic/medical source records.
- Reproducible public-snapshot exporter that omits raw Show Notes and transcript payloads.
- Release checks, unit tests, dependency lock, CI, contribution policy, data dictionary and copyright audit.
