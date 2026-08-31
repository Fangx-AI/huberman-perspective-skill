# Reproducibility

## Deterministic release validation

From a clean clone:

```bash
python -m pip install -r requirements.lock
python scripts/release_check.py
python scripts/quality_check.py SKILL.md
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

The committed public snapshot should validate without network access.

On Windows installations whose Python default text encoding is not UTF-8, enable UTF-8 mode before running third-party validators that do not specify an encoding:

```powershell
$env:PYTHONUTF8 = "1"
python path\to\quick_validate.py .
```

The repository's own scripts open project text files explicitly as UTF-8.

## Rebuilding the public snapshot

Raw Episode page data is intentionally absent from Git. A maintainer with a lawful local research cache can rebuild the sanitized files:

```bash
python scripts/export_public_snapshot.py \
  --source /path/to/local/huberman-perspective \
  --destination .
python scripts/release_check.py
```

The exporter reads local `episode-pages.jsonl`, `claim-index.jsonl` and `knowledge-graph.json`, then emits only `episodes.csv`, a claim locator without `claim_text`, a sanitized graph and a SHA-256 manifest. Given identical inputs, output bytes are deterministic.

## Full network refresh

The collectors use public webpages/APIs and therefore produce time-varying results. Run them into an ignored `work/` directory first. Review source terms, robots/access constraints, rate limits and individual article licenses before retrieval. Never bypass paywalls or access controls.

Incremental bibliographic verification can be run in small batches:

```bash
python scripts/verify_academic_batch.py \
  --queue references/catalog/academic-verification-queue.csv \
  --limit 20
```

If one provider is rate-limited, continue only through the unaffected public providers:

```bash
python scripts/verify_academic_batch.py \
  --queue references/catalog/academic-verification-queue.csv \
  --limit 20 \
  --providers europe-pmc crossref
```

The verifier skips identifier-free search pages, preserves unresolved rows as `pending` and stops querying a provider after repeated API errors. It reads exact legacy repairs from `academic-identifier-overrides.csv` and can use the NCBI ID Converter when Europe PMC search does not return a known PMCID. Overrides require official provenance and still pass through a public bibliographic API. A successful API match produces `verified-bibliographic` only; it does not establish study design, efficacy or safety.

After each verification batch, rebuild the deterministic repair queue:

```bash
python scripts/build_academic_repair_queue.py \
  --queue references/catalog/academic-verification-queue.csv \
  --output references/catalog/academic-repair-queue.csv
```

After a human reviewer has read the primary study and recorded design, sample, positive and negative findings, limitations, safe interpretation and provenance in `academic-study-cards.jsonl`, apply the cards deterministically:

```bash
python scripts/apply_academic_study_cards.py \
  --cards references/catalog/academic-study-cards.jsonl \
  --queue references/catalog/academic-verification-queue.csv
```

The command refuses to promote a `pending` record, verifies exact URL alignment and is idempotent. Use `--check-only` to validate cards without writing.

After review, promote only the safe derived fields through `export_public_snapshot.py`. The full private contract check is available as `scripts/contract_check_full.py` when all local raw catalogs exist.
