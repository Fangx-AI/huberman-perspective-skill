#!/usr/bin/env python3
"""Build a deterministic repair queue for unresolved academic source URLs."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urlsplit

try:
    from .verify_academic_batch import (
        identifiers,
        is_malformed_url,
        load_identifier_overrides,
        provider_for_identifiers,
    )
except ImportError:  # direct script execution
    from verify_academic_batch import (
        identifiers,
        is_malformed_url,
        load_identifier_overrides,
        provider_for_identifiers,
    )


FIELDS = [
    "url",
    "episode_count",
    "episode_ids",
    "episode_title_sample",
    "repair_class",
    "parsed_provider",
    "parsed_identifier",
    "next_action",
]


def primary_identifier(ids: dict[str, str]) -> str:
    for key in ("pmcid", "pmid", "doi", "pii"):
        if ids.get(key):
            return f"{key}:{ids[key]}"
    return ""


def classify(url: str, overrides: dict[str, dict[str, str]] | None = None) -> tuple[str, str, str, str]:
    ids = identifiers(url, overrides)
    provider = provider_for_identifiers(ids)
    identifier = primary_identifier(ids)
    if is_malformed_url(url):
        return (
            "malformed-url",
            "",
            "",
            "Repair only from the official Episode resource link or publisher record; do not infer the missing suffix.",
        )
    if provider == "elsevier":
        return (
            "elsevier-unresolved",
            provider,
            identifier,
            "Retry a small provider batch after cooldown; if unresolved, inspect official citation metadata or another verified index without guessing a DOI.",
        )
    if provider == "crossref":
        return (
            "doi-unresolved",
            provider,
            identifier,
            "Inspect the official article citation and add a provenance-bearing override only if the canonical DOI differs.",
        )
    if provider == "europe-pmc":
        return (
            "pmc-unresolved",
            provider,
            identifier,
            "Cross-check the official NCBI record and correct the identifier only with traceable provenance.",
        )

    parts = urlsplit(url)
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.lower()
    if host == "pubmed.ncbi.nlm.nih.gov" and (not path.strip("/") or parts.query):
        return (
            "nonspecific-search-page",
            "",
            "",
            "Do not treat a database search page as a paper; identify a specific source from the official Episode context.",
        )
    if host == "ncbi.nlm.nih.gov" and "/books/" in path:
        return (
            "reference-work",
            "",
            "",
            "Review as a background reference work, not an original study; record edition and chapter provenance if retained.",
        )
    if host in {"cell.com", "sciencedirect.com"} and ("/topics/" in path or "/author/" in path):
        return (
            "nonspecific-publisher-page",
            "",
            "",
            "Keep only as background context or replace with a specific cited paper from the official Episode resource context.",
        )
    return (
        "missing-identifier",
        "",
        "",
        "Inspect official citation metadata and add a traceable identifier override; do not infer from title similarity alone.",
    )


def build_rows(queue_rows: list[dict[str, str]], overrides: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in queue_rows:
        if row.get("verification_status", "pending") != "pending":
            continue
        repair_class, provider, identifier, next_action = classify(row.get("url", ""), overrides)
        output.append(
            {
                "url": row.get("url", ""),
                "episode_count": row.get("episode_count", ""),
                "episode_ids": row.get("episode_ids", ""),
                "episode_title_sample": row.get("episode_title_sample", ""),
                "repair_class": repair_class,
                "parsed_provider": provider,
                "parsed_identifier": identifier,
                "next_action": next_action,
            }
        )
    output.sort(key=lambda row: (row["repair_class"], -int(row["episode_count"] or 0), row["url"]))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overrides", type=Path)
    args = parser.parse_args()

    with args.queue.open(encoding="utf-8-sig", newline="") as handle:
        queue_rows = list(csv.DictReader(handle))
    overrides_path = args.overrides or args.queue.with_name("academic-identifier-overrides.csv")
    rows = build_rows(queue_rows, load_identifier_overrides(overrides_path))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["repair_class"]] = counts.get(row["repair_class"], 0) + 1
    print({"rows": len(rows), "classes": counts})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
