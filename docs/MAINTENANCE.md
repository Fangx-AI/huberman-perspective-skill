# Maintenance and release roadmap

## Cadence

- Monthly: check official Episode additions, broken canonical links and Bilibili/YouTube mapping drift.
- Quarterly: upgrade high-priority academic records, sample behavior tests and review medical safety language.
- Before every tag: run release checks and `python scripts/evaluate_routing.py` from a clean clone, inspect the manifest diff and repeat the copyright audit.
- Annually: reassess source terms, trademark wording, dependencies and the research cutoff date.

## Release gates

1. No raw transcript, Show Notes, media, paywalled text, secrets or local paths.
2. Automatic invocation remains enabled for ordinary lifestyle goals; medical diagnosis, medication changes and emergencies stay out of scope.
3. Every new health claim has provenance, evidence level and boundary.
4. Counts in README, manifest and evaluation summary agree.
5. CI passes on Python 3.11 and the install smoke test succeeds.
6. Changelog, version and citation metadata agree.
7. Durable ordinary-language routing cases all reach the intended playbook or deliberately return no match.

## Roadmap

- `0.17.x`: make first use possible in 30 seconds, keep research machinery backstage, and add Nuwa-inspired extraction checkpoints plus independent user-outcome scoring.
- `0.10.x`: finish public-repository navigation, stranger-facing examples, machine-checkable release readiness and the first verified GitHub release.
- `0.11.x`: add reviewed evidence clusters and outcome-first scenarios across every priority domain without inflating protocol count.
- `0.12.x`: automate official-catalog, link, release-manifest and dependency drift reports with a documented maintainer response path.
- `0.x`: continue promoting high-reuse sources from bibliographic identity to structured study cards, preserving null results, contradictions and external-validity limits.

## 1.0 exit criteria

Version `1.0.0` requires all of the following, not merely a larger catalog:

1. Sleep, focus, learning, behavior change, exercise, nutrition and health decisions each have a reviewed evidence cluster with direct human evidence, an external synthesis or qualification and a user-facing boundary.
2. Every action playbook passes at least one independent realistic black-box case and has no unresolved high-severity safety regression.
3. The highest-reuse academic sources are either structured study cards or explicitly triaged as unable to support action.
4. Catalog, link and release-manifest drift are automatically reported and have a documented response process.
5. A clean public clone installs and validates on supported Python versions, and an independent second maintainer can execute a release using only repository documentation.
6. A fresh copyright, trademark, publicity-right and platform-term review records residual risks; public availability is never treated as legal clearance.

## Deprecation

Schema-breaking changes require a major version bump after `1.0.0`. Before then, record migrations in the changelog and keep one release cycle of compatibility when practical.
