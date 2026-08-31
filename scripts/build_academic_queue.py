#!/usr/bin/env python3
"""Build a deduplicated academic/medical verification queue."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_QUERY_KEYS = {
    "_returnURL",
    "rfr_dat",
    "rfr_id",
    "url_ver",
    "via",
}


def state_score(row: dict[str, str]) -> int:
    """Prefer verified state, then an explicit data-quality note, over blank pending state."""
    if row.get("verification_status", "pending") != "pending":
        return 2
    if row.get("evidence_notes", "").strip():
        return 1
    return 0


def normalized_url(url: str) -> str:
    """Remove publisher/referrer query noise while retaining meaningful parameters."""
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key not in TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    existing: dict[str, dict[str, str]] = {}
    existing_normalized: dict[str, dict[str, str]] = {}
    if args.output.exists():
        with args.output.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                url = row.get("url", "").strip()
                if url:
                    existing[url] = row
                    key = normalized_url(url)
                    current = existing_normalized.get(key)
                    if current is None or state_score(row) > state_score(current):
                        existing_normalized[key] = row
    grouped: dict[str, dict] = {}
    episodes: defaultdict[str, set[str]] = defaultdict(set)
    titles: dict[str, str] = {}
    with args.input.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("kind") != "academic-or-medical":
                continue
            url = row.get("url", "").strip()
            if not url:
                continue
            grouped.setdefault(url, {"url": url})
            episodes[url].add(row.get("episode_id", ""))
            titles[url] = row.get("episode_title", "")
    rows = []
    preserved = 0
    for url, data in grouped.items():
        candidates = [existing.get(url), existing_normalized.get(normalized_url(url))]
        prior = max((row for row in candidates if row), key=state_score, default={})
        status = prior.get("verification_status", "pending")
        notes = prior.get("evidence_notes", "")
        if status != "pending" or notes:
            preserved += 1
        rows.append({
            "url": url,
            "episode_count": str(len(episodes[url])),
            "episode_ids": ";".join(sorted(episodes[url])),
            "episode_title_sample": titles.get(url, ""),
            "verification_status": status,
            "evidence_notes": notes,
        })
    rows.sort(key=lambda r: (-int(r["episode_count"]), r["url"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fields = ["url", "episode_count", "episode_ids", "episode_title_sample", "verification_status", "evidence_notes"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} unique academic/medical URLs; preserved {preserved} existing verification records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
