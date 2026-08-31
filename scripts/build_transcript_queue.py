#!/usr/bin/env python3
"""Create a resumable YouTube transcript-analysis queue from Episode pages."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


SEED_ANALYZED = {
    "yb5zpo5WDG4", "nm1TxQj9IsQ", "ddq8JIMhz7c", "t1F7EEGPQwo", "ntfcfJ28eiU"
}
HIGH_PRIORITY = re.compile(r"sleep|focus|attention|learning|memory|goal|motivation|stress|anxiety|exercise|nutrition|supplement|brain|neuroplastic|睡眠|专注|学习|记忆|目标|压力|运动|营养", re.I)


def video_id(url: str) -> str:
    if "v=" in url:
        return url.split("v=", 1)[1].split("&", 1)[0]
    return url.rstrip("/").rsplit("/", 1)[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    prior_by_episode: dict[str, dict[str, str]] = {}
    prior_by_video: dict[str, dict[str, str]] = {}
    if args.output.exists():
        with args.output.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("episode_id"):
                    prior_by_episode[row["episode_id"]] = row
                if row.get("youtube_id"):
                    prior_by_video[row["youtube_id"]] = row
    rows = []
    for item in records:
        urls = item.get("youtube_urls", [])
        if not urls:
            continue
        url = urls[0]
        text = " ".join([item.get("title", ""), item.get("show_notes", ""), item.get("timestamps", "")])
        ident = video_id(url)
        old = prior_by_episode.get(item.get("episode_id", "")) or prior_by_video.get(ident, {})
        same_video = old.get("youtube_id") == ident
        default_status = "seed-analyzed" if ident in SEED_ANALYZED else "pending"
        rows.append({
            "episode_id": item.get("episode_id", ""),
            "episode_number": item.get("episode_number", ""),
            "title": item.get("title", ""),
            "date_published": item.get("date_published", ""),
            "youtube_id": ident,
            "youtube_url": url,
            "priority": "high" if HIGH_PRIORITY.search(text) else "normal",
            "transcript_status": old.get("transcript_status", default_status) if same_video else default_status,
            "analysis_status": old.get("analysis_status", default_status) if same_video else default_status,
            "notes_status": old.get("notes_status", "available" if item.get("show_notes") else "missing") if same_video else ("available" if item.get("show_notes") else "missing"),
            "timestamp_status": old.get("timestamp_status", "available" if item.get("timestamps") else "missing") if same_video else ("available" if item.get("timestamps") else "missing"),
            "caption_provenance": old.get("caption_provenance", "") if same_video else "",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fields = list(rows[0]) if rows else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["priority"] != "high", r["date_published"], r["episode_id"])))
    print(f"wrote {len(rows)} queue rows; seed_analyzed={sum(r['analysis_status']=='seed-analyzed' for r in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
