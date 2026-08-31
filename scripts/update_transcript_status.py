#!/usr/bin/env python3
"""Update the transcript queue from a baoyu-youtube-transcript cache."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument(
        "--analyzed-ids",
        type=Path,
        help="Optional newline-delimited YouTube IDs that have been manually analyzed.",
    )
    return parser.parse_args()


def load_analyzed_ids(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def caption_label(meta: dict) -> str:
    language = meta.get("language") or {}
    code = language.get("code", "unknown")
    kind = "auto" if language.get("isGenerated") else "manual"
    return f"{code}:{kind}"


def main() -> int:
    args = parse_args()
    analyzed_ids = load_analyzed_ids(args.analyzed_ids)

    with args.queue.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0]) if rows else []

    by_video_id = {row.get("youtube_id", ""): row for row in rows}
    updated: list[tuple[str, str]] = []
    unmatched: list[str] = []

    for meta_path in sorted(args.cache.glob("*/meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        video_id = meta.get("videoId")
        if not video_id or video_id not in by_video_id:
            unmatched.append(str(meta_path.parent))
            continue
        transcript_path = meta_path.parent / "transcript.md"
        row = by_video_id[video_id]
        if transcript_path.exists() and transcript_path.stat().st_size > 0:
            row["transcript_status"] = "downloaded"
            row["analysis_status"] = "analyzed" if video_id in analyzed_ids else "pending"
            row["timestamp_status"] = "available" if meta.get("chapters") else row.get("timestamp_status", "pending")
            row["caption_provenance"] = caption_label(meta)
            updated.append((video_id, row["transcript_status"]))

    if "caption_provenance" not in fieldnames:
        fieldnames.append("caption_provenance")
    with args.queue.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({"updated": updated, "updated_count": len(updated), "unmatched_cache_dirs": unmatched}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
