from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evidence_relations", ROOT / "scripts" / "validate_evidence_relations.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EvidenceRelationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cards = MODULE.load_jsonl(ROOT / "references" / "catalog" / "academic-study-cards.jsonl")
        cls.relations = MODULE.load_jsonl(ROOT / "references" / "catalog" / "evidence-relations.jsonl")

    def test_committed_relations_validate(self) -> None:
        MODULE.validate_relations(self.cards, self.relations)
        self.assertGreaterEqual(len(self.relations), 14)

    def test_cold_exposure_relations_keep_short_term_recovery_and_long_term_adaptation_separate(self) -> None:
        relation = next(
            item
            for item in self.relations
            if item["relation_id"] == "malta-2021-qualifies-moore-2022-recovery-vs-adaptation"
        )
        self.assertEqual(relation["relation"], "qualifies")
        self.assertIn("短期", relation["rationale"])
        self.assertIn("长期", relation["rationale"])
        immunity = next(
            item
            for item in self.relations
            if item["relation_id"] == "buijze-2016-qualifies-cain-2025-immunity"
        )
        self.assertIn("患病天数没有显著变化", immunity["rationale"])

    def test_natural_light_followup_is_support_not_independent_replication(self) -> None:
        relation = next(
            item
            for item in self.relations
            if item["relation_id"] == "stothard-2017-supports-wright-2013-natural-light-entrainment"
        )
        self.assertEqual(relation["relation"], "supports")
        self.assertIn("不是独立复制", relation["boundary"])
        self.assertIn("作者重叠", relation["boundary"])

    def test_retrieval_followup_is_support_not_independent_replication(self) -> None:
        relation = next(
            item
            for item in self.relations
            if item["relation_id"] == "karpicke-roediger-2008-supports-roediger-karpicke-2006-delayed-retrieval"
        )
        self.assertEqual(relation["relation"], "supports")
        self.assertIn("不是独立复制", relation["boundary"])

    def test_narrative_review_qualifies_both_retrieval_experiments(self) -> None:
        relations = [
            item
            for item in self.relations
            if item["source_review_id"] == "dunlosky-2013-effective-learning-techniques-review"
        ]
        self.assertEqual(len(relations), 2)
        self.assertTrue(all(item["relation"] == "qualifies" for item in relations))
        self.assertTrue(any("不是荟萃分析" in item["boundary"] for item in relations))

    def test_sauna_relations_keep_cohort_association_hormone_spikes_and_rct_nulls_separate(self) -> None:
        causality = next(
            item for item in self.relations
            if item["relation_id"] == "hamaya-2025-qualifies-laukkanen-2018-causality"
        )
        self.assertEqual(causality["relation"], "qualifies")
        self.assertIn("不能把关联梯度当成因果剂量", causality["rationale"])
        hormones = next(
            item for item in self.relations
            if item["relation_id"] == "podstawski-2021-qualifies-leppaluoto-1986-hormone-optimization"
        )
        self.assertIn("睾酮", hormones["rationale"])
        self.assertIn("不构成严格复制", hormones["boundary"])
        safety = next(
            item for item in self.relations
            if item["relation_id"] == "kaiser-2023-qualifies-laukkanen-2018-sauna-safety"
        )
        self.assertIn("没有总暴露分母", safety["boundary"])

    def test_breathwork_relations_separate_broad_stress_acute_anxiety_and_specific_technique(self) -> None:
        broad = next(
            item for item in self.relations
            if item["relation_id"] == "fincham-2023-supports-balban-2023-broad-breathwork-context"
        )
        self.assertEqual(broad["relation"], "supports")
        self.assertIn("未纳入循环叹息", broad["boundary"])
        acute = next(
            item for item in self.relations
            if item["relation_id"] == "chin-2024-qualifies-balban-2023-acute-anxiety-superiority"
        )
        self.assertEqual(acute["relation"], "qualifies")
        self.assertIn("状态焦虑", acute["rationale"])
        transfer = next(
            item for item in self.relations
            if item["relation_id"] == "chin-2024-qualifies-fincham-2023-acute-transfer"
        )
        self.assertIn("不构成直接矛盾", transfer["boundary"])

    def test_daytime_energy_relation_blocks_self_treating_sleep_disorder_signals(self) -> None:
        relation = next(
            item for item in self.relations
            if item["relation_id"] == "kapur-2017-qualifies-dempsey-2016-fatigue-self-management"
        )
        self.assertEqual(relation["relation"], "qualifies")
        self.assertIn("短暂走动不能充当", relation["rationale"])
        self.assertIn("停止生活实验", relation["boundary"])

    def test_insomnia_relation_blocks_universal_sleep_restriction(self) -> None:
        relation = next(
            item
            for item in self.relations
            if item["relation_id"] == "va-dod-2025-qualifies-edinger-2021-self-directed-sleep-restriction"
        )
        self.assertEqual(relation["relation"], "qualifies")
        self.assertIn("固定睡眠窗口", relation["boundary"])
        self.assertIn("双相障碍", relation["rationale"])

    def test_ongoing_stress_relations_block_individualizing_work_and_clinical_problems(self) -> None:
        work = next(
            item for item in self.relations
            if item["relation_id"] == "who-2022-qualifies-who-2020-individual-coping-at-work"
        )
        care = next(
            item for item in self.relations
            if item["relation_id"] == "nice-2024-qualifies-who-2020-self-help-for-persistent-anxiety"
        )
        self.assertEqual(work["relation"], "qualifies")
        self.assertIn("结构性问题", work["boundary"])
        self.assertIn("固定天数", care["boundary"])
        self.assertIn("功能", care["rationale"])

    def test_weight_relations_block_shame_restrictive_dieting_and_unapproved_glp1(self) -> None:
        by_id = {item["relation_id"]: item for item in self.relations}
        expected = {
            "nice-2025-qualifies-hall-2019-food-environment-for-weight-management",
            "nice-2017-eating-disorders-qualifies-weight-loss-self-help",
            "niddk-2023-qualifies-single-cause-weight-narratives",
            "fda-2026-qualifies-niddk-prescription-glp1-options",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("不是完整治疗", by_id["nice-2025-qualifies-hall-2019-food-environment-for-weight-management"]["rationale"])
        self.assertIn("不给减脂、断食", by_id["nice-2017-eating-disorders-qualifies-weight-loss-self-help"]["boundary"])
        self.assertIn("不得羞辱用户", by_id["niddk-2023-qualifies-single-cause-weight-narratives"]["boundary"])
        self.assertIn("不得给复配浓度换算", by_id["fda-2026-qualifies-niddk-prescription-glp1-options"]["boundary"])

    def test_unknown_card_is_rejected(self) -> None:
        relation = dict(self.relations[0])
        relation["target_review_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown study card"):
            MODULE.validate_relations(self.cards, [relation])

    def test_self_relation_is_rejected(self) -> None:
        relation = dict(self.relations[0])
        relation["target_review_id"] = relation["source_review_id"]
        with self.assertRaisesRegex(ValueError, "same study card"):
            MODULE.validate_relations(self.cards, [relation])


if __name__ == "__main__":
    unittest.main()
