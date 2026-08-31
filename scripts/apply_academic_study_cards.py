#!/usr/bin/env python3
"""Validate structured study cards and apply their review status to the academic queue."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "review_id",
    "title",
    "doi",
    "source_urls",
    "provenance_urls",
    "verification_status",
    "evidence_level",
    "topic_tags",
    "study_design",
    "sample_size",
    "population",
    "intervention_exposure",
    "comparator",
    "outcomes",
    "result_summary",
    "null_findings",
    "limitations",
    "safe_interpretation",
    "queue_note",
    "reviewed_at",
}
ALLOWED_STATUSES = {"verified-study", "verified-review", "verified-observational"}
PROMOTABLE_STATUSES = {"verified-bibliographic", *ALLOWED_STATUSES}
ALLOWED_SOURCE_SCOPES = {"episode-linked", "external-context"}


def queue_urls(card: dict) -> list[str]:
    return card.get("queue_urls", card["source_urls"])


def load_cards(path: Path) -> list[dict]:
    cards = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc}") from exc
            missing = sorted(REQUIRED_FIELDS - set(card))
            if missing:
                raise ValueError(f"card on line {line_number} is missing fields: {', '.join(missing)}")
            cards.append(card)
    return cards


def validate_cards(cards: list[dict]) -> None:
    review_ids: set[str] = set()
    source_urls: set[str] = set()
    for card in cards:
        review_id = card["review_id"]
        if not review_id or review_id in review_ids:
            raise ValueError(f"empty or duplicate review_id: {review_id!r}")
        review_ids.add(review_id)
        if card["verification_status"] not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported verification_status for {review_id}: {card['verification_status']}")
        source_scope = card.get("source_scope", "episode-linked")
        if source_scope not in ALLOWED_SOURCE_SCOPES:
            raise ValueError(f"unsupported source_scope for {review_id}: {source_scope}")
        if "queue_urls" in card and not isinstance(card["queue_urls"], list):
            raise ValueError(f"queue_urls must be a list for {review_id}")
        if source_scope == "external-context" and ("queue_urls" not in card or card["queue_urls"]):
            raise ValueError(f"external-context cards must declare an empty queue_urls list for {review_id}")
        if not isinstance(card["sample_size"], int) or card["sample_size"] <= 0:
            raise ValueError(f"sample_size must be a positive integer for {review_id}")
        for field in ("source_urls", "provenance_urls", "topic_tags", "outcomes", "null_findings", "limitations"):
            if not isinstance(card[field], list) or not card[field]:
                raise ValueError(f"{field} must be a non-empty list for {review_id}")
        if "search_aliases" in card and (
            not isinstance(card["search_aliases"], list)
            or not card["search_aliases"]
            or not all(isinstance(alias, str) and alias.strip() for alias in card["search_aliases"])
        ):
            raise ValueError(f"search_aliases must be a non-empty string list for {review_id}")
        if not all(url.startswith("https://") for url in card["source_urls"] + card["provenance_urls"]):
            raise ValueError(f"all source/provenance URLs must use HTTPS for {review_id}")
        for source_url in card["source_urls"]:
            if source_url in source_urls:
                raise ValueError(f"source URL appears in more than one card: {source_url}")
            source_urls.add(source_url)
        if not set(queue_urls(card)) <= set(card["source_urls"]):
            raise ValueError(f"queue_urls must be a subset of source_urls for {review_id}")
        for field in (
            "title",
            "doi",
            "evidence_level",
            "study_design",
            "population",
            "intervention_exposure",
            "comparator",
            "result_summary",
            "safe_interpretation",
            "queue_note",
            "reviewed_at",
        ):
            if not isinstance(card[field], str) or not card[field].strip():
                raise ValueError(f"{field} must be a non-empty string for {review_id}")


def apply_cards(queue_rows: list[dict[str, str]], cards: list[dict]) -> int:
    by_url = {row["url"]: row for row in queue_rows}
    requested_urls = {url for card in cards for url in queue_urls(card)}
    missing = sorted(requested_urls - set(by_url))
    if missing:
        raise ValueError(f"study-card URLs missing from academic queue: {missing}")

    changed = 0
    for card in cards:
        for url in queue_urls(card):
            row = by_url[url]
            current = row.get("verification_status", "pending")
            if current not in PROMOTABLE_STATUSES:
                raise ValueError(f"refusing to promote {url} from {current!r}; bibliographic verification is required first")
            target = card["verification_status"]
            note = card["queue_note"]
            if current != target or row.get("evidence_notes", "") != note:
                row["verification_status"] = target
                row["evidence_notes"] = note
                changed += 1
    return changed


def write_queue(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", required=True, type=Path)
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    cards = load_cards(args.cards)
    validate_cards(cards)
    with args.queue.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    changed = apply_cards(rows, cards)
    if not args.check_only:
        write_queue(args.queue, rows, fieldnames)
    print(json.dumps({"cards": len(cards), "queue_rows_changed": changed, "check_only": args.check_only}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
