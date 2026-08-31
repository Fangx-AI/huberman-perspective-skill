#!/usr/bin/env python3
"""Find one outcome-first action playbook without dumping the full evidence archive."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from validate_action_playbooks import load_jsonl
except ModuleNotFoundError:  # pragma: no cover
    from scripts.validate_action_playbooks import load_jsonl


SEARCH_FIELDS = ("playbook_id", "title", "user_goal", "scope", "safe_summary")
LIST_FIELDS = ("aliases", "first_questions", "baseline_checks", "not_for")


def searchable_text(playbook: dict) -> str:
    values = [str(playbook.get(field, "")) for field in SEARCH_FIELDS]
    values.extend(str(value) for field in LIST_FIELDS for value in playbook.get(field, []))
    for action in playbook.get("actions", []):
        values.extend(str(action.get(field, "")) for field in ("action", "why", "trigger", "minimum_version", "metric", "adaptation"))
    return "\n".join(values).casefold()


def query_playbooks(playbooks: list[dict], query: str) -> list[dict]:
    normalized = query.casefold().strip()
    tokens = [token for token in re.split(r"[^\w\u4e00-\u9fff]+", normalized) if token]
    if not tokens:
        return []
    scored = []
    for playbook in playbooks:
        text = searchable_text(playbook)
        score = sum(3 if token in str(playbook.get("title", "")).casefold() else 1 for token in tokens if token in text)
        score += sum(4 for alias in playbook.get("aliases", []) if alias.casefold() in normalized or normalized in alias.casefold())
        if score:
            scored.append((score, playbook["playbook_id"], playbook))
    return [item[2] for item in sorted(scored, key=lambda item: (-item[0], item[1]))]


def concise_playbook(playbook: dict) -> dict:
    return {
        "playbook_id": playbook["playbook_id"],
        "title": playbook["title"],
        "user_goal": playbook["user_goal"],
        "first_questions": playbook["first_questions"],
        "actions": [
            {
                key: action[key]
                for key in (
                    "priority",
                    "classification",
                    "action",
                    "trigger",
                    "minimum_version",
                    "metric",
                    "review_after_days",
                    "adaptation",
                    "stop_conditions",
                )
            }
            for action in sorted(playbook["actions"], key=lambda item: item["priority"])
        ],
        "safe_summary": playbook["safe_summary"],
        "not_for": playbook["not_for"],
        "escalation": playbook["escalation"],
        "evidence_boundaries": [link["boundary"] for link in playbook["evidence_links"] + playbook["claim_links"]],
    }


def render(playbook: dict) -> str:
    lines = [f"{playbook['title']}（{playbook['playbook_id']}）", playbook["safe_summary"], "", "先确认："]
    lines.extend(f"- {question}" for question in playbook["first_questions"])
    lines.append("")
    for action in sorted(playbook["actions"], key=lambda item: item["priority"]):
        lines.extend(
            [
                f"{action['priority']}. {action['action']} [{action['classification']}]",
                f"   触发：{action['trigger']}",
                f"   最小版本：{action['minimum_version']}",
                f"   记录：{action['metric']}",
                f"   可调整的复盘点（示例为 {action['review_after_days']} 天，不是最佳间隔）：{action['adaptation']}",
            ]
        )
    lines.extend(["", "关键边界：", f"- {playbook['evidence_links'][0]['boundary']}", f"- {playbook['claim_links'][0]['boundary']}"])
    if playbook.get("escalation"):
        lines.extend(["", "需要升级处理：", *[f"- {item}" for item in playbook["escalation"]]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--playbooks", type=Path, default=Path(__file__).parents[1] / "references/catalog/action-playbooks.jsonl")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = query_playbooks(load_jsonl(args.playbooks), args.query)
    if not results:
        print("no matching action playbook")
        return 1
    selected = results[0]
    print(json.dumps(concise_playbook(selected), ensure_ascii=False, indent=2) if args.json else render(selected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
