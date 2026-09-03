# Project status and completion audit

This file maps the long-term project objective to evidence in the repository. Passing the release checker proves the current snapshot is internally consistent; it does not prove that every Huberman episode or every cited paper has been fully distilled.

Status date: 2026-09-03.

| Objective requirement | Authoritative evidence | Status |
|---|---|---|
| Catalog public long-form material across official pages, YouTube, Bilibili and courses | `episodes.csv`, `youtube-transcript-queue.csv`, `bilibili-discovery.csv`, `courses-lectures.csv` | Current official catalog captured; drift monitoring remains ongoing |
| Preserve traceable claims without redistributing transcripts | `claim-index.jsonl`, `source-registry.md`, `release_check.py` | Implemented for the current public snapshot |
| Connect claims, studies, limitations and contradictions | `academic-study-cards.jsonl`, `evidence-relations.jsonl`, `knowledge-graph.json` | Implemented, but research-level coverage remains partial |
| Help ordinary users improve health-related daily life | `SKILL.md`, `coaching-guide.md`, `USAGE_EXAMPLES.md` | Automatic lifestyle guidance now starts from the user's real outcome, constraints and safest next step |
| Turn evidence into action without knowledge overload | Thirteen outcome-first playbooks, a durable ordinary-language routing corpus and user-guidance contract tests | Implemented for thirteen high-frequency scenarios; 50 first-use routing cases are regression tested and more scenarios remain |
| Keep deep research backstage and independently test user value | `ARCHITECTURE.md`, `extraction-framework.md`, `huberman-operating-model.md`, `fidelity-scorecard.md`, `research_checkpoint.py` | Nuwa-inspired maintenance structure implemented; health-specific user-outcome and safety gates added |
| State evidence levels, medical boundaries and uncertainty | `SKILL.md`, `evidence-ledger.md`, structured card limitations and stop/escalation fields | Implemented and regression tested |
| Respect copyright, platform terms and third-party ownership | `COPYRIGHT_AND_DATA_POLICY.md`, `DATA-LICENSE.md`, `THIRD_PARTY_NOTICES.md`, forbidden-payload release checks | Engineering controls implemented; not a substitute for legal clearance |
| Provide installation, verification, contribution and reproducibility paths | `README.md`, `USAGE_EXAMPLES.md`, `CONTRIBUTING.md`, `REPRODUCIBILITY.md`, CI and clean-install test | One-command first use and manual fallback implemented for a public clone |
| Provide versioning, citation and maintenance roadmap | `VERSION`, `CHANGELOG.md`, `CITATION.cff`, `MAINTENANCE.md` | Implemented |
| Publish as a public GitHub repository | <https://github.com/Fangx-AI/huberman-perspective-skill> and verified public `origin` metadata | Repository published; every tag still requires release and CI verification per `PUBLISHING.md` |

## Current research gap

The product goal is not to expose the largest possible research archive. The user-facing measure is whether a person can describe an ordinary problem in their own words and receive a small, safe, observable next step with a workable failure adjustment. Evidence coverage matters because it improves those decisions and boundaries; it is not the default conversation.

The public academic queue contains 1,736 deduplicated Show Notes URLs. Only 684 have bibliographic or stronger verification, and only 52 high-priority papers or guidelines currently have full structured evidence cards. `verified-bibliographic` confirms identity only; it cannot support efficacy. The remaining queue and future episodes keep the long-term Goal active.

The private maintainer cache records batch-level analysis for 423 available canonical YouTube videos, while the public claim locator intentionally exposes only a small, copyright-minimized set of neutral claim records. This protects source expression but means public users cannot independently reproduce every transcript-level judgment from repository payloads alone.

## What would justify 1.0

Version 1.0 requires more than increasing counts:

1. Every priority domain—sleep, focus, learning, behavior change, exercise, nutrition and health decisions—has a reviewed evidence cluster with direct human evidence, at least one synthesis or external qualification, and an explicit user-facing boundary.
2. Every released action playbook passes an independent realistic black-box case and has no unresolved high-severity safety regression.
3. The highest-reuse academic sources are either promoted to structured cards or explicitly triaged with a documented reason they cannot support action.
4. Link drift, catalog drift and release-manifest drift have automated reports and a maintainer response process.
5. A clean public clone installs and validates on supported Python versions, and a second maintainer can perform a release using only the documented process.

Until these conditions are met, releases should remain clearly labeled as research previews.
