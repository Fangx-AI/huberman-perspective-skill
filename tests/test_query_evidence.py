from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("query_evidence", ROOT / "scripts" / "query_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EvidenceQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cards = MODULE.load_cards(ROOT / "references" / "catalog" / "academic-study-cards.jsonl")
        cls.relations = MODULE.load_relations(ROOT / "references" / "catalog" / "evidence-relations.jsonl")

    def test_chinese_query_returns_bounded_caffeine_card(self) -> None:
        results = MODULE.query_cards(self.cards, "咖啡因 多巴胺")
        self.assertEqual(results[0]["review_id"], "volkow-2015-caffeine-pet")
        concise = MODULE.concise_record(results[0])
        self.assertTrue(concise["null_findings"])
        self.assertTrue(concise["limitations"])
        self.assertTrue(concise["safe_interpretation"])
        self.assertTrue(concise["provenance_urls"])

    def test_english_query_ranks_gratitude_card(self) -> None:
        results = MODULE.query_cards(self.cards, "gratitude inflammation")
        self.assertEqual(results[0]["review_id"], "hazlett-2021-gratitude-rct")

    def test_chinese_sleep_query_includes_motor_learning_boundaries(self) -> None:
        results = MODULE.query_cards(self.cards, "睡眠 运动学习 巩固")
        self.assertEqual(results[0]["review_id"], "walker-2003-sleep-motor-learning")
        card = next(item for item in results if item["review_id"] == "walker-2003-sleep-motor-learning")
        concise = MODULE.concise_record(card)
        self.assertIn("所有学习", concise["safe_interpretation"])
        self.assertTrue(any("三晚" in finding for finding in concise["null_findings"]))
        self.assertTrue(any("随机" in limitation for limitation in concise["limitations"]))

    def test_sleep_card_surfaces_bounded_counterevidence(self) -> None:
        card = next(item for item in self.cards if item["review_id"] == "walker-2003-sleep-motor-learning")
        concise = MODULE.concise_record(card, self.cards, self.relations)
        related = {item["relation_id"]: item for item in concise["related_evidence"]}
        challenge = related["rickard-2008-challenges-walker-2003-enhancement"]
        qualification = related["nettersheim-2015-qualifies-walker-2003-enhancement"]
        self.assertEqual(challenge["counterpart_review_id"], "rickard-2008-sleep-motor-sequence")
        self.assertEqual(challenge["direction"], "incoming")
        self.assertEqual(qualification["direction"], "incoming")
        self.assertIn("不否定", challenge["boundary"])

    def test_stabilization_query_returns_outgoing_evidence_triangle(self) -> None:
        results = MODULE.query_cards(self.cards, "睡眠 稳定 运动学习")
        self.assertEqual(results[0]["review_id"], "nettersheim-2015-sleep-stabilization")
        concise = MODULE.concise_record(results[0], self.cards, self.relations)
        self.assertEqual(len(concise["related_evidence"]), 2)
        self.assertTrue(all(item["direction"] == "outgoing" for item in concise["related_evidence"]))
        self.assertEqual({item["relation"] for item in concise["related_evidence"]}, {"qualifies", "supports"})

    def test_natural_light_query_returns_bounded_followup_pair(self) -> None:
        results = MODULE.query_cards(self.cards, "自然光 昼夜节律 周末露营")
        self.assertEqual(results[0]["review_id"], "stothard-2017-natural-light-seasons-weekend")
        self.assertEqual(results[1]["review_id"], "wright-2013-natural-light-entrainment")
        concise = MODULE.concise_record(results[0], self.cards, self.relations)
        relation = next(
            item
            for item in concise["related_evidence"]
            if item["relation_id"] == "stothard-2017-supports-wright-2013-natural-light-entrainment"
        )
        self.assertEqual(relation["direction"], "outgoing")
        self.assertEqual(relation["relation"], "supports")
        self.assertIn("不是独立复制", relation["boundary"])
        self.assertIn("固定晨光分钟数", concise["safe_interpretation"])

    def test_legacy_stothart_spelling_remains_searchable(self) -> None:
        results = MODULE.query_cards(self.cards, "stothart")
        self.assertEqual(results[0]["review_id"], "stothard-2017-natural-light-seasons-weekend")

    def test_active_retrieval_query_returns_bounded_three_card_cluster(self) -> None:
        results = MODULE.query_cards(self.cards, "主动提取 测试效应 长期保持 反馈")
        self.assertEqual(
            [item["review_id"] for item in results[:3]],
            [
                "dunlosky-2013-effective-learning-techniques-review",
                "roediger-karpicke-2006-test-enhanced-learning",
                "karpicke-roediger-2008-repeated-retrieval",
            ],
        )
        review = MODULE.concise_record(results[0], self.cards, self.relations)
        self.assertEqual(len(review["related_evidence"]), 2)
        self.assertTrue(all(item["direction"] == "outgoing" for item in review["related_evidence"]))
        self.assertTrue(all(item["relation"] == "qualifies" for item in review["related_evidence"]))
        first_experiment = MODULE.concise_record(results[1], self.cards, self.relations)
        self.assertEqual({item["relation"] for item in first_experiment["related_evidence"]}, {"supports", "qualifies"})
        self.assertIn("反馈", review["safe_interpretation"])
        self.assertIn("固定", review["safe_interpretation"])

    def test_habit_query_rejects_fixed_twenty_one_or_sixty_six_day_rule(self) -> None:
        results = MODULE.query_cards(self.cards, "习惯形成 21天 66天 自动化 情境线索")
        self.assertEqual(
            {item["review_id"] for item in results[:3]},
            {
                "fritz-2020-habit-interventions-scoping-review",
                "singh-2024-health-habit-formation-systematic-review",
                "lally-2010-real-world-habit-formation",
            },
        )
        review = MODULE.concise_record(
            next(item for item in results if item["review_id"] == "singh-2024-health-habit-formation-systematic-review"),
            self.cards,
            self.relations,
        )
        self.assertEqual({item["relation"] for item in review["related_evidence"]}, {"supports", "qualifies"})
        self.assertTrue(any("不是独立复制" in item["boundary"] for item in review["related_evidence"]))
        self.assertIn("不能证明", review["safe_interpretation"])
        observational = MODULE.concise_record(
            next(item for item in results if item["review_id"] == "lally-2010-real-world-habit-formation"),
            self.cards,
            self.relations,
        )
        self.assertIn("不要把 66 天", observational["safe_interpretation"])

    def test_focus_exercise_and_food_queries_keep_new_study_boundaries(self) -> None:
        focus = MODULE.query_cards(self.cards, "自然提高专注 注意力恢复")[0]
        exercise = MODULE.query_cards(self.cards, "久坐 有氧运动 海马 运动后提神")[0]
        food = MODULE.query_cards(self.cards, "外卖 零食 超加工食品 饮食环境")[0]
        self.assertEqual(focus["review_id"], "berman-2008-nature-directed-attention")
        self.assertIn("不应承诺固定时长", focus["safe_interpretation"])
        self.assertEqual(exercise["review_id"], "erickson-2011-aerobic-exercise-hippocampus")
        self.assertIn("不能承诺个人海马增长", exercise["safe_interpretation"])
        self.assertEqual(food["review_id"], "hall-2019-ultra-processed-diet-rct")
        self.assertIn("不要把所有加工食品妖魔化", food["safe_interpretation"])

    def test_cold_exposure_query_returns_the_six_part_decision_cluster(self) -> None:
        results = MODULE.query_cards(self.cards, "cold exposure ice bath cold shower recovery safety")
        first_six = {item["review_id"] for item in results[:6]}
        self.assertEqual(
            first_six,
            {
                "sramek-2000-cold-water-physiology",
                "moore-2022-cold-water-acute-recovery-review",
                "cain-2025-cold-water-wellbeing-review",
                "malta-2021-regular-cold-water-training-adaptation-review",
                "tipton-2017-cold-water-risks-benefits-review",
                "buijze-2016-cold-shower-rct",
            },
        )
        recovery = next(item for item in results if item["review_id"] == "moore-2022-cold-water-acute-recovery-review")
        concise = MODULE.concise_record(recovery, self.cards, self.relations)
        self.assertTrue(any(item["relation_id"] == "malta-2021-qualifies-moore-2022-recovery-vs-adaptation" for item in concise["related_evidence"]))

    def test_red_light_query_preserves_purchase_and_device_boundaries(self) -> None:
        results = MODULE.query_cards(self.cards, "红光 面板 面罩 血糖 视力 皮肤 设备等效")
        ids = {item["review_id"] for item in results}
        self.assertTrue(
            {
                "powner-2024-red-light-glucose",
                "shinhmar-2021-red-light-colour-contrast",
                "jagdeo-2018-led-dermatology-review",
                "baeza-moyano-2026-commercial-led-mask-spectra",
            }
            <= ids
        )
        device = next(item for item in results if item["review_id"] == "baeza-moyano-2026-commercial-led-mask-spectra")
        self.assertIn("默认视为证据不匹配", device["safe_interpretation"])

    def test_sauna_query_preserves_association_randomized_null_and_safety_cluster(self) -> None:
        results = MODULE.query_cards(self.cards, "桑拿 热暴露 长寿 生长激素 血压 恢复 安全")
        ids = {item["review_id"] for item in results}
        self.assertTrue({
            "leppaluoto-1986-repeated-sauna-endocrine",
            "laukkanen-2018-sauna-cvd-mortality-cohort",
            "hamaya-2025-passive-heating-rct-meta-analysis",
            "debray-2023-sauna-stable-cad-rct",
            "kaiser-2023-sauna-injury-series",
            "ahokas-2025-postexercise-heat-review",
        } <= ids)
        cohort = next(item for item in results if item["review_id"] == "laukkanen-2018-sauna-cvd-mortality-cohort")
        concise = MODULE.concise_record(cohort, self.cards, self.relations)
        self.assertTrue(any(item["relation_id"] == "hamaya-2025-qualifies-laukkanen-2018-causality" for item in concise["related_evidence"]))
        self.assertIn("频率类别不是处方剂量", concise["safe_interpretation"])

    def test_breathwork_query_returns_direct_broad_and_acute_qualification_cluster(self) -> None:
        results = MODULE.query_cards(self.cards, "循环叹息 急性焦虑 压力 呼吸")
        first_three = {item["review_id"] for item in results[:3]}
        self.assertEqual(first_three, {
            "balban-2023-structured-respiration-rct",
            "fincham-2023-breathwork-stress-meta-analysis",
            "chin-2024-brief-state-anxiety-review",
        })
        balban = next(item for item in results if item["review_id"] == "balban-2023-structured-respiration-rct")
        concise = MODULE.concise_record(balban, self.cards, self.relations)
        self.assertTrue(any(item["relation_id"] == "chin-2024-qualifies-balban-2023-acute-anxiety-superiority" for item in concise["related_evidence"]))
        self.assertIn("不证明循环叹息是急性焦虑的最佳技术", concise["safe_interpretation"])

    def test_empty_query_returns_no_results(self) -> None:
        self.assertEqual(MODULE.query_cards(self.cards, "---"), [])


if __name__ == "__main__":
    unittest.main()
