#!/usr/bin/env python3
"""Build an auditable Episode-topic-platform-claim-study knowledge graph from JSONL."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunsplit


ACADEMIC_HOSTS = {"doi.org", "pubmed.ncbi.nlm.nih.gov", "nature.com", "sciencedirect.com", "cell.com", "journals.sagepub.com", "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov"}
TRACKING_QUERY_KEYS = {"_returnURL", "rfr_dat", "rfr_id", "url_ver", "via"}


def academic_key(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key not in TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, urlencode(query), ""))


def topic_label(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"[-_]", " ", slug).title()


def resource_kind(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if host in ACADEMIC_HOSTS or host.endswith(".nature.com") or host.endswith(".sciencedirect.com"):
        return "academic-or-medical"
    if "hubermanlab.com" in host or "stanford.edu" in host:
        return "official-or-institutional"
    if "youtube.com" in host or "youtu.be" in host:
        return "video"
    return "other-resource"


def youtube_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/", 1)[0]
    if host in {"youtube.com", "m.youtube.com"}:
        query = dict(pair.split("=", 1) for pair in parsed.query.split("&") if "=" in pair)
        return query.get("v", "")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bilibili", type=Path)
    parser.add_argument("--courses", type=Path)
    parser.add_argument("--claims", type=Path)
    parser.add_argument("--academic", type=Path)
    parser.add_argument("--study-cards", type=Path)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    academic_by_key: dict[str, dict[str, str]] = {}
    if args.academic and args.academic.exists():
        with args.academic.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                url = row.get("url", "").strip()
                if url:
                    academic_by_key[academic_key(url)] = row
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str, str]] = set()
    resources_by_academic_key: dict[str, set[str]] = {}
    topic_counts: Counter[str] = Counter()
    episode_by_url: dict[str, str] = {}
    youtube_by_id: dict[str, str] = {}
    for item in records:
        if not item.get("fetch_ok"):
            continue
        eid = f"episode:{item['episode_id']}"
        episode_by_url[item["url"]] = eid
        nodes[eid] = {
            "id": eid,
            "type": "episode",
            "label": item.get("title", item["episode_id"]),
            "url": item["url"],
            "date_published": item.get("date_published", ""),
            "episode_number": item.get("episode_number", ""),
            "has_show_notes": bool(item.get("show_notes")),
            "has_timestamps": bool(item.get("timestamps")),
        }
        for topic in item.get("topics", []):
            tid = f"topic:{topic}"
            nodes.setdefault(tid, {"id": tid, "type": "topic", "label": topic_label(topic), "url": topic})
            edges.add((eid, "has_topic", tid))
            topic_counts[topic] += 1
        for video in item.get("youtube_urls", []):
            vid = f"youtube:{video}"
            nodes.setdefault(vid, {"id": vid, "type": "youtube", "label": video, "url": video})
            edges.add((eid, "has_video", vid))
            extracted_id = youtube_id(video)
            if extracted_id:
                youtube_by_id[extracted_id] = vid
        for resource in item.get("resource_urls", []):
            rid = f"resource:{resource}"
            resource_node = nodes.setdefault(rid, {"id": rid, "type": "resource", "label": resource, "url": resource, "kind": resource_kind(resource)})
            verification = academic_by_key.get(academic_key(resource))
            if verification:
                resource_node["verification_status"] = verification.get("verification_status", "pending")
                resource_node["evidence_notes"] = verification.get("evidence_notes", "")
                resource_node["academic_episode_count"] = verification.get("episode_count", "")
            resources_by_academic_key.setdefault(academic_key(resource), set()).add(rid)
            edges.add((eid, "cites_resource", rid))

    bilibili_count = 0
    if args.bilibili and args.bilibili.exists():
        with args.bilibili.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                bid = row.get("id", "").strip()
                if not bid:
                    continue
                nid = f"bilibili:{bid}"
                nodes[nid] = {
                    "id": nid,
                    "type": "bilibili",
                    "label": row.get("category", bid),
                    "url": row.get("url", ""),
                    "bv_id": bid,
                    "source_level": row.get("source_level", ""),
                    "status": row.get("status", ""),
                    "uploader": row.get("uploader", ""),
                    "duration": row.get("duration", ""),
                    "subtitle_type": row.get("subtitle_type", ""),
                }
                bilibili_count += 1
                yid = row.get("youtube_id", "").strip()
                if yid and yid in youtube_by_id:
                    edges.add((nid, "maps_to_video", youtube_by_id[yid]))
                official_url = row.get("official_episode_url", "").strip()
                if official_url and official_url in episode_by_url:
                    edges.add((nid, "maps_to_episode", episode_by_url[official_url]))

    course_count = 0
    if args.courses and args.courses.exists():
        with args.courses.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                identity = "|".join(
                    row.get(key, "")
                    for key in ("type", "title", "course_or_event", "date_or_term", "source_url")
                )
                digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
                nid = f"course-lecture:{digest}"
                nodes[nid] = {
                    "id": nid,
                    "type": "course-lecture",
                    "label": row.get("title", ""),
                    "course_or_event": row.get("course_or_event", ""),
                    "date_or_term": row.get("date_or_term", ""),
                    "source_level": row.get("source_level", ""),
                    "url": row.get("source_url", ""),
                    "notes": row.get("notes", ""),
                }
                course_count += 1
    claim_count = 0
    if args.claims and args.claims.exists():
        with args.claims.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                claim = json.loads(line)
                claim_id = claim.get("claim_id", "").strip()
                if not claim_id:
                    continue
                nid = f"claim:{claim_id}"
                nodes[nid] = {
                    "id": nid,
                    "type": "claim",
                    "label": claim.get("claim_text", ""),
                    "record_kind": claim.get("record_kind", ""),
                    "section_number": claim.get("section_number", ""),
                    "section_title": claim.get("section_title", ""),
                    "subsection_title": claim.get("subsection_title", ""),
                    "evidence_layer": claim.get("evidence_layer", ""),
                    "speaker_scope": claim.get("speaker_scope", ""),
                    "boundary": claim.get("boundary", ""),
                    "timestamps": claim.get("timestamps", []),
                    "analysis_source": claim.get("analysis_source", ""),
                    "source_line": claim.get("source_line", ""),
                }
                claim_count += 1
                for video_id in claim.get("youtube_ids", []):
                    video_node = youtube_by_id.get(video_id)
                    if video_node:
                        edges.add((nid, "located_in_video", video_node))
    study_card_count = 0
    study_finding_count = 0
    study_limitation_count = 0
    evidence_topic_count = 0
    if args.study_cards and args.study_cards.exists():
        evidence_topics: set[str] = set()
        with args.study_cards.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                card = json.loads(line)
                review_id = card.get("review_id", "").strip()
                if not review_id:
                    continue
                nid = f"study-card:{review_id}"
                nodes[nid] = {
                    "id": nid,
                    "type": "study-card",
                    "label": card.get("title", review_id),
                    "review_id": review_id,
                    "doi": card.get("doi", ""),
                    "verification_status": card.get("verification_status", ""),
                    "evidence_level": card.get("evidence_level", ""),
                    "study_design": card.get("study_design", ""),
                    "sample_size": card.get("sample_size", ""),
                    "population": card.get("population", ""),
                    "intervention_exposure": card.get("intervention_exposure", ""),
                    "comparator": card.get("comparator", ""),
                    "outcomes": card.get("outcomes", []),
                    "result_summary": card.get("result_summary", ""),
                    "safe_interpretation": card.get("safe_interpretation", ""),
                    "provenance_urls": card.get("provenance_urls", []),
                    "reviewed_at": card.get("reviewed_at", ""),
                }
                study_card_count += 1
                for source_url in card.get("source_urls", []):
                    for resource_node_id in resources_by_academic_key.get(academic_key(source_url), set()):
                        edges.add((nid, "reviews_resource", resource_node_id))
                for tag in card.get("topic_tags", []):
                    normalized_tag = re.sub(r"[^a-z0-9-]+", "-", tag.lower()).strip("-")
                    if not normalized_tag:
                        continue
                    topic_id = f"evidence-topic:{normalized_tag}"
                    nodes.setdefault(topic_id, {"id": topic_id, "type": "evidence-topic", "label": tag})
                    evidence_topics.add(topic_id)
                    edges.add((nid, "has_evidence_topic", topic_id))
                finding_groups = [
                    ("result", [card.get("result_summary", "")], "reports_result"),
                    ("null", card.get("null_findings", []), "reports_null_finding"),
                ]
                for finding_kind, findings, relation in finding_groups:
                    for finding in findings:
                        if not finding:
                            continue
                        digest = hashlib.sha1(f"{review_id}|{finding_kind}|{finding}".encode("utf-8")).hexdigest()[:16]
                        finding_id = f"study-finding:{digest}"
                        nodes[finding_id] = {
                            "id": finding_id,
                            "type": "study-finding",
                            "label": finding,
                            "finding_kind": finding_kind,
                            "review_id": review_id,
                        }
                        study_finding_count += 1
                        edges.add((nid, relation, finding_id))
                for limitation in card.get("limitations", []):
                    if not limitation:
                        continue
                    digest = hashlib.sha1(f"{review_id}|limitation|{limitation}".encode("utf-8")).hexdigest()[:16]
                    limitation_id = f"study-limitation:{digest}"
                    nodes[limitation_id] = {
                        "id": limitation_id,
                        "type": "study-limitation",
                        "label": limitation,
                        "review_id": review_id,
                    }
                    study_limitation_count += 1
                    edges.add((nid, "has_limitation", limitation_id))
        evidence_topic_count = len(evidence_topics)
    graph = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": (
            "episode-topic-platform-claim-study-v4"
            if args.study_cards
            else "episode-topic-platform-claim-v3"
            if args.claims
            else "episode-topic-platform-v2"
        ),
        "stats": {
            "episode_nodes": sum(n["type"] == "episode" for n in nodes.values()),
            "topic_nodes": sum(n["type"] == "topic" for n in nodes.values()),
            "youtube_nodes": sum(n["type"] == "youtube" for n in nodes.values()),
            "bilibili_nodes": sum(n["type"] == "bilibili" for n in nodes.values()),
            "course_lecture_nodes": sum(n["type"] == "course-lecture" for n in nodes.values()),
            "claim_nodes": sum(n["type"] == "claim" for n in nodes.values()),
            "study_card_nodes": study_card_count,
            "study_finding_nodes": study_finding_count,
            "study_limitation_nodes": study_limitation_count,
            "evidence_topic_nodes": evidence_topic_count,
            "resource_nodes": sum(n["type"] == "resource" for n in nodes.values()),
            "academic_resource_nodes": sum(
                n["type"] == "resource" and "verification_status" in n for n in nodes.values()
            ),
            "verified_academic_resource_nodes": sum(
                n.get("verification_status") != "pending"
                for n in nodes.values()
                if n["type"] == "resource" and "verification_status" in n
            ),
            "edges": len(edges),
            "top_topics": [{"url": u, "count": c, "label": topic_label(u)} for u, c in topic_counts.most_common(20)],
        },
        "nodes": sorted(nodes.values(), key=lambda n: (n["type"], n["id"])),
        "edges": [{"source": s, "relation": r, "target": t} for s, r, t in sorted(edges)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(graph["stats"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
