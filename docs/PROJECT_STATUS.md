# Project status and completion audit

This file maps the long-term project objective to evidence in the repository. Passing the release checker proves the current snapshot is internally consistent; it does not prove that every Huberman episode or every cited paper has been fully distilled.

Status date: 2026-08-31.

| Objective requirement | Authoritative evidence | Status |
|---|---|---|
| Catalog public long-form material across official pages, YouTube, Bilibili and courses | `episodes.csv`, `youtube-transcript-queue.csv`, `bilibili-discovery.csv`, `courses-lectures.csv` | Current official catalog captured; drift monitoring remains ongoing |
| Preserve traceable claims without redistributing transcripts | `claim-index.jsonl`, `source-registry.md`, `release_check.py` | Implemented for the current public snapshot |
| Connect claims, studies, limitations and contradictions | `academic-study-cards.jsonl`, `evidence-relations.jsonl`, `knowledge-graph.json` | Implemented, but research-level coverage remains partial |
| Produce a callable Chinese Huberman-perspective Skill | `SKILL.md`, `agents/openai.yaml`, `action-playbooks.jsonl` | Implemented and installed locally |
| Put user outcomes ahead of knowledge accumulation | Six outcome-first playbooks and Cases 5–10 | Implemented for six high-frequency scenarios; more scenarios remain |
| State evidence levels, medical boundaries and uncertainty | `SKILL.md`, `evidence-ledger.md`, structured card limitations and stop/escalation fields | Implemented and regression tested |
| Respect copyright, platform terms and third-party ownership | `COPYRIGHT_AND_DATA_POLICY.md`, `DATA-LICENSE.md`, `THIRD_PARTY_NOTICES.md`, forbidden-payload release checks | Engineering controls implemented; not a substitute for legal clearance |
| Provide installation, verification, contribution and reproducibility paths | `README.md`, `USAGE_EXAMPLES.md`, `CONTRIBUTING.md`, `REPRODUCIBILITY.md`, CI and clean-install test | Implemented for a public clone |
| Provide versioning, citation and maintenance roadmap | `VERSION`, `CHANGELOG.md`, `CITATION.cff`, `MAINTENANCE.md` | Implemented |
| Publish as a public GitHub repository | <https://github.com/Fangx-AI/huberman-perspective-skill> and verified public `origin` metadata | Repository published; every tag still requires release and CI verification per `PUBLISHING.md` |

## Current research gap

The public academic queue contains 1,736 deduplicated Show Notes URLs. Only 673 have bibliographic or stronger verification, and only 20 high-priority papers currently have full structured study cards. `verified-bibliographic` confirms identity only; it cannot support efficacy. The remaining queue and future episodes keep the long-term Goal active.

The private maintainer cache records batch-level analysis for 423 available canonical YouTube videos, while the public claim locator intentionally exposes only a small, copyright-minimized set of neutral claim records. This protects source expression but means public users cannot independently reproduce every transcript-level judgment from repository payloads alone.

## What would justify 1.0

Version 1.0 requires more than increasing counts:

1. Every priority domain—sleep, focus, learning, behavior change, exercise, nutrition and health decisions—has a reviewed evidence cluster with direct human evidence, at least one synthesis or external qualification, and an explicit user-facing boundary.
2. Every released action playbook passes an independent realistic black-box case and has no unresolved high-severity safety regression.
3. The highest-reuse academic sources are either promoted to structured cards or explicitly triaged with a documented reason they cannot support action.
4. Link drift, catalog drift and release-manifest drift have automated reports and a maintainer response process.
5. A clean public clone installs and validates on supported Python versions, and a second maintainer can perform a release using only the documented process.

Until these conditions are met, releases should remain clearly labeled as research previews.
