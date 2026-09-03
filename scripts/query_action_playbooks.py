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
LIST_FIELDS = ("aliases", "first_questions", "baseline_checks")

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
        "开车犯困",
        "开车还会犯困",
        "白天开车",
    ),
    "support-trouble-falling-or-staying-asleep": (
        "躺下一个多小时都睡不着",
        "躺下睡不着",
        "翻来覆去睡不着",
        "一上床就清醒",
        "明明很困却睡不着",
        "半夜醒了睡不回去",
        "醒了以后睡不回去",
        "每晚三四点醒",
        "比闹钟早醒",
        "天没亮就醒",
        "越想睡越焦虑",
        "一直看时间",
        "睡前脑子停不下来",
        "连续几周睡不好",
        "少睡反而特别兴奋",
        "不需要睡觉也很兴奋",
        "失眠",
    ),
    "stabilize-sleep-wake-timing": (
        "越睡越晚",
        "早上起不来",
        "白天没精神",
        "作息越来越乱",
        "凌晨睡",
        "中午才醒",
        "白天昏昏沉沉",
        "轮班工作",
        "白天睡不着",
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
        "下班后散步的习惯",
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
    "support-weight-and-appetite-without-restrictive-protocols": (
        "想减肥但总失败",
        "想减脂不知道从哪开始",
        "晚上总忍不住吃零食",
        "一到晚上就吃很多",
        "控制不住食欲",
        "最近体重一直涨",
        "瘦不下来",
        "是不是代谢坏了",
        "白天一直忍着不吃",
        "晚上吃到撑",
        "夜班凌晨特别饿",
        "疯狂点外卖",
        "吃完就催吐",
        "减重",
        "weight loss",
        "appetite control",
    ),
    "reduce-alcohol-use-with-withdrawal-and-overdose-safety": (
        "想少喝酒",
        "不想完全戒酒",
        "一下班就开一瓶",
        "每天顺手开一罐啤酒",
        "靠酒入睡",
        "睡前喝酒才能睡",
        "睡前喝一杯才能睡",
        "停酒后手抖出汗",
        "戒酒时抽搐",
        "酒后叫不醒",
        "喝酒后呼吸异常",
        "酒和安眠药一起吃",
        "怀孕喝酒",
        "cut down drinking",
        "alcohol withdrawal",
        "alcohol overdose",
    ),
    "manage-an-acute-stress-spike-without-overclaiming-breathwork": (
        "压力大到无法工作",
        "先让我缓下来",
        "一紧张就喘不过气",
        "焦虑得无法工作",
        "胸痛气短",
        "活着没意思",
        "不想活",
        "呼吸法",
    ),
    "support-ongoing-stress-worry-and-work-overload": (
        "最近几个月一直紧绷",
        "下班后也放松不下来",
        "每天都焦虑",
        "脑子一直想最坏的事",
        "压力不是突然来的",
        "工作堆了半年",
        "生理叹息只能管一会儿",
        "长期压力怎么办",
        "一到周日晚上就焦虑",
        "想到上班就难受",
        "反复想一件事停不下来",
        "最近没动力什么都不想做",
        "被工作耗空了",
        "职业倦怠",
        "burnout",
        "rumination",
        "chronic stress",
    ),
    "decide-whether-to-try-one-health-protocol": (
        "鱼油",
        "镁能改善",
        "补剂",
        "吃药后头晕",
        "吃药以后整天疲劳",
        "自己减量",
        "自己加量",
        "安眠药",
        "停药",
    ),
    "decide-whether-a-red-light-device-is-worth-buying": ("红光面罩", "红光设备", "红光是不是智商税"),
    "decide-whether-and-when-to-use-cold-exposure": ("冷水澡", "冰浴", "冷水浴"),
    "decide-whether-sauna-or-heat-is-worth-using": ("桑拿房", "蒸桑拿", "桑拿值不值"),
}

