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

# Natural-language phrases observed in user requests. Keep these separate from the
# evidence catalog: they improve routing without changing any evidence claim.
COMMON_ROUTING_ALIASES = {
    "restore-daytime-energy-without-stimulant-stacking": (
        "下午三点就没精神",
        "午后崩掉",
        "午后犯困",
        "下午犯困",
        "靠咖啡硬撑",
        "越喝咖啡越没精神",
        "明明睡够了还是很累",
        "睡够还是很累",
        "睡够仍然疲劳",
        "白天总想睡",
    ),
    "stabilize-sleep-wake-timing": (
        "越睡越晚",
        "早上起不来",
        "白天没精神",
        "睡不着",
        "作息越来越乱",
        "凌晨睡",
        "中午才醒",
        "白天昏昏沉沉",
        "轮班工作",
        "白天睡不着",
        "睡眠都碎",
    ),
    "start-and-sustain-one-habit": (
        "健康建议执行不下去",
        "一个也坚持不住",
        "总是坚持不住",
        "做了三天又乱了",
        "计划又乱了",
        "是不是自律差",
        "我自律差",
        "又没坚持住",
        "计划三天就放弃",
        "每天读书的习惯",
        "晨间习惯",
        "习惯都失败",
    ),
    "protect-one-focus-block": (
        "工作时被手机打断",
        "总被手机打断",
        "脑子转不动",
        "打开电脑就摸手机",
        "进入不了工作状态",
        "注意力很差",
        "恢复专注",
        "ADHD",
    ),
    "retain-what-you-learn": ("背了就忘", "学得牢", "看了很多课", "什么都记不住"),
    "start-exercise-without-protocol-overload": (
        "几年没运动",
        "从什么开始运动",
        "膝盖痛还能不能跑步",
        "训练后总是很累",
    ),
    "improve-food-environment-first": (
        "忍不住点外卖",
        "焦虑就暴食",
        "不想算卡路里",
        "饮食先改",
    ),
    "manage-an-acute-stress-spike-without-overclaiming-breathwork": (
        "压力大到无法工作",
        "先让我缓下来",
        "一紧张就喘不过气",
        "一直焦虑",
        "焦虑得无法工作",
        "胸痛气短",
        "呼吸法",
    ),
    "decide-whether-to-try-one-health-protocol": (
        "鱼油",
        "镁能改善",
        "补剂",
        "吃药后头晕",
        "吃药以后整天疲劳",
        "自己减量",
    ),
    "decide-whether-a-red-light-device-is-worth-buying": ("红光面罩", "红光设备", "红光是不是智商税"),
    "decide-whether-and-when-to-use-cold-exposure": ("冷水澡", "冰浴", "冷水浴"),
    "decide-whether-sauna-or-heat-is-worth-using": ("桑拿房", "蒸桑拿", "桑拿值不值"),
}

MIN_LEXICAL_ROUTE_SCORE = 18


def lexical_units(value: str) -> set[str]:
    """Split Latin text and add 2–4 character CJK n-grams for phrase routing."""
    normalized = value.casefold()
    units = set(re.findall(r"[a-z0-9_-]+", normalized))
    for run in re.findall(r"[\u4e00-\u9fff]+", normalized):
        units.add(run)
        for size in (2, 3, 4):
            if len(run) >= size:
                units.update(run[index : index + size] for index in range(len(run) - size + 1))
    return units


def searchable_text(playbook: dict) -> str:
    values = [str(playbook.get(field, "")) for field in SEARCH_FIELDS]
    values.extend(str(value) for field in LIST_FIELDS for value in playbook.get(field, []))
    for action in playbook.get("actions", []):
        values.extend(str(action.get(field, "")) for field in ("action", "why", "trigger", "minimum_version", "metric", "adaptation"))
    return "\n".join(values).casefold()


def query_playbooks(playbooks: list[dict], query: str) -> list[dict]:
    normalized = query.casefold().strip()
    query_units = lexical_units(normalized)
    if not query_units:
        return []
    scored = []
    for playbook in playbooks:
        aliases = list(playbook.get("aliases", [])) + list(COMMON_ROUTING_ALIASES.get(playbook["playbook_id"], ()))
        routing_text = "\n".join(
            [playbook.get("playbook_id", ""), playbook.get("title", ""), playbook.get("user_goal", "")]
            + aliases
        )
        routing_units = lexical_units(routing_text)
        body_units = lexical_units(searchable_text(playbook))
        routing_overlap = query_units & routing_units
        body_overlap = query_units & body_units
        score = sum(max(1, min(len(unit), 4) - 1) * 3 for unit in routing_overlap)
        score += sum(1 for unit in body_overlap - routing_overlap)
        exact_aliases = [
            alias.casefold()
            for alias in aliases
            if alias.casefold() in normalized or normalized in alias.casefold()
        ]
        if exact_aliases:
            # A phrase maintained from real user language should beat incidental
            # 2–4 character overlap in a long playbook body.
            score += 1000 + max(len(alias) for alias in exact_aliases) * 10
        if exact_aliases or score >= MIN_LEXICAL_ROUTE_SCORE:
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
