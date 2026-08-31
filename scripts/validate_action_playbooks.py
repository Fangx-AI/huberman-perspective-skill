#!/usr/bin/env python3
"""Validate user action playbooks against reviewed study and claim catalogs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_PLAYBOOK_FIELDS = {
    "playbook_id",
    "title",
    "user_goal",
    "aliases",
    "scope",
    "first_questions",
    "baseline_checks",
    "actions",
    "evidence_links",
    "claim_links",
    "not_for",
    "escalation",
    "safe_summary",
    "last_reviewed",
}
REQUIRED_ACTION_FIELDS = {
    "action_id",
    "priority",
    "classification",
    "action",
    "why",
    "trigger",
    "minimum_version",
    "metric",
    "review_after_days",
    "adaptation",
    "stop_conditions",
    "evidence_refs",
}
ACTION_CLASSIFICATIONS = {"evidence-supported", "bounded-experiment", "framework-inference"}
SUPPORT_TYPES = {"direct-support", "bounded-support", "framework-context"}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number} of {path}: {exc}") from exc
    return records


def validate_playbooks(playbooks: list[dict], study_cards: list[dict], claims: list[dict]) -> None:
    study_ids = {card.get("review_id", "") for card in study_cards}
    claim_ids = {claim.get("claim_id", "") for claim in claims}
    playbook_ids: set[str] = set()
    for playbook in playbooks:
        playbook_id = playbook.get("playbook_id", "")
        missing = sorted(REQUIRED_PLAYBOOK_FIELDS - set(playbook))
        if missing:
            raise ValueError(f"{playbook_id or '<missing>'} missing fields: {', '.join(missing)}")
        if not playbook_id or playbook_id in playbook_ids:
            raise ValueError(f"empty or duplicate playbook_id: {playbook_id!r}")
        playbook_ids.add(playbook_id)
        for field in ("aliases", "first_questions", "baseline_checks", "not_for", "escalation"):
            values = playbook[field]
            if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
                raise ValueError(f"{field} must be a non-empty string list for {playbook_id}")
        actions = playbook["actions"]
        if not isinstance(actions, list) or not 1 <= len(actions) <= 3:
            raise ValueError(f"{playbook_id} must contain one to three actions")
        action_ids: set[str] = set()
        priorities = []
        allowed_refs = study_ids | claim_ids
        for action in actions:
            missing_action = sorted(REQUIRED_ACTION_FIELDS - set(action))
            if missing_action:
                raise ValueError(f"action in {playbook_id} missing fields: {', '.join(missing_action)}")
            action_id = action["action_id"]
            if not action_id or action_id in action_ids:
                raise ValueError(f"empty or duplicate action_id in {playbook_id}: {action_id!r}")
            action_ids.add(action_id)
            if action["classification"] not in ACTION_CLASSIFICATIONS:
                raise ValueError(f"unsupported action classification in {playbook_id}: {action['classification']}")
            if not isinstance(action["priority"], int) or isinstance(action["priority"], bool) or action["priority"] < 1:
                raise ValueError(f"action priority must be a positive integer in {playbook_id}")
            priorities.append(action["priority"])
            if not isinstance(action["review_after_days"], int) or isinstance(action["review_after_days"], bool) or action["review_after_days"] < 1:
                raise ValueError(f"review_after_days must be a positive integer in {playbook_id}")
            if not action["stop_conditions"] or not all(isinstance(value, str) and value.strip() for value in action["stop_conditions"]):
                raise ValueError(f"stop_conditions must be non-empty in {playbook_id}/{action_id}")
            evidence_refs = action["evidence_refs"]
            if not evidence_refs or not set(evidence_refs) <= allowed_refs:
                raise ValueError(f"unknown or empty evidence_refs in {playbook_id}/{action_id}")
        if sorted(priorities) != list(range(1, len(actions) + 1)):
            raise ValueError(f"action priorities must be contiguous from one in {playbook_id}")
        linked_studies = set()
        for link in playbook["evidence_links"]:
            if link.get("review_id") not in study_ids:
                raise ValueError(f"unknown study link in {playbook_id}: {link.get('review_id')}")
            if link.get("support_type") not in SUPPORT_TYPES or not link.get("supports") or not link.get("boundary"):
                raise ValueError(f"incomplete study link in {playbook_id}: {link.get('review_id')}")
            linked_studies.add(link["review_id"])
        linked_claims = set()
        for link in playbook["claim_links"]:
            if link.get("claim_id") not in claim_ids:
                raise ValueError(f"unknown claim link in {playbook_id}: {link.get('claim_id')}")
            if link.get("support_type") != "framework-context" or not link.get("supports") or not link.get("boundary"):
                raise ValueError(f"incomplete claim link in {playbook_id}: {link.get('claim_id')}")
            linked_claims.add(link["claim_id"])
        if not linked_studies or not linked_claims:
            raise ValueError(f"{playbook_id} must link both reviewed studies and public-claim context")
        declared_refs = linked_studies | linked_claims
        used_refs = {ref for action in actions for ref in action["evidence_refs"]}
        if not used_refs <= declared_refs:
            raise ValueError(f"action evidence_refs are not declared at playbook level in {playbook_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playbooks", required=True, type=Path)
    parser.add_argument("--study-cards", required=True, type=Path)
    parser.add_argument("--claims", required=True, type=Path)
    args = parser.parse_args()
    playbooks = load_jsonl(args.playbooks)
    study_cards = load_jsonl(args.study_cards)
    claims = load_jsonl(args.claims)
    validate_playbooks(playbooks, study_cards, claims)
    print(json.dumps({"playbooks": len(playbooks), "actions": sum(len(item["actions"]) for item in playbooks)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
