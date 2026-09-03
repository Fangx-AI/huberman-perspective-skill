#!/usr/bin/env python3
"""Build a conservative, timestamp-oriented claim index from batch analysis Markdown."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


YOUTUBE_ID_RE = re.compile(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])")
YOUTUBE_URL_RE = re.compile(r"https?://(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{11})")
SOURCE_URL_RE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|hubermanlab\.com)/[^\s)]+")
TIMESTAMP_RE = re.compile(r"(?<![\w])\d{1,2}:\d{2}(?::\d{2})?(?![\w])")
SECTION_RE = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.*)$")

BOUNDARY_MARKERS = (
    "不能",
    "不应",
    "不作",
    "不等于",
    "不替代",
    "必须",
    "需",
    "仍需",
    "转介",
    "待核查",
)
FRAMEWORK_MARKERS = (
    "可复用",
    "可升级为稳定框架",
    "支持",
    "强化",
    "框架",
    "拆成",
    "拆分",
    "区分",
    "组织成",
)


def load_official_ids(queue_path: Path) -> set[str]:
    with queue_path.open(encoding="utf-8-sig", newline="") as handle:
        return {row["youtube_id"].strip() for row in csv.DictReader(handle) if row.get("youtube_id", "").strip()}


def load_statuses(queue_path: Path) -> dict[str, str]:
    with queue_path.open(encoding="utf-8-sig", newline="") as handle:
        return {
            row["youtube_id"].strip(): row.get("analysis_status", "")
            for row in csv.DictReader(handle)
            if row.get("youtube_id", "").strip()
        }


def evidence_layer(text: str) -> str:
    if text.startswith("证据边界") or "待核查" in text:
        return "boundary-rule"
    if any(marker in text for marker in FRAMEWORK_MARKERS):
        return "framework-synthesis"
    return "podcast-claim"


def speaker_scope(text: str) -> str:
    if "嘉宾观点" in text or "嘉宾经验" in text:
        return "guest-or-mixed"
    if "访谈" in text or "由" in text and "讨论" in text:
        return "guest-or-mixed"
    return "Huberman-or-mixed"


def boundary_text(text: str) -> str:
    parts = [part.strip() for part in re.split(r"[。；]", text) if part.strip()]
    selected = [part for part in parts if any(marker in part for marker in BOUNDARY_MARKERS)]
    return "；".join(selected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    valid_ids = load_official_ids(args.queue)
    statuses = load_statuses(args.queue)
    section_number = ""
    section_title = ""
    subsection_title = ""
    records: list[dict] = []

    for line_number, raw_line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        section_match = SECTION_RE.match(line)
        if section_match:
            section_number, section_title = section_match.groups()
            subsection_title = ""
            continue
        if line.startswith("### "):
            subsection_title = line[4:].strip()
            continue
        if not line.startswith("- "):
            continue

        claim_text = line[2:].strip()
        url_ids = YOUTUBE_URL_RE.findall(claim_text)
        ids = [video_id for video_id in url_ids if video_id in valid_ids]
        for video_id in YOUTUBE_ID_RE.findall(claim_text):
            if video_id in valid_ids and video_id not in ids:
                ids.append(video_id)
        if not ids:
            continue

        timestamps = []
        for timestamp in TIMESTAMP_RE.findall(claim_text):
            if timestamp not in timestamps:
                timestamps.append(timestamp)
        source_urls = []
        for source_url in SOURCE_URL_RE.findall(claim_text):
            if source_url not in source_urls:
                source_urls.append(source_url)
        if "不可访问视频处理" in claim_text:
            kind = "provenance-note"
        elif claim_text.startswith("视频："):
            kind = "source-location"
        else:
            kind = "topic-synthesis"
        records.append(
            {
                "claim_id": f"batch02-claim-{len(records) + 1:04d}",
                "record_kind": kind,
                "section_number": section_number,
                "section_title": section_title,
                "subsection_title": subsection_title,
                "claim_text": claim_text,
                "youtube_ids": ids,
                "youtube_statuses": {video_id: statuses.get(video_id, "unknown") for video_id in ids},
                "source_urls": source_urls or [f"https://www.youtube.com/watch?v={video_id}" for video_id in ids],
                "timestamps": timestamps,
                "evidence_layer": evidence_layer(claim_text),
                "speaker_scope": speaker_scope(claim_text),
                "boundary": boundary_text(claim_text),
                "analysis_source": "references/research/batch-02-transcript-analysis.md",
                "source_basis": "公开字幕/章节的批次级分析摘要；不是完整转录，不作为逐字引文",
                "source_line": line_number,
                "parse_quality": "explicit-video-and-timestamp" if timestamps else "explicit-video-no-timestamp",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"claims": len(records), "with_timestamps": sum(bool(r["timestamps"]) for r in records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