MIN_LEXICAL_ROUTE_SCORE = 18
INSOMNIA_PLAYBOOK = "support-trouble-falling-or-staying-asleep"
ONGOING_STRESS_PLAYBOOK = "support-ongoing-stress-worry-and-work-overload"
WEIGHT_PLAYBOOK = "support-weight-and-appetite-without-restrictive-protocols"
ALCOHOL_PLAYBOOK = "reduce-alcohol-use-with-withdrawal-and-overdose-safety"
ACUTE_STRESS_PLAYBOOK = "manage-an-acute-stress-spike-without-overclaiming-breathwork"
PROTOCOL_PLAYBOOK = "decide-whether-to-try-one-health-protocol"
SLEEP_PLAYBOOKS = {INSOMNIA_PLAYBOOK, "stabilize-sleep-wake-timing"}
EXTERNAL_SLEEP_INTERRUPTION_TERMS = ("带娃", "孩子叫醒", "照护", "夜班照护", "噪音", "室友", "邻居")
SELF_SLEEP_DIFFICULTY_TERMS = ("睡不着", "睡不回", "失眠", "早醒", "越想睡", "清醒", "不需要睡")
SLEEP_TIMING_TERMS = ("作息", "越睡越晚", "凌晨睡", "中午醒", "轮班", "时差")
SLEEP_CONTEXT_TERMS = ("睡", "床", "躺下", "困", "晚上", "夜醒", "早醒", "闹钟", "失眠", "作息", "凌晨", "轮班", "时差")
NEGATED_SLEEP_DIFFICULTY_PATTERNS = ("不是睡不着", "没有睡不着", "并非失眠", "不是失眠", "睡眠没问题", "我能睡")
ONGOING_STRESS_TERMS = (
    "几个月", "半年", "长期", "每天都焦虑", "最近一直焦虑", "反复想", "想同一件事", "周日晚上", "一到周日", "下班后",
    "工作堆", "工作耗空", "职业倦怠", "倦怠", "放松不下来", "撑不住", "最坏的事", "担心",
    "反刍", "没动力", "什么都不想做", "burnout", "rumination", "chronic stress",
)
ACUTE_STRESS_TERMS = ("突然", "现在", "刚刚", "马上", "先让我缓下来", "压力高峰", "惊恐", "喘不过气")
CORTISOL_PROTOCOL_TERMS = ("皮质醇", "肾上腺疲劳", "降皮质醇", "补剂", "ashwagandha", "南非醉茄")
WEIGHT_PROTOCOL_TERMS = ("glp-1", "semaglutide", "司美格鲁肽", "ozempic", "wegovy", "二甲双胍", "小檗碱", "berberine", "减肥药", "胰岛素", "糖尿病药")
WEIGHT_CONTEXT_TERMS = (
    "减肥", "减脂", "减重", "体重", "食欲", "总忍不住吃", "晚上总吃", "一到晚上就吃", "夜间吃",
    "暴食", "吃很多", "吃到撑", "忍着不吃", "明明不饿", "疯狂点外卖", "催吐", "泻药", "补偿运动",
    "怕长胖", "瘦不下来", "代谢坏了", "胖了", "weight loss", "appetite control",
)
ALCOHOL_CONTEXT_TERMS = (
    "喝酒", "喝了酒", "每天喝", "喝很多", "很多酒", "喝醉", "饮酒", "戒酒", "停酒", "减酒", "少喝", "酒精", "啤酒", "白酒", "红酒", "烈酒",
    "宿醉", "醉酒", "酒后", "靠酒", "睡前喝一杯才能睡", "alcohol", "drinking", "withdrawal",
)
ALCOHOL_HIGH_RISK_TERMS = (
    "手抖", "出汗", "心慌", "抽搐", "癫痫", "幻觉", "看到不存在", "意识混乱", "叫不醒", "呼吸慢",
    "呼吸异常", "呼吸不规则", "嘴唇发青", "反复呕吐", "吐了几次", "安眠药", "阿普唑仑", "苯二氮卓",
    "阿片", "强效止痛药", "怀孕", "孕期", "备孕", "未成年", "开车", "驾驶",
)
EMERGENCY_TERMS = (
    "胸痛", "胸口发紧", "喘不上气", "呼吸不顺", "严重气促", "晕厥", "意识混乱", "单侧无力",
    "活着没意思", "不想活", "不想醒来", "想消失", "消失算了", "自伤", "他伤", "无法保证安全",
)
MEDICATION_TERMS = ("安眠药", "处方药", "药物", "加量", "减量", "停药", "漏服", "下一剂")
NEGATION_PREFIXES = ("没有", "没", "无", "否认", "不是", "并非", "不", "从不")
HABIT_GOAL_TERMS = ("想养成", "建立习惯", "培养习惯", "养成习惯")


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


