# Changelog

All notable changes follow a simplified Keep a Changelog format. Versions use Semantic Versioning.

## [Unreleased]

- Continue expanding structured study cards beyond the first high-priority batch.
- Add replication/contradiction review cards and periodic drift checks for official Episode and platform metadata.

## [0.4.1] - 2026-08-31

### Added

- Added a structured external-context card for Nettersheim et al. (2015), including its 61-person design, 30-minute early boost, four-hour decay, polysomnography, null sleep-stage correlations and pre-sleep-estimation boundary.
- Added `qualifies` and `supports` relations that connect Nettersheim 2015 to Walker 2003 and Rickard 2008 as a three-study evidence triangle.
- Added regression coverage for incoming/outgoing relation direction and stabilization-focused Chinese retrieval.

### Changed

- Expanded the graph to eight study cards, 36 findings, 46 limitations, 30 evidence topics, three evidence relations, 6,022 resource nodes and 8,490 edges.
- Made command-line relation output explicit about whether the current study or the counterpart is the source of a relation.
- Preserved the 749-row Episode Show Notes queue unchanged while raising graph-level verified academic resources to 675 through two explicitly external cards.

## [0.4.0] - 2026-08-31

### Added

- Added a structured external-context card for Rickard et al. (2008), preserving the two-experiment design, large between-session exclusion count, reactive-inhibition/fatigue analysis, absent wake control in Experiment 2 and stabilization boundary.
- Added `evidence-relations.jsonl` and a validator for typed `replicates`, `supports`, `qualifies`, `challenges` and `contradicts` links between study cards.
- Added first-class evidence-relation graph nodes and query output that surfaces bounded counterevidence next to the matched study.

### Changed

- Advanced the full graph to `episode-topic-platform-claim-study-relation-v5` with seven study cards, 28 findings, 38 limitations, 26 evidence topics, one evidence relation, 6,021 resource nodes and 8,462 edges.
- Allowed manually reviewed external-context cards to remain outside the Episode Show Notes queue through explicit empty `queue_urls`, preserving all queue counts.
- Added regression coverage for external cards, relation validation, graph relations and counterevidence-aware Chinese querying.

## [0.3.2] - 2026-08-31

### Added

- Added a structured evidence card for Walker et al. (2003) on sleep and sequential finger-tapping performance, preserving the 40-person new cohort, reused 30-person comparison data, non-significant three-night trends and task-specific interpretation.
- Added a Chinese sleep/motor-learning evidence-query regression.

### Changed

- Promoted the linked PMC record to `verified-study`, yielding 114 study-level and 507 bibliographic-only verified records.
- Expanded the graph to six study cards, 23 findings, 32 limitations, 24 evidence topics and 8,443 relations.
- Weighted evidence-query matches in study design, results and safe interpretation above incidental matches found only in limitations.

## [0.3.1] - 2026-08-31

### Added

- Added a structured clinical evidence card for the eight-week EPA/fluoxetine major-depression trial, including its absent pure-placebo arm, 48-person analysis set, LOCF limitation and explicit no-self-medication boundary.

### Changed

- Promoted two duplicate URL records for the trial to `verified-study`, yielding 113 study-level and 508 bibliographic-only verified records.
- Expanded the graph to five study cards, 18 findings, 25 limitations, 20 evidence topics and 8,426 relations.
- Replaced fixed study-card graph counts in release validation with invariants derived directly from the committed cards.

## [0.3.0] - 2026-08-31

### Added

- Added first-class `study-card`, `study-finding`, `study-limitation` and `evidence-topic` graph nodes with auditable resource, result, null-finding and limitation relations.
- Added a bilingual evidence-card query command that always returns negative findings, limitations, safe interpretation and primary-source provenance alongside matching results.
- Added graph-builder integration tests and evidence-query regression tests.

### Changed

- Advanced the full graph to `episode-topic-platform-claim-study-v4` and the sanitized public graph to `public-evidence-v2`.
- Expanded the graph from 8,355 to 8,412 relations while keeping all prior Episode, platform, claim and academic-resource counts stable.

## [0.2.0] - 2026-08-31

### Added

- Added four machine-readable study cards for high-priority meditation, binaural-beat, caffeine PET and gratitude-writing papers. Every card preserves study design, sample, outcomes, negative findings, limitations, safe interpretation and primary-source provenance.
- Added a deterministic card-to-queue application command, idempotence and refusal guards, release invariants and regression tests.

### Changed

- Promoted five URL records representing four papers from bibliographic-only to `verified-study`, yielding 111 study-level, 32 review-level, 21 observational and 510 bibliographic-only verified records.
- Corrected the brief-meditation sample from 76 to 42 and recorded its four-week null result, unexpected sleep-quality result and adherence imbalance.
- Tightened the binaural-beat, caffeine and gratitude summaries so task-specific, correlational and null findings cannot be rewritten as universal protocols or treatment effects.

## [0.1.4] - 2026-08-31

### Added

- Added a deterministic academic repair queue that classifies every remaining pending source and gives a bounded next action for Elsevier PII, nonspecific search/publisher pages, reference works, missing identifiers and malformed URLs.
- Added three repair-queue regression tests and a release invariant requiring repair-queue URLs to equal pending verification-queue URLs.

### Changed

- Verified one additional Elsevier source, raising coverage to 674 of 749 records and reducing the classified repair queue to 75 rows.

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
