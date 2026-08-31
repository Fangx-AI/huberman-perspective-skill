#!/usr/bin/env python3
"""Incrementally verify academic queue records against public bibliographic APIs.

This tool is intentionally conservative: a successful lookup only upgrades a
pending row to ``verified-bibliographic``. It never infers study design,
efficacy, safety, or clinical recommendations from a URL or abstract alone.
Run it repeatedly with a small limit; existing non-pending rows and notes are
preserved by design.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from urllib.error import HTTPError
from urllib.request import Request, urlopen


PMCID_RE = re.compile(r"PMC\d+", re.IGNORECASE)
PMID_RE = re.compile(r"(?:pubmed\.ncbi\.nlm\.nih\.gov/|pmid[:/ ]+)(\d+)", re.IGNORECASE)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
PII_RE = re.compile(r"S\d{4,8}-\d{4}\(\d{2}\)\d{4,6}-[0-9X]|\bS\d{14,17}[0-9X]\b", re.IGNORECASE)
NATURE_SLUG_RE = re.compile(r"(?:d41586|s\d{4,6}-\d{3,4}-\d{4,6}(?:-[a-z0-9]+)?|nature\d+|nrn\d+|nm\d+[_-]\d+|tp\d+|\d{6,8}[a-z]\d*)", re.IGNORECASE)
MALFORMED_CELL_URL_RE = re.compile(r"/S\d{4}-\d{4}\(\d{2}$", re.IGNORECASE)
PROVIDERS = ("europe-pmc", "crossref", "elsevier")


def request_json(url: str, timeout: float, user_agent: str) -> dict:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def identifiers(url: str) -> dict[str, str]:
    decoded = unquote(url)
    pmcid = (PMCID_RE.search(decoded) or [""])[0].upper()
    pmid_match = PMID_RE.search(decoded)
    doi_match = DOI_RE.search(decoded)
    pii_match = PII_RE.search(decoded)
    doi = doi_match.group(0).rstrip(".,;)") if doi_match else ""
    pii = pii_match.group(0).upper() if pii_match else ""
    if not doi:
        parts = urlsplit(decoded)
        host = parts.netloc.lower().removeprefix("www.")
        slug = parts.path.rstrip("/").rsplit("/", 1)[-1]
        if host == "nature.com" and NATURE_SLUG_RE.fullmatch(slug):
            doi = "10.1038/" + slug.replace("_", "-")
    return {"pmcid": pmcid, "pmid": pmid_match.group(1) if pmid_match else "", "doi": doi, "pii": pii}


def is_malformed_url(url: str) -> bool:
    return bool(MALFORMED_CELL_URL_RE.search(unquote(url)))


def provider_for_identifiers(ids: dict[str, str]) -> str:
    if ids["pmcid"] or ids["pmid"]:
        return "europe-pmc"
    if ids["doi"]:
        return "crossref"
    if ids["pii"]:
        return "elsevier"
    return ""


def select_candidates(
    pending: list[dict[str, str]],
    limit: int,
    scan_limit: int = 0,
    allowed_providers: set[str] | None = None,
) -> tuple[list[tuple[dict[str, str], dict[str, str]]], int, int, int, int]:
    scan_rows = pending[: scan_limit or None]
    candidates: list[tuple[dict[str, str], dict[str, str]]] = []
    skipped_malformed = 0
    skipped_no_identifier = 0
    skipped_provider = 0
    scanned = 0
    for row in scan_rows:
        scanned += 1
        url = row.get("url", "")
        if is_malformed_url(url):
            skipped_malformed += 1
            continue
        ids = identifiers(url)
        if not any(ids.values()):
            skipped_no_identifier += 1
            continue
        if allowed_providers is not None and provider_for_identifiers(ids) not in allowed_providers:
            skipped_provider += 1
            continue
        candidates.append((row, ids))
        if len(candidates) >= limit:
            break
    return candidates, scanned, skipped_malformed, skipped_no_identifier, skipped_provider


def europe_pmc_lookup(id_kind: str, value: str, timeout: float, user_agent: str) -> dict | None:
    query = f"{id_kind}:{value}"
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + "query=" + quote(query, safe=":") + "&resultType=core&pageSize=1&format=json"
    data = request_json(url, timeout, user_agent)
    results = data.get("resultList", {}).get("result", [])
    return results[0] if results else None


def crossref_lookup(doi: str, timeout: float, user_agent: str) -> dict | None:
    url = "https://api.crossref.org/works/" + quote(doi, safe="")
    data = request_json(url, timeout, user_agent)
    return data.get("message") or None


def elsevier_lookup(pii: str, timeout: float, user_agent: str) -> dict | None:
    url = "https://api.elsevier.com/content/article/pii/" + quote(pii, safe="()")
    data = request_json(url, timeout, user_agent)
    return data.get("full-text-retrieval-response") or None


def compact_metadata(source_url: str, ids: dict[str, str], record: dict, provider: str) -> dict:
    if provider == "elsevier":
        core = record.get("coredata", {})
        title = core.get("dc:title", "")
        journal = core.get("prism:publicationName", "")
        doi = core.get("prism:doi", "")
        year = str(core.get("prism:coverDate", ""))[:4]
        return {
            "source_url": source_url,
            "provider": provider,
            "pmcid": ids.get("pmcid", ""),
            "pmid": ids.get("pmid", ""),
            "doi": doi,
            "pii": ids.get("pii", ""),
            "title": title,
            "journal": journal,
            "year": year,
            "publication_type": core.get("prism:aggregationType", ""),
            "abstract_available": bool(core.get("dc:description")),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }
    title = record.get("title") or record.get("title", [""])
    if isinstance(title, list):
        title = title[0] if title else ""
    journal = record.get("journalTitle") or record.get("container-title") or ""
    if isinstance(journal, list):
        journal = journal[0] if journal else ""
    doi = record.get("doi") or ids.get("doi", "")
    return {
        "source_url": source_url,
        "provider": provider,
        "pmcid": record.get("pmcid") or ids.get("pmcid", ""),
        "pmid": str(record.get("pmid") or ids.get("pmid", "")),
        "doi": doi,
        "pii": ids.get("pii", ""),
        "title": title,
        "journal": journal,
        "year": str(record.get("pubYear") or (record.get("published", {}).get("date-parts", [[""]])[0][0] if record.get("published") else "")),
        "publication_type": record.get("pubType") or record.get("type") or "",
        "abstract_available": bool(record.get("abstractText") or record.get("abstract")),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def make_note(metadata: dict) -> str:
    title = metadata.get("title") or "（题名未返回）"
    year = metadata.get("year") or "年份未返回"
    journal = metadata.get("journal") or "期刊未返回"
    identifier = metadata.get("pmcid") or metadata.get("pmid") or metadata.get("doi") or "标识未返回"
    return (
        f"自动书目核验：{identifier}；《{title}》；{journal}；{year}。"
        "仅确认公开来源身份，不自动证明研究设计、疗效、安全性或与 Episode 主张匹配；"
        "研究类型与外推边界需人工核验。"
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ["url", "episode_count", "episode_ids", "episode_title_sample", "verification_status", "evidence_notes"]
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--metadata-output", type=Path)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument(
        "--scan-limit",
        type=int,
        default=0,
        help="maximum pending rows to inspect while finding resolvable identifiers; 0 scans all pending rows",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        choices=PROVIDERS,
        default=list(PROVIDERS),
        help="bibliographic providers to use; restrict this when one provider is rate-limited",
    )
    parser.add_argument(
        "--max-provider-errors",
        type=int,
        default=3,
        help="stop querying a provider for the current run after this many network/API errors",
    )
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--user-agent", default="huberman-perspective-academic-verifier/1.0")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.scan_limit < 0:
        parser.error("--scan-limit cannot be negative")
    if args.max_provider_errors < 1:
        parser.error("--max-provider-errors must be positive")

    output = args.output or args.queue
    metadata_output = args.metadata_output or args.queue.with_name("academic-metadata.jsonl")
    with args.queue.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    pending = [row for row in rows if row.get("verification_status", "pending") == "pending"]
    candidates, scanned, skipped_malformed, skipped_no_identifier, skipped_provider = select_candidates(
        pending, args.limit, args.scan_limit, set(args.providers)
    )

    records: list[dict] = []
    matched = 0
    errors = 0
    provider_errors: dict[str, int] = {}
    skipped_provider_cooldown = 0
    for index, (row, ids) in enumerate(candidates):
        url = row.get("url", "")
        provider_hint = provider_for_identifiers(ids)
        if provider_errors.get(provider_hint, 0) >= args.max_provider_errors:
            skipped_provider_cooldown += 1
            continue
        record = None
        provider = ""
        try:
            if ids["pmcid"]:
                record = europe_pmc_lookup("PMCID", ids["pmcid"], args.timeout, args.user_agent)
                provider = "europe-pmc"
            elif ids["pmid"]:
                record = europe_pmc_lookup("EXT_ID", ids["pmid"], args.timeout, args.user_agent)
                provider = "europe-pmc"
            elif ids["doi"]:
                record = crossref_lookup(ids["doi"], args.timeout, args.user_agent)
                provider = "crossref"
            elif ids["pii"]:
                record = elsevier_lookup(ids["pii"], args.timeout, args.user_agent)
                provider = "elsevier"
        except HTTPError as exc:
            if exc.code in {400, 404}:
                record = None
            else:
                errors += 1
                provider_errors[provider_hint] = provider_errors.get(provider_hint, 0) + 1
                records.append({"source_url": url, "lookup_error": str(exc), "retrieved_at": datetime.now(timezone.utc).isoformat()})
                continue
        except Exception as exc:  # network/API errors should not destroy the queue
            errors += 1
            provider_errors[provider_hint] = provider_errors.get(provider_hint, 0) + 1
            records.append({"source_url": url, "lookup_error": str(exc), "retrieved_at": datetime.now(timezone.utc).isoformat()})
            continue
        if record:
            metadata = compact_metadata(url, ids, record, provider)
            records.append(metadata)
            matched += 1
            if not args.dry_run:
                row["verification_status"] = "verified-bibliographic"
                row["evidence_notes"] = make_note(metadata)
        if index + 1 < len(candidates):
            time.sleep(max(args.delay, 0.0))

    if not args.dry_run:
        write_csv(output, rows)
        metadata_output.parent.mkdir(parents=True, exist_ok=True)
        with metadata_output.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "pending": len(pending),
                "scanned": scanned,
                "candidates": len(candidates),
                "matched": matched,
                "skipped_malformed": skipped_malformed,
                "skipped_no_identifier": skipped_no_identifier,
                "skipped_provider": skipped_provider,
                "skipped_provider_cooldown": skipped_provider_cooldown,
                "provider_errors": provider_errors,
                "errors": errors,
                "dry_run": args.dry_run,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
