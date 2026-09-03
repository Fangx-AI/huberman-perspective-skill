#!/usr/bin/env python3
"""Contract-level QA for the Huberman perspective Skill and its catalogs."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

try:
    from validate_action_playbooks import load_jsonl, validate_playbooks
except ModuleNotFoundError:  # pragma: no cover
    from scripts.validate_action_playbooks import load_jsonl, validate_playbooks


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def youtube_id(url: str) -> str:
    parsed = urlsplit(url)
    host = parsed.netloc.lower().removeprefix("www.")
    if host == "youtu.be":
        return parsed.path.strip("/").split("/", 1)[0]
    if host in {"youtube.com", "m.youtube.com"}:
        return parse_qs(parsed.query).get("v", [""])[0]
    return ""


def main() -> int:
    failures: list[str] = []
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

    for phrase in (
        "帮助用户过得更好",
        "即使用户没有提到 Huberman",
        "不冒充 Andrew Huberman",
        "Huberman 明确说过",
        "基于框架的推断",
        "一次只问一个问题",
        "默认不超过三个动作",
        "B 站搬运与原视频只算一条主张证据",
        "不能诊断、开药",
        "药物相互作用",
        "付费转录内容不绕过访问控制",
    ):
        require(phrase in skill, f"SKILL.md missing contract phrase: {phrase}", failures)

    transcript_path = ROOT / "references/catalog/youtube-transcript-queue.csv"
    with transcript_path.open(encoding="utf-8-sig", newline="") as handle:
        transcript_rows = list(csv.DictReader(handle))
    transcript_ids = [row["youtube_id"] for row in transcript_rows]
    transcript_status = Counter(row["analysis_status"] for row in transcript_rows)
    require(len(transcript_rows) == 424, "YouTube queue row count is not 424", failures)
    require(len(set(transcript_ids)) == len(transcript_ids), "YouTube queue IDs are duplicated", failures)
    require(not transcript_status.get("pending"), "YouTube queue still has pending analysis", failures)
    require(transcript_status.get("analyzed", 0) >= 400, "Too few analyzed YouTube entries", failures)

    academic_path = ROOT / "references/catalog/academic-verification-queue.csv"
    with academic_path.open(encoding="utf-8-sig", newline="") as handle:
        academic_reader = csv.DictReader(handle)
        academic_rows = list(academic_reader)
        academic_fields = academic_reader.fieldnames or []
    require(
        academic_fields
        == [
            "url",
            "episode_count",
            "episode_ids",
            "episode_title_sample",
            "verification_status",
            "evidence_notes",
        ],
        "Academic queue schema changed",
        failures,
    )
    require(len(academic_rows) == 1736, "Academic queue row count is not 1736", failures)
    allowed_statuses = {
        "pending",
        "verified-study",
        "verified-review",
        "verified-nonresearch",
        "verified-observational",
        "verified-bibliographic",
    }
    require(
        all(row["verification_status"] in allowed_statuses for row in academic_rows),
        "Academic queue contains an unknown verification status",
        failures,
    )
    require(
        sum(row["verification_status"] != "pending" for row in academic_rows) >= 20,
        "Academic queue has too few verified records",
        failures,
    )
    malformed_academic = [
        row
        for row in academic_rows
        if row["url"].endswith("(21") or row["url"].endswith("(22") or "2030532-8" in row["url"]
    ]
    require(
        all(row["verification_status"] == "pending" for row in malformed_academic),
        "Malformed academic links must remain pending for repair-queue classification",
        failures,
    )

    study_cards_path = ROOT / "references/catalog/academic-study-cards.jsonl"
    try:
        with study_cards_path.open(encoding="utf-8") as handle:
            study_cards = [json.loads(line) for line in handle if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        study_cards = []
        failures.append(f"Academic study cards cannot be loaded: {exc}")
    required_study_card_fields = {
        "review_id",
        "source_urls",
        "provenance_urls",
        "verification_status",
        "study_design",
        "sample_size",
        "population",
        "outcomes",
        "result_summary",
        "null_findings",
        "limitations",
        "safe_interpretation",
        "queue_note",
    }
    require(len(study_cards) >= 4, "Academic study-card catalog has too few records", failures)
    require(
        all(required_study_card_fields <= set(card) for card in study_cards),
        "Academic study cards have an incomplete schema",
        failures,
    )
    require(
        len({card.get("review_id") for card in study_cards}) == len(study_cards),
        "Academic study-card review IDs are duplicated",
        failures,
    )
    academic_by_url = {row["url"]: row for row in academic_rows}
    require(
        all(
            url in academic_by_url
            and academic_by_url[url]["verification_status"] == card.get("verification_status")
            and academic_by_url[url]["evidence_notes"] == card.get("queue_note")
            for card in study_cards
            for url in card.get("queue_urls", card.get("source_urls", []))
        ),
        "Academic study cards and verification queue have drifted",
        failures,
    )
    require(
        all(
            card.get("null_findings")
            and card.get("limitations")
            and card.get("safe_interpretation")
            and all(url.startswith("https://") for url in card.get("provenance_urls", []))
            for card in study_cards
        ),
        "Academic study cards lack negative findings, limitations, safe interpretation, or HTTPS provenance",
        failures,
    )

    bilibili_path = ROOT / "references/catalog/bilibili-discovery.csv"
    with bilibili_path.open(encoding="utf-8-sig", newline="") as handle:
        bilibili_reader = csv.DictReader(handle)
        bilibili_rows = list(bilibili_reader)
        bilibili_fields = bilibili_reader.fieldnames or []
    require(
        bilibili_fields
        == [
            "platform",
            "id",
            "category",
            "source_level",
            "status",
            "url",
            "notes",
            "youtube_id",
            "official_episode_url",
            "uploader",
            "duration",
            "subtitle_type",
        ],
        "Bilibili discovery schema changed",
        failures,
    )
    require(len(bilibili_rows) >= 2, "Bilibili discovery catalog is empty", failures)
    bilibili_ids = [row["id"] for row in bilibili_rows]
    require(len(set(bilibili_ids)) == len(bilibili_ids), "Bilibili BV IDs are duplicated", failures)
    require(
        sum(bool(row["youtube_id"] and row["official_episode_url"]) for row in bilibili_rows) >= 2,
        "Bilibili catalog has too few confirmed links to original YouTube/Episode sources",
        failures,
    )
    episode_pages_path = ROOT / "references/catalog/episode-pages.jsonl"
    official_youtube_to_episode: dict[str, str] = {}
    official_episode_urls: set[str] = set()
    with episode_pages_path.open(encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            episode_url = item.get("url", "")
            if not episode_url:
                continue
            official_episode_urls.add(episode_url)
            for video_url in item.get("youtube_urls", []):
                video_id = youtube_id(video_url)
                if video_id:
                    official_youtube_to_episode[video_id] = episode_url
    mapped_bilibili = [row for row in bilibili_rows if row["youtube_id"] and row["official_episode_url"]]
    require(
        all(
            row["official_episode_url"] in official_episode_urls
            and official_youtube_to_episode.get(row["youtube_id"]) == row["official_episode_url"]
            for row in mapped_bilibili
        ),
        "Bilibili mappings do not resolve to the same official Episode/YouTube pair",
        failures,
    )

    course_path = ROOT / "references/catalog/courses-lectures.csv"
    with course_path.open(encoding="utf-8-sig", newline="") as handle:
        course_reader = csv.DictReader(handle)
        course_rows = list(course_reader)
        course_fields = course_reader.fieldnames or []
    require(
        course_fields
        == [
            "type",
            "title",
            "course_or_event",
            "date_or_term",
            "source_level",
            "source_url",
            "notes",
        ],
        "Course/lecture catalog schema changed",
        failures,
    )
    require(len(course_rows) >= 6, "Course/lecture catalog has too few institutional entries", failures)
    require(
        all(row["source_url"].startswith("https://") and row["notes"] for row in course_rows),
        "Course/lecture catalog contains incomplete provenance or notes",
        failures,
    )

    claim_path = ROOT / "references/catalog/claim-index.jsonl"
    claim_rows = []
    try:
        with claim_path.open(encoding="utf-8") as handle:
            claim_rows = [json.loads(line) for line in handle if line.strip()]
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"Claim index cannot be loaded: {exc}")
    require(len(claim_rows) >= 20, "Claim index has too few source-grounded records", failures)
    claim_ids = [row.get("claim_id", "") for row in claim_rows]
    require(all(claim_ids), "Claim index contains an empty claim_id", failures)
    require(len(set(claim_ids)) == len(claim_ids), "Claim index claim_ids are duplicated", failures)
    require(all(row.get("claim_text", "").strip() for row in claim_rows), "Claim index contains an empty claim_text", failures)
    require(
        all(isinstance(row.get("source_line"), int) and row["source_line"] > 0 for row in claim_rows),
        "Claim index contains an invalid source_line",
        failures,
    )
    require(
        all(row.get("record_kind") in {"source-location", "topic-synthesis", "provenance-note"} for row in claim_rows),
        "Claim index contains an unknown record kind",
        failures,
    )
    allowed_claim_layers = {"podcast-claim", "framework-synthesis", "boundary-rule"}
    require(
        all(row.get("evidence_layer") in allowed_claim_layers for row in claim_rows),
        "Claim index contains an unknown evidence layer",
        failures,
    )
    require(
        all(
            row.get("analysis_source") == "references/research/batch-02-transcript-analysis.md"
            and row.get("youtube_ids")
            and row.get("source_urls")
            and all(url.startswith("https://") for url in row.get("source_urls", []))
            and set(row.get("youtube_statuses", {})) == set(row.get("youtube_ids", []))
            and all(
                any(youtube_id(url) == video_id for url in row.get("source_urls", []))
                for video_id in row.get("youtube_ids", [])
            )
            for row in claim_rows
        ),
        "Claim index has incomplete provenance or source alignment",
        failures,
    )
    require(
        all(
            all(re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) for video_id in row.get("youtube_ids", []))
            for row in claim_rows
        ),
        "Claim index contains an invalid YouTube ID",
        failures,
    )
    require(
        all(
            all(re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", timestamp) for timestamp in row.get("timestamps", []))
            for row in claim_rows
        ),
        "Claim index contains an invalid timestamp",
        failures,
    )

    action_playbooks_path = ROOT / "references/catalog/action-playbooks.jsonl"
    try:
        action_playbooks = load_jsonl(action_playbooks_path)
        validate_playbooks(action_playbooks, study_cards, claim_rows)
    except (OSError, ValueError) as exc:
        action_playbooks = []
        failures.append(f"Action playbooks cannot be loaded or validated: {exc}")
    require(len(action_playbooks) == 13, "Action playbook catalog must contain thirteen reviewed playbooks", failures)

    graph_path = ROOT / "references/catalog/knowledge-graph.json"
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        graph = {}
        failures.append(f"Knowledge graph cannot be loaded: {exc}")
    require(
        graph.get("schema") == "episode-topic-platform-claim-study-relation-action-v6",
        "Knowledge graph schema is not claim-study-relation-action v6",
        failures,
    )
    graph_stats = graph.get("stats", {})
    require(graph_stats.get("bilibili_nodes") == len(bilibili_rows), "Knowledge graph Bilibili count is stale", failures)
    require(
        graph_stats.get("course_lecture_nodes") == len(course_rows),
        "Knowledge graph course/lecture count is stale",
        failures,
    )
    require(any(node.get("type") == "bilibili" for node in graph.get("nodes", [])), "Knowledge graph has no Bilibili nodes", failures)
    require(
        any(node.get("type") == "course-lecture" for node in graph.get("nodes", [])),
        "Knowledge graph has no course/lecture nodes",
        failures,
    )
    academic_resource_nodes = [
        node for node in graph.get("nodes", [])
        if node.get("type") == "resource" and "verification_status" in node
    ]
    require(
        len(academic_resource_nodes) >= 100,
        "Knowledge graph does not propagate academic verification metadata",
        failures,
    )
    require(
        sum(node.get("verification_status") != "pending" for node in academic_resource_nodes) >= 20,
        "Knowledge graph has too few verified academic resource nodes",
        failures,
    )
    require(graph_stats.get("claim_nodes") == len(claim_rows), "Knowledge graph claim count is stale", failures)
    require(any(node.get("type") == "claim" for node in graph.get("nodes", [])), "Knowledge graph has no claim nodes", failures)
    claim_video_edges = sum(edge.get("relation") == "located_in_video" for edge in graph.get("edges", []))
    source_grounded_claims = sum(
        any(video_id in official_youtube_to_episode for video_id in row.get("youtube_ids", []))
        for row in claim_rows
    )
    require(
        claim_video_edges >= source_grounded_claims,
        "Knowledge graph is missing claim-to-video provenance edges",
        failures,
    )
    require(
        graph_stats.get("study_card_nodes") == len(study_cards),
        "Knowledge graph study-card count is stale",
        failures,
    )
    require(
        graph_stats.get("study_finding_nodes")
        == sum(1 + len(card.get("null_findings", [])) for card in study_cards),
        "Knowledge graph study-finding count is stale",
        failures,
    )
    require(
        graph_stats.get("study_limitation_nodes")
        == sum(len(card.get("limitations", [])) for card in study_cards),
        "Knowledge graph study-limitation count is stale",
        failures,
    )
    graph_relations = Counter(edge.get("relation") for edge in graph.get("edges", []))
    action_steps = sum(len(playbook.get("actions", [])) for playbook in action_playbooks)
    require(graph_stats.get("action_playbook_nodes") == len(action_playbooks), "Knowledge graph action-playbook count is stale", failures)
    require(graph_stats.get("action_step_nodes") == action_steps, "Knowledge graph action-step count is stale", failures)
    require(graph_relations["has_action"] == action_steps, "Knowledge graph action-step links are stale", failures)
    require(
        graph_relations["uses_study_evidence"] == sum(len(item.get("evidence_links", [])) for item in action_playbooks),
        "Knowledge graph action-to-study links are stale",
        failures,
    )
    require(
        graph_relations["uses_claim_context"] == sum(len(item.get("claim_links", [])) for item in action_playbooks),
        "Knowledge graph action-to-claim links are stale",
        failures,
    )
    require(
        graph_relations["grounded_in"]
        == sum(len(action.get("evidence_refs", [])) for item in action_playbooks for action in item.get("actions", [])),
        "Knowledge graph action grounding links are stale",
        failures,
    )
    require(
        graph_relations["reviews_resource"] >= len(study_cards),
        "Knowledge graph is missing study-card-to-resource provenance edges",
        failures,
    )
    require(
        graph_relations["reports_null_finding"]
        == sum(len(card.get("null_findings", [])) for card in study_cards),
        "Knowledge graph does not preserve every structured null finding",
        failures,
    )
    require(
        graph_relations["has_limitation"]
        == sum(len(card.get("limitations", [])) for card in study_cards),
        "Knowledge graph does not preserve every structured limitation",
        failures,
    )

    queue_builder = (ROOT / "scripts/build_academic_queue.py").read_text(encoding="utf-8")
    require(
        "existing_normalized" in queue_builder and "preserved" in queue_builder,
        "Academic queue builder does not preserve prior verification state",
        failures,
    )
    verifier = (ROOT / "scripts/verify_academic_batch.py").read_text(encoding="utf-8")
    require(
        "verified-bibliographic" in verifier and "--dry-run" in verifier and "academic-metadata.jsonl" in verifier,
        "Incremental academic verifier is missing conservative dry-run or metadata behavior",
        failures,
    )

    cases = (ROOT / "references/evals/behavioral-cases.md").read_text(encoding="utf-8")
    for case in ("Case 1", "Case 2", "Case 3", "Case 4", "Case 5", "Case 6", "Case 7", "Case 8", "Case 9", "Case 10", "Case 11", "Case 12", "Case 13", "Case 14", "Case 15"):
        require(case in cases, f"Behavioral eval missing {case}", failures)
    blackbox_path = ROOT / "references/evals/blackbox-2026-08-31.md"
    blackbox = blackbox_path.read_text(encoding="utf-8") if blackbox_path.exists() else ""
    require("15/15 用例通过" in blackbox, "Independent black-box evaluation record is missing or not passing", failures)

    eval_summary_path = ROOT / "references/evals/eval-summary.md"
    eval_summary = eval_summary_path.read_text(encoding="utf-8")
    academic_verified = sum(row["verification_status"] != "pending" for row in academic_rows)
    academic_pending = sum(row["verification_status"] == "pending" for row in academic_rows)
    require(
        re.search(
            rf"学术/医学资源：1,736 个去重核查 URL；{academic_verified:,} 条已核验，{academic_pending:,} 条待核验",
            eval_summary,
        )
        is not None,
        "Evaluation summary academic counts are stale",
        failures,
    )
    require(
        re.search(
            rf"B站发现目录：{len(bilibili_rows)} 条长视频/合集记录；{sum(bool(row['youtube_id'] and row['official_episode_url']) for row in bilibili_rows)} 条已回链",
            eval_summary,
        )
        is not None,
        "Evaluation summary Bilibili counts are stale",
        failures,
    )
    require(
        re.search(
            rf"知识图谱 claim-study-relation-action-v6：.*{graph_stats.get('edges'):,} 条关系",
            eval_summary,
            re.S,
        )
        is not None,
        "Evaluation summary graph edge count is stale",
        failures,
    )

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print(f"summary: {len(failures)} failed")
        return 1

    print(
        "PASS  contract: trigger/safety/evidence/action rules, catalogs, Bilibili/course layers, and Case 1-15 fixtures"
    )
    print(
        f"summary: YouTube={len(transcript_rows)} ({dict(transcript_status)}), "
        f"academic={len(academic_rows)} ({sum(row['verification_status'] != 'pending' for row in academic_rows)} verified), "
        f"bilibili={len(bilibili_rows)} ({sum(bool(row['youtube_id'] and row['official_episode_url']) for row in bilibili_rows)} mapped), "
        f"courses_lectures={len(course_rows)}, claims={len(claim_rows)}, action_playbooks={len(action_playbooks)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
