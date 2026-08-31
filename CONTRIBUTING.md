# Contributing

Contributions are welcome when they improve traceability, evidence quality, safety or reproducibility.

## Before opening a change

1. Do not submit full transcripts, caption files, audio, video, images, complete Show Notes, paywalled text or paper PDFs.
2. Link the canonical source. Bilibili mirrors must also identify the official Episode or YouTube source when known.
3. Distinguish the speaker: Huberman, guest, mixed discussion, or external research.
4. Do not present mechanism, animal evidence or a single study as settled human efficacy.
5. Health changes must state population, design, primary outcome, uncertainty, contraindications and when professional care is needed.

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

## Status vocabulary

- `verified-study`: design, main result and limits checked for an original study.
- `verified-observational`: association checked; no causal wording.
- `verified-review`: review/meta-analysis scope and heterogeneity checked.
- `verified-bibliographic`: identity only; cannot support efficacy.
- `pending`: not yet manually verified.

## Required checks

```bash
python scripts/release_check.py
python scripts/quality_check.py SKILL.md
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

Changes to schemas must update `docs/DATA_DICTIONARY.md`, the exporter, tests and changelog together. Changes to invocation policy must remain explicit-only unless maintainers intentionally make and document a different product decision.
