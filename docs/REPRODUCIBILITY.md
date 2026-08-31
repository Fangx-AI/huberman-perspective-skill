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

After review, promote only the safe derived fields through `export_public_snapshot.py`. The full private contract check is available as `scripts/contract_check_full.py` when all local raw catalogs exist.
