# Contributing

Contributions are welcome when they improve traceability, evidence quality, safety or reproducibility.

## Before opening a change

1. Do not submit full transcripts, caption files, audio, video, images, complete Show Notes, paywalled text or paper PDFs.
2. Link the canonical source. Bilibili mirrors must also identify the official Episode or YouTube source when known.
3. Distinguish the speaker: Huberman, guest, mixed discussion, or external research.
4. Do not present mechanism, animal evidence or a single study as settled human efficacy.
5. Health changes must state population, design, primary outcome, uncertainty, contraindications and when professional care is needed.
6. Replication or counterevidence not cited in Episode Show Notes must use `source_scope=external-context` and `queue_urls=[]`; never add it to the Episode queue merely to satisfy card validation.
7. Use `replicates` only for genuinely independent repetition. Overlapping authors/laboratories or reused cohorts/data should normally be represented as `supports` or `qualifies`, with the overlap stated in the relation boundary.
8. For `verified-review` cards, encode `sample_size` as a non-empty description of the review scope, not as a fictitious participant count. State whether the source is systematic, meta-analytic or narrative, and record missing search, risk-of-bias or pooled-effect methods as limitations. Original and observational study cards must use a positive integer participant/sample count.
9. Action playbooks must solve one observable user goal with one to three actions. Each action needs a classification, trigger, minimum version, metric, review interval, adaptation and stop conditions; each playbook must link reviewed study evidence and public claim context.
10. Do not turn framework inferences or low-risk experiments into validated prescriptions. Preserve exclusions, escalation conditions and dose/timing uncertainty, especially for sleep, supplements, mental health and clinical topics.

## Evidence contribution template

Include the following in the pull request description:

- Claim in neutral language
- Canonical source URL and timestamp/page locator
- Source owner/speaker
- Research design and sample/setting
- Main result, including null or mixed outcomes
- Evidence level
- Conflicts, funding or replication concerns
- Population and external-validity limits
- Medical safety boundary
- Copyright statement confirming no restricted payload was added
- For study-to-study claims: relation type, exact claim scope, rationale, boundary and both card IDs
- For action playbooks: user outcome, likely execution barrier, one-to-three action rationale, all evidence/claim IDs, classification of each step, failure adaptation and safety escalation

## Status vocabulary

- `verified-study`: design, main result and limits checked for an original study.
- `verified-observational`: association checked; no causal wording.
- `verified-review`: review/meta-analysis scope and heterogeneity checked.
- `verified-bibliographic`: identity only; cannot support efficacy.
- `pending`: not yet manually verified.

## Required checks

```bash
python scripts/release_check.py
python scripts/validate_evidence_relations.py --cards references/catalog/academic-study-cards.jsonl --relations references/catalog/evidence-relations.jsonl
python scripts/validate_action_playbooks.py --playbooks references/catalog/action-playbooks.jsonl --study-cards references/catalog/academic-study-cards.jsonl --claims references/catalog/claim-index.jsonl
python scripts/quality_check.py SKILL.md
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

Changes to schemas must update `docs/DATA_DICTIONARY.md`, the exporter, tests and changelog together. Changes to invocation policy must remain explicit-only unless maintainers intentionally make and document a different product decision.
