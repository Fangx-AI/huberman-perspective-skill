from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_episodes(source: Path, output: Path) -> int:
    fields = [
        "episode_id",
        "title",
        "url",
        "date_published",
        "episode_number",
        "duration",
        "topic_urls",
        "youtube_urls",
        "has_show_notes",
        "has_timestamps",
        "fetch_ok",
    ]
    rows = []
    for record in load_jsonl(source):
        rows.append(
            {
                "episode_id": record.get("episode_id", ""),
                "title": record.get("title", ""),
                "url": record.get("url", ""),
                "date_published": record.get("date_published", ""),
                "episode_number": record.get("episode_number", ""),
                "duration": record.get("duration", ""),
                "topic_urls": ";".join(record.get("topics") or []),
                "youtube_urls": ";".join(record.get("youtube_urls") or []),
                "has_show_notes": bool(record.get("show_notes")),
                "has_timestamps": bool(record.get("timestamps")),
                "fetch_ok": bool(record.get("fetch_ok")),
            }
        )
    rows.sort(key=lambda row: row["episode_id"])
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def export_claims(source: Path, output: Path) -> int:
    records = []
    for record in load_jsonl(source):
        records.append(
            {
                "boundary": record.get("boundary", ""),
                "claim_id": record["claim_id"],
                "evidence_layer": record.get("evidence_layer", ""),
                "parse_quality": record.get("parse_quality", ""),
                "record_kind": record.get("record_kind", ""),
                "source_basis": "Public source locator only; no transcript or verbatim claim text is distributed.",
                "source_urls": record.get("source_urls") or [],
                "speaker_scope": record.get("speaker_scope", ""),
                "timestamps": record.get("timestamps") or [],
                "topic": record.get("subsection_title") or record.get("section_title") or record["claim_id"],
                "youtube_ids": record.get("youtube_ids") or [],
            }
        )
    records.sort(key=lambda item: item["claim_id"])
    write_jsonl(output, records)
    return len(records)


def export_video_urls(source: Path, output: Path) -> int:
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        source_url = row.get("source_url", "")
        if ":\\" in source_url or source_url.startswith("/"):
            row["source_url"] = "references/catalog/bilibili-discovery.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def export_graph(source: Path, output: Path) -> dict:
    graph = json.loads(source.read_text(encoding="utf-8"))
    nodes = []
    for node in graph.get("nodes", []):
        if node.get("type") == "claim":
            nodes.append(
                {
                    "boundary": node.get("boundary", ""),
                    "evidence_layer": node.get("evidence_layer", ""),
                    "id": node["id"],
                    "label": node.get("subsection_title") or node["id"].removeprefix("claim:"),
                    "record_kind": node.get("record_kind", ""),
                    "speaker_scope": node.get("speaker_scope", ""),
                    "timestamps": node.get("timestamps") or [],
                    "type": "claim",
                }
            )
        elif node.get("type") == "course-lecture":
            nodes.append({key: value for key, value in node.items() if key != "notes"})
        else:
            nodes.append(node)
    public_graph = {
        "edges": graph.get("edges", []),
        "generated_at": graph.get("generated_at"),
        "nodes": nodes,
        "schema": "public-evidence-v2",
        "stats": graph.get("stats", {}),
    }
    output.write_text(
        json.dumps(public_graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return public_graph.get("stats", {})


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a deterministic, copyright-minimized public snapshot.")
    parser.add_argument("--source", required=True, type=Path, help="Local full Skill root containing private raw catalogs")
    parser.add_argument("--destination", default=Path(__file__).parents[1], type=Path, help="Public repository root")
    args = parser.parse_args()

    source_catalog = args.source.resolve() / "references" / "catalog"
    destination = args.destination.resolve()
    output_catalog = destination / "references" / "catalog"
    output_catalog.mkdir(parents=True, exist_ok=True)

    episode_count = export_episodes(source_catalog / "episode-pages.jsonl", output_catalog / "episodes.csv")
    claim_count = export_claims(source_catalog / "claim-index.jsonl", output_catalog / "claim-index.jsonl")
    action_playbooks = sorted(
        load_jsonl(source_catalog / "action-playbooks.jsonl"),
        key=lambda item: item["playbook_id"],
    )
    write_jsonl(output_catalog / "action-playbooks.jsonl", action_playbooks)
    video_url_count = export_video_urls(source_catalog / "video-urls.csv", output_catalog / "video-urls.csv")
    stats = export_graph(source_catalog / "knowledge-graph.json", output_catalog / "knowledge-graph.json")

    exported = ["episodes.csv", "claim-index.jsonl", "action-playbooks.jsonl", "knowledge-graph.json", "video-urls.csv"]
    manifest = {
        "counts": {"action_playbooks": len(action_playbooks), "claims": claim_count, "episodes": episode_count, "video_urls": video_url_count, **stats},
        "generated_at": json.loads((output_catalog / "knowledge-graph.json").read_text(encoding="utf-8"))["generated_at"],
        "raw_payloads_included": False,
        "schema": "public-release-manifest-v1",
        "sha256": {name: sha256(output_catalog / name) for name in exported},
    }
    (output_catalog / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