def contains_unnegated_term(normalized: str, terms: tuple[str, ...]) -> bool:
    """Treat a nearby explicit negation as a safety disclosure, not a positive symptom."""
    for term in terms:
        start = 0
        while True:
            index = normalized.find(term, start)
            if index < 0:
                break
            prefix = normalized[max(0, index - 4) : index]
            if not any(prefix.endswith(negation) for negation in NEGATION_PREFIXES):
                return True
            start = index + len(term)
    return False


def searchable_text(playbook: dict) -> str:
    values = [str(playbook.get(field, "")) for field in SEARCH_FIELDS]
    values.extend(str(value) for field in LIST_FIELDS for value in playbook.get(field, []))
    for action in playbook.get("actions", []):
        values.extend(str(action.get(field, "")) for field in ("action", "why", "trigger", "minimum_version", "metric", "adaptation"))
    return "\n".join(values).casefold()


def blocked_by_context(playbook_id: str, normalized: str) -> bool:
    if playbook_id in SLEEP_PLAYBOOKS:
        has_sleep_context = any(term in normalized for term in SLEEP_CONTEXT_TERMS)
        if not has_sleep_context:
            return True
        externally_interrupted = any(term in normalized for term in EXTERNAL_SLEEP_INTERRUPTION_TERMS)
        has_self_sleep_difficulty = any(term in normalized for term in SELF_SLEEP_DIFFICULTY_TERMS)
        has_timing_shift = any(term in normalized for term in SLEEP_TIMING_TERMS)
        negates_sleep_difficulty = any(term in normalized for term in NEGATED_SLEEP_DIFFICULTY_PATTERNS)
        if negates_sleep_difficulty and not has_timing_shift:
            return True
        return externally_interrupted and not has_self_sleep_difficulty and not has_timing_shift
    if playbook_id == ONGOING_STRESS_PLAYBOOK:
        return not any(term in normalized for term in ONGOING_STRESS_TERMS)
    if playbook_id == WEIGHT_PLAYBOOK:
        return not any(term in normalized for term in WEIGHT_CONTEXT_TERMS)
    if playbook_id == ALCOHOL_PLAYBOOK:
        return not contains_unnegated_term(normalized, ALCOHOL_CONTEXT_TERMS)
    return False


def context_bonus(playbook_id: str, normalized: str) -> int:
    has_alcohol_context = contains_unnegated_term(normalized, ALCOHOL_CONTEXT_TERMS)
    if playbook_id == ALCOHOL_PLAYBOOK and has_alcohol_context and any(
        term in normalized for term in ALCOHOL_HIGH_RISK_TERMS
    ):
        return 6500
    if playbook_id == ACUTE_STRESS_PLAYBOOK and contains_unnegated_term(normalized, EMERGENCY_TERMS):
        return 5000
    if playbook_id == PROTOCOL_PLAYBOOK and any(
        term in normalized for term in MEDICATION_TERMS + CORTISOL_PROTOCOL_TERMS + WEIGHT_PROTOCOL_TERMS
    ):
        return 3000
    if playbook_id == ACUTE_STRESS_PLAYBOOK and any(term in normalized for term in ACUTE_STRESS_TERMS):
        return 1800
    if playbook_id == "start-and-sustain-one-habit" and any(term in normalized for term in HABIT_GOAL_TERMS):
        return 2200
    if playbook_id == ONGOING_STRESS_PLAYBOOK and any(term in normalized for term in ONGOING_STRESS_TERMS):
        return 1600
    if playbook_id == WEIGHT_PLAYBOOK and any(term in normalized for term in WEIGHT_CONTEXT_TERMS):
        return 2400
    if playbook_id == ALCOHOL_PLAYBOOK and has_alcohol_context:
        return 2600
    if playbook_id == INSOMNIA_PLAYBOOK and any(term in normalized for term in SELF_SLEEP_DIFFICULTY_TERMS):
        return 30
    return 0


def query_playbooks(playbooks: list[dict], query: str) -> list[dict]:
    normalized = query.casefold().strip()
    query_units = lexical_units(normalized)
    if not query_units:
        return []
    scored = []
    for playbook in playbooks:
        if blocked_by_context(playbook["playbook_id"], normalized):
            continue
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
        score += context_bonus(playbook["playbook_id"], normalized)
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
