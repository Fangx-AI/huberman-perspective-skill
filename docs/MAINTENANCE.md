# Maintenance and release roadmap

## Cadence

- Monthly: check official Episode additions, broken canonical links and Bilibili/YouTube mapping drift.
- Quarterly: upgrade high-priority academic records, sample behavior tests and review medical safety language.
- Before every tag: run release checks from a clean clone, inspect the manifest diff and repeat the copyright audit.
- Annually: reassess source terms, trademark wording, dependencies and the research cutoff date.

## Release gates

1. No raw transcript, Show Notes, media, paywalled text, secrets or local paths.
2. Explicit-only invocation remains enabled.
3. Every new health claim has provenance, evidence level and boundary.
4. Counts in README, manifest and evaluation summary agree.
5. CI passes on Python 3.11 and the install smoke test succeeds.
6. Changelog, version and citation metadata agree.

## Roadmap

- `0.1.x`: public-repository hardening, rights review, schema stabilization and bug fixes.
- `0.2.0`: raise research-level academic coverage and expand timestamped claim cards without transcript redistribution.
- `0.3.0`: add contradiction/replication edges and automated link-rot reports.
- `1.0.0`: stable schemas, repeatable update cadence, independent behavior evaluation and documented maintainer succession.

## Deprecation

Schema-breaking changes require a major version bump after `1.0.0`. Before then, record migrations in the changelog and keep one release cycle of compatibility when practical.
