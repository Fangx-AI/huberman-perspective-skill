from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("action_playbook_validator", ROOT / "scripts" / "validate_action_playbooks.py")
QUERY = load_module("action_playbook_query", ROOT / "scripts" / "query_action_playbooks.py")
CATALOG = ROOT / "references" / "catalog"


class ActionPlaybookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playbooks = VALIDATOR.load_jsonl(CATALOG / "action-playbooks.jsonl")
        cls.cards = VALIDATOR.load_jsonl(CATALOG / "academic-study-cards.jsonl")
        cls.claims = VALIDATOR.load_jsonl(CATALOG / "claim-index.jsonl")

    def test_committed_catalog_is_valid_and_action_limited(self) -> None:
        VALIDATOR.validate_playbooks(self.playbooks, self.cards, self.claims)
        self.assertGreaterEqual(len(self.playbooks), 8)
        for playbook in self.playbooks:
            self.assertLessEqual(len(playbook["actions"]), 3)
            self.assertTrue({"evidence-supported", "bounded-experiment", "framework-inference"} & {
                action["classification"] for action in playbook["actions"]
            })

    def test_queries_route_to_the_expected_single_playbook(self) -> None:
        cases = {
            "最近越睡越晚，早上起不来，白天没精神": "stabilize-sleep-wake-timing",
            "我收藏了很多健康建议但执行不下去": "start-and-sustain-one-habit",
            "工作时总被手机打断": "protect-one-focus-block",
            "收藏很多协议 执行不下去 习惯": "start-and-sustain-one-habit",
            "看完就忘 主动回忆 复习": "retain-what-you-learn",
            "作息漂移 晨光 睡眠": "stabilize-sleep-wake-timing",
            "总被手机打断 无法专注 工作分心": "protect-one-focus-block",
            "我久坐很久，看到很多 Huberman 运动协议反而不知道怎么开始。给我一个简单方案。": "start-exercise-without-protocol-overload",
            "我总点外卖、吃零食，但不想算卡路里。按 Huberman 视角帮我先做一个改变。": "improve-food-environment-first",
            "Huberman讲了很多补剂和健康协议，我怎么判断一个值不值得试？": "decide-whether-to-try-one-health-protocol",
            "Huberman说冷水澡提高多巴胺和免疫，我要不要每天冰浴？": "decide-whether-and-when-to-use-cold-exposure",
            "我力量训练后冰浴会不会影响增肌？": "decide-whether-and-when-to-use-cold-exposure",
            "Huberman说每周桑拿能提高生长激素、帮助长寿，我要不要买桑拿房？": "decide-whether-sauna-or-heat-is-worth-using",
            "我压力突然很大，Huberman说生理叹息有用，我现在应该怎么呼吸？": "manage-an-acute-stress-spike-without-overclaiming-breathwork",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                matches = QUERY.query_playbooks(self.playbooks, query)
                self.assertTrue(matches)
                self.assertEqual(matches[0]["playbook_id"], expected)

    def test_concise_output_keeps_execution_fields_without_evidence_dump(self) -> None:
        selected = QUERY.concise_playbook(self.playbooks[1])
        self.assertEqual(len(selected["actions"]), 3)
        for action in selected["actions"]:
            self.assertTrue({"trigger", "minimum_version", "metric", "review_after_days", "adaptation"} <= set(action))
        serialized_keys = str(selected.keys()) + str(selected["actions"][0].keys())
        for excluded in ("study_design", "sample_size", "result_summary", "provenance_urls"):
            self.assertNotIn(excluded, serialized_keys)

    def test_summaries_reject_universal_habit_deadlines_and_fixed_light_doses(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        habit = by_id["start-and-sustain-one-habit"]["safe_summary"]
        sleep = by_id["stabilize-sleep-wake-timing"]["safe_summary"]
        self.assertIn("不要用 21 或 66 天", habit)
        self.assertIn("不要直视太阳", sleep)
        self.assertIn("固定分钟数", sleep)

    def test_new_playbooks_preserve_focus_exercise_and_food_boundaries(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        focus = by_id["protect-one-focus-block"]["safe_summary"]
        exercise = by_id["start-exercise-without-protocol-overload"]["safe_summary"]
        food = by_id["improve-food-environment-first"]["safe_summary"]
        self.assertIn("不要套固定 45/5", focus)
        self.assertIn("不要把它当 ADHD", focus)
        self.assertIn("不等于长期认知改变", exercise)
        self.assertIn("不能承诺个人海马增长", exercise)
        self.assertIn("不要直接跳过进食", food)
        self.assertIn("不要把 20 人短期住院结果", food)

    def test_health_protocol_decision_separates_evidence_risk_and_care(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        decision = by_id["decide-whether-to-try-one-health-protocol"]
        self.assertIn("代理指标", decision["safe_summary"])
        self.assertIn("主要阴性结果", decision["safe_summary"])
        self.assertIn("低风险、可逆", decision["safe_summary"])
        self.assertIn("不推荐购买或给补剂剂量", decision["safe_summary"])
        self.assertIn("医生或药师", decision["safe_summary"])
        self.assertIn("不能证明疾病疗效或长期安全", decision["safe_summary"])
        self.assertEqual(
            {link["review_id"] for link in decision["evidence_links"]},
            {"volkow-2015-caffeine-pet", "hazlett-2021-gratitude-rct", "jazayeri-2008-epa-fluoxetine-mdd"},
        )
        self.assertTrue(all("剂量" not in action["action"] for action in decision["actions"]))
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("药物相互作用", skill)
        self.assertIn("个人尝试只能帮助判断一个低风险行为是否值得保留", skill)
        self.assertIn("默认不超过三个动作", skill)

    def test_cold_exposure_decision_separates_goals_nulls_adaptation_and_safety(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        cold = by_id["decide-whether-and-when-to-use-cold-exposure"]
        self.assertEqual(len(cold["actions"]), 3)
        for phrase in ("不是睡眠、专注、免疫、减脂或情绪的必需品", "外周多巴胺", "缺勤下降", "长期适应", "不给固定温度/时长", "开放水域"):
            self.assertIn(phrase, cold["safe_summary"])
        self.assertIn("患病天数未改善", cold["actions"][2]["why"])
        self.assertIn("不规定温度或时长", cold["actions"][2]["minimum_version"])
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("冷水", skill)
        self.assertIn("不得发明固定剂量、温度、时长", skill)
        self.assertIn("不能证明疾病疗效或长期安全", skill)

    def test_sauna_decision_rejects_observational_dose_and_hormone_optimization(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        sauna = by_id["decide-whether-sauna-or-heat-is-worth-using"]
        self.assertEqual(len(sauna["actions"]), 3)
        for phrase in ("不足以支持购买桑拿房", "观察关联", "急性激素峰值", "多数结局总体阴性", "不给固定温度"):
            self.assertIn(phrase, sauna["safe_summary"])
        evidence_ids = {link["review_id"] for link in sauna["evidence_links"]}
        self.assertTrue({
            "leppaluoto-1986-repeated-sauna-endocrine",
            "hamaya-2025-passive-heating-rct-meta-analysis",
            "debray-2023-sauna-stable-cad-rct",
            "kaiser-2023-sauna-injury-series",
        } <= evidence_ids)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("桑拿/热暴露", skill)
        self.assertIn("停止条件", skill)

    def test_acute_stress_breathing_decision_preserves_nulls_and_triage(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        breathing = by_id["manage-an-acute-stress-spike-without-overclaiming-breathwork"]
        self.assertEqual(len(breathing["actions"]), 3)
        for phrase in (
            "先排除急症",
            "没有证明它在状态焦虑下降上优于正念",
            "HRV",
            "单独呼吸总体不显著",
            "不要在驾驶",
            "反复惊恐",
        ):
            self.assertIn(phrase, breathing["safe_summary"])
        self.assertIn("不计时、不憋气、不快速深呼吸", breathing["actions"][1]["minimum_version"])
        self.assertIn("失控感", " ".join(breathing["actions"][1]["stop_conditions"]))
        evidence_ids = {link["review_id"] for link in breathing["evidence_links"]}
        self.assertEqual(evidence_ids, {
            "balban-2023-structured-respiration-rct",
            "fincham-2023-breathwork-stress-meta-analysis",
            "chin-2024-brief-state-anxiety-review",
        })
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("非紧急压力与呼吸", skill)
        self.assertIn("先排除危险", skill)

    def test_validator_rejects_more_than_three_actions_and_unknown_refs(self) -> None:
        too_many = copy.deepcopy(self.playbooks)
        extra = copy.deepcopy(too_many[0]["actions"][0])
        extra["action_id"] = "fourth"
        extra["priority"] = 4
        too_many[0]["actions"].append(extra)
        with self.assertRaisesRegex(ValueError, "one to three actions"):
            VALIDATOR.validate_playbooks(too_many, self.cards, self.claims)

        unknown = copy.deepcopy(self.playbooks)
        unknown[0]["actions"][0]["evidence_refs"] = ["unknown-evidence"]
        with self.assertRaisesRegex(ValueError, "unknown or empty evidence_refs"):
            VALIDATOR.validate_playbooks(unknown, self.cards, self.claims)

    def test_skill_forbids_invented_protocol_numbers_after_routing(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for rule in ("不得把动作拆成更多协议", "不得发明固定剂量、温度、时长、频率、阈值或保证", "一次只调整一个变量", "机制只有在帮助选择、执行或避险时才解释"):
            self.assertIn(rule, skill)

    def test_renderer_labels_review_days_as_adjustable_not_optimal(self) -> None:
        rendered = QUERY.render(self.playbooks[1])
        self.assertIn("可调整的复盘点", rendered)
        self.assertIn("不是最佳间隔", rendered)


if __name__ == "__main__":
    unittest.main()
