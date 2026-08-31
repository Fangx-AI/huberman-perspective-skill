#!/usr/bin/env python3
"""Search structured academic study cards without treating keyword matches as conclusions."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SEARCH_FIELDS = (
    "review_id",
    "title",
    "doi",
    "evidence_level",
    "study_design",
    "population",
    "intervention_exposure",
    "comparator",
    "result_summary",
    "safe_interpretation",
)
LIST_FIELDS = ("topic_tags", "outcomes", "null_findings", "limitations")


def load_cards(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def searchable_text(card: dict) -> str:
    values = [str(card.get(field, "")) for field in SEARCH_FIELDS]
    values.extend(str(value) for field in LIST_FIELDS for value in card.get(field, []))
    return "\n".join(values).casefold()


def query_cards(cards: list[dict], query: str, limit: int = 10) -> list[dict]:
    terms = [term.casefold() for term in re.findall(r"[\w+-]+", query, flags=re.UNICODE) if term.strip()]
    if not terms:
        return []
    scored = []
    for card in cards:
        haystack = searchable_text(card)
        matched = [term for term in terms if term in haystack]
        if not matched:
            continue
        title = str(card.get("title", "")).casefold()
        tags = " ".join(card.get("topic_tags", [])).casefold()
        score = len(matched) + 2 * sum(term in title for term in matched) + 2 * sum(term in tags for term in matched)
        scored.append((score, card.get("review_id", ""), card))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [card for _, _, card in scored[:limit]]


def concise_record(card: dict) -> dict:
    return {
        "review_id": card.get("review_id", ""),
        "title": card.get("title", ""),
        "doi": card.get("doi", ""),
        "evidence_level": card.get("evidence_level", ""),
        "study_design": card.get("study_design", ""),
        "sample_size": card.get("sample_size", ""),
        "population": card.get("population", ""),
        "result_summary": card.get("result_summary", ""),
        "null_findings": card.get("null_findings", []),
        "limitations": card.get("limitations", []),
        "safe_interpretation": card.get("safe_interpretation", ""),
        "provenance_urls": card.get("provenance_urls", []),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument(
        "--cards",
        type=Path,
        default=Path(__file__).parents[1] / "references/catalog/academic-study-cards.jsonl",
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.limit <= 0:
        raise SystemExit("--limit must be positive")
    results = [concise_record(card) for card in query_cards(load_cards(args.cards), args.query, args.limit)]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for index, result in enumerate(results, start=1):
            print(f"[{index}] {result['title']} ({result['review_id']})")
            print(f"设计/样本：{result['study_design']}；n={result['sample_size']}；{result['population']}")
            print(f"结果：{result['result_summary']}")
            print(f"阴性结果：{'；'.join(result['null_findings'])}")
            print(f"边界：{result['safe_interpretation']}")
            print(f"来源：{'；'.join(result['provenance_urls'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
