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
            "我做了三天又乱了，是不是我就是自律差": "start-and-sustain-one-habit",
            "计划又乱了，我总是坚持不住": "start-and-sustain-one-habit",
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
            "下午三点就没精神，只能靠咖啡硬撑": "restore-daytime-energy-without-stimulant-stacking",
            "明明睡够了白天还是总想睡": "restore-daytime-energy-without-stimulant-stacking",
            "作息挺规律，但常常躺一个多小时睡不着": "support-trouble-falling-or-staying-asleep",
            "半夜醒了以后很久睡不回去": "support-trouble-falling-or-staying-asleep",
            "最近几个月一直紧绷，下班后也放松不下来": "support-ongoing-stress-worry-and-work-overload",
            "我每天都焦虑，脑子一直想最坏的事": "support-ongoing-stress-worry-and-work-overload",
            "我总是反复想一件事停不下来": "support-ongoing-stress-worry-and-work-overload",
            "我被工作耗空了，是不是职业倦怠": "support-ongoing-stress-worry-and-work-overload",
            "我想减肥，但晚上总忍不住吃零食": "support-weight-and-appetite-without-restrictive-protocols",
            "我白天一直忍着不吃，晚上回家就停不下来，吃到撑": "support-weight-and-appetite-without-restrictive-protocols",
            "我体重已经很低了，但还是害怕长胖，想继续减肥": "support-weight-and-appetite-without-restrictive-protocols",
            "我想用司美格鲁肽减肥，能不能自己买来打": "decide-whether-to-try-one-health-protocol",
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
            {
                "volkow-2015-caffeine-pet",
                "hazlett-2021-gratitude-rct",
                "jazayeri-2008-epa-fluoxetine-mdd",
                "niddk-prescription-weight-management-medications",
                "fda-2026-unapproved-glp1-weight-loss-warning",
            },
        )
        glp1_refs = {
            ref
            for action in decision["actions"]
            for ref in action["evidence_refs"]
        }
        self.assertTrue(
            {
                "niddk-prescription-weight-management-medications",
                "fda-2026-unapproved-glp1-weight-loss-warning",
            }
            <= glp1_refs
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
        self.assertIn("一次压力高峰", skill)
        self.assertIn("先排除危险", skill)

    def test_daytime_energy_route_prioritizes_function_and_safety_over_stimulants(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        energy = by_id["restore-daytime-energy-without-stimulant-stacking"]
        self.assertEqual(len(energy["actions"]), 3)
        for phrase in (
            "先区分普通午后低能量、危险困倦和持续疲劳",
            "舒适可停止的轻松走动",
            "不加量、不突然停用",
            "不套统一截止时间",
            "停止生活实验和危险操作",
        ):
            self.assertIn(phrase, energy["safe_summary"])
        self.assertIn("能否安全完成下一小段具体任务", energy["actions"][1]["metric"])
        self.assertIn("不追研究中的固定分钟或间隔", energy["actions"][1]["minimum_version"])
        self.assertIn("今天先不增加，也不突然取消原有摄入", energy["actions"][2]["minimum_version"])
        self.assertIn("不自行决定直接停或减量", energy["actions"][2]["minimum_version"])
        self.assertEqual(
            {link["review_id"] for link in energy["evidence_links"]},
            {
                "dempsey-2016-walking-breaks-fatigue",
                "stanyer-2024-caffeine-dose-timing-sleep",
                "kapur-2017-osa-diagnostic-guideline",
            },
        )

    def test_insomnia_route_gives_tonight_help_without_self_directed_sleep_restriction(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        insomnia = by_id["support-trouble-falling-or-staying-asleep"]
        self.assertEqual(len(insomnia["actions"]), 3)
        for phrase in ("‘睡不着’不等于‘作息后移’", "不计固定分钟", "CBT-I", "自行限睡"):
            self.assertIn(phrase, insomnia["safe_summary"])
        self.assertIn("离床不安全", insomnia["actions"][1]["minimum_version"])
        self.assertEqual(
            {link["review_id"] for link in insomnia["evidence_links"]},
            {"edinger-2021-insomnia-behavioral-guideline", "va-dod-2025-insomnia-osa-guideline"},
        )
        self.assertEqual({link["claim_id"] for link in insomnia["claim_links"]}, {"batch02-claim-0043"})

    def test_sleep_routing_respects_context_and_safety_priority(self) -> None:
        self.assertNotIn("not_for", QUERY.LIST_FIELDS)
        self.assertEqual(QUERY.query_playbooks(self.playbooks, "带娃夜里被叫醒很多次，我能睡，只是总被打断。"), [])
        medication = QUERY.query_playbooks(self.playbooks, "安眠药没用了，我今晚能不能自己加量？")
        emergency = QUERY.query_playbooks(self.playbooks, "半夜醒来胸痛、喘不上气，睡不回去怎么办？")
        self.assertEqual(medication[0]["playbook_id"], "decide-whether-to-try-one-health-protocol")
        self.assertEqual(emergency[0]["playbook_id"], "manage-an-acute-stress-spike-without-overclaiming-breathwork")
        rumination = QUERY.query_playbooks(self.playbooks, "我不是睡不着，就是白天一直想同一件事停不下来。")
        self.assertEqual(rumination[0]["playbook_id"], "support-ongoing-stress-worry-and-work-overload")

    def test_ongoing_stress_route_changes_demands_before_stacking_protocols(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        stress = by_id["support-ongoing-stress-worry-and-work-overload"]
        self.assertEqual(len(stress["actions"]), 3)
        for phrase in ("工作量", "事实—预测—下一步", "不要求先忍固定天数", "不能说明皮质醇高低", "不要用补剂"):
            self.assertIn(phrase, stress["safe_summary"])
        self.assertIn("延期、移交或取消", stress["actions"][1]["minimum_version"])
        self.assertIn("症状—持续—功能", stress["actions"][2]["action"])
        self.assertEqual(
            {link["review_id"] for link in stress["evidence_links"]},
            {
                "who-2022-mental-health-at-work-guideline",
                "nice-2024-gad-panic-guideline",
                "who-2020-doing-what-matters-stress-guide",
            },
        )
        self.assertEqual({link["claim_id"] for link in stress["claim_links"]}, {"batch02-claim-0044"})
        self.assertEqual(
            QUERY.query_playbooks(self.playbooks, "我想养成下班后散步的习惯，但回家就没动力")[0]["playbook_id"],
            "start-and-sustain-one-habit",
        )

    def test_weight_route_starts_with_safety_and_one_non_stigmatising_context(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        weight = by_id["support-weight-and-appetite-without-restrictive-protocols"]
        self.assertEqual(len(weight["actions"]), 3)
        for phrase in ("不把体重当品格", "快速/原因不明", "失控和补偿行为", "GLP-1", "不进入后续减重实验"):
            self.assertIn(phrase, weight["safe_summary"])
        self.assertIn("不跳餐、不空腹硬练", weight["actions"][1]["minimum_version"])
        self.assertIn("变化时间线—伴随症状—已尝试与影响", weight["actions"][2]["adaptation"])
        self.assertEqual(
            {link["review_id"] for link in weight["evidence_links"]},
            {
                "nice-2025-overweight-obesity-management-guideline",
                "nice-2017-eating-disorders-recognition-treatment-guideline",
                "niddk-2023-factors-affecting-weight-health",
                "hall-2019-ultra-processed-diet-rct",
            },
        )
        self.assertEqual({link["claim_id"] for link in weight["claim_links"]}, {"batch02-claim-0045"})
        medication = QUERY.query_playbooks(self.playbooks, "我打胰岛素，想直接断食减肥")
        self.assertEqual(medication[0]["playbook_id"], "decide-whether-to-try-one-health-protocol")
        self.assertEqual(
            QUERY.query_playbooks(self.playbooks, "我吃东西时完全停不下来，之后会催吐")[0]["playbook_id"],
            "support-weight-and-appetite-without-restrictive-protocols",
        )
        self.assertEqual(
            QUERY.query_playbooks(self.playbooks, "最近体重突然一直涨，不知道为什么")[0]["playbook_id"],
            "support-weight-and-appetite-without-restrictive-protocols",
        )

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
