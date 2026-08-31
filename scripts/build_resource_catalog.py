#!/usr/bin/env python3
"""Flatten Show Notes resource links into a deduplicated, auditable CSV."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
try:
    from resource_classification import classify_resource
except ModuleNotFoundError:  # pragma: no cover - import path used by module-based tests
    from scripts.resource_classification import classify_resource


def kind(url: str) -> str:
    return classify_resource(url)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    seen = set()
    for item in records:
        for url in item.get("resource_urls", []):
            key = (item.get("episode_id", ""), url)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "episode_id": item.get("episode_id", ""),
                "episode_title": item.get("title", ""),
                "kind": kind(url),
                "url": url,
                "source_episode_url": item.get("url", ""),
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fields = ["episode_id", "episode_title", "kind", "url", "source_episode_url"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["kind"], r["episode_id"], r["url"])))
    by_kind = {}
    for row in rows:
        by_kind[row["kind"]] = by_kind.get(row["kind"], 0) + 1
    print(json.dumps({"rows": len(rows), "by_kind": by_kind}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
