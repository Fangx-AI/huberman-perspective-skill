#!/usr/bin/env python3
"""Validate auditable relations between structured academic study cards."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FIELDS = {
    "relation_id",
    "source_review_id",
    "relation",
    "target_review_id",
    "claim_scope",
    "rationale",
    "boundary",
    "provenance_urls",
    "reviewed_at",
}
ALLOWED_RELATIONS = {"replicates", "supports", "qualifies", "challenges", "contradicts"}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number} of {path}: {exc}") from exc
    return records


def validate_relations(cards: list[dict], relations: list[dict]) -> None:
    review_ids = {card.get("review_id", "") for card in cards}
    relation_ids: set[str] = set()
    for relation in relations:
        missing = sorted(REQUIRED_FIELDS - set(relation))
        if missing:
            raise ValueError(f"evidence relation is missing fields: {', '.join(missing)}")
        relation_id = relation["relation_id"]
        if not relation_id or relation_id in relation_ids:
            raise ValueError(f"empty or duplicate relation_id: {relation_id!r}")
        relation_ids.add(relation_id)
        source = relation["source_review_id"]
        target = relation["target_review_id"]
        if source not in review_ids or target not in review_ids:
            raise ValueError(f"relation {relation_id} references an unknown study card")
        if source == target:
            raise ValueError(f"relation {relation_id} cannot point to the same study card")
        if relation["relation"] not in ALLOWED_RELATIONS:
            raise ValueError(f"unsupported evidence relation for {relation_id}: {relation['relation']}")
        for field in ("claim_scope", "rationale", "boundary", "reviewed_at"):
            if not isinstance(relation[field], str) or not relation[field].strip():
                raise ValueError(f"{field} must be a non-empty string for {relation_id}")
        urls = relation["provenance_urls"]
        if not isinstance(urls, list) or not urls or not all(isinstance(url, str) and url.startswith("https://") for url in urls):
            raise ValueError(f"provenance_urls must be a non-empty HTTPS list for {relation_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", required=True, type=Path)
    parser.add_argument("--relations", required=True, type=Path)
    args = parser.parse_args()
    cards = load_jsonl(args.cards)
    relations = load_jsonl(args.relations)
    validate_relations(cards, relations)
    print(json.dumps({"cards": len(cards), "relations": len(relations)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
