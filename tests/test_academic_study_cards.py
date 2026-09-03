from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("study_cards", ROOT / "scripts" / "apply_academic_study_cards.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class AcademicStudyCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cards = MODULE.load_cards(ROOT / "references" / "catalog" / "academic-study-cards.jsonl")

    def test_cards_validate(self) -> None:
        MODULE.validate_cards(self.cards)
        self.assertGreaterEqual(len(self.cards), 26)

    def test_cold_exposure_cluster_separates_proxy_recovery_adaptation_and_safety(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "sramek-2000-cold-water-physiology",
            "moore-2022-cold-water-acute-recovery-review",
            "cain-2025-cold-water-wellbeing-review",
            "malta-2021-regular-cold-water-training-adaptation-review",
            "tipton-2017-cold-water-risks-benefits-review",
            "buijze-2016-cold-shower-rct",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertEqual(by_id["sramek-2000-cold-water-physiology"]["sample_size"], 10)
        self.assertIn("患病天数没有显著", " ".join(by_id["buijze-2016-cold-shower-rct"]["null_findings"]))
        self.assertIn("长期力量增长", by_id["moore-2022-cold-water-acute-recovery-review"]["safe_interpretation"])
        for review_id in expected - {"sramek-2000-cold-water-physiology", "moore-2022-cold-water-acute-recovery-review"}:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_sauna_cluster_separates_association_hormone_spikes_nulls_and_safety(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "leppaluoto-1986-repeated-sauna-endocrine",
            "podstawski-2021-sauna-cold-endocrine",
            "laukkanen-2018-sauna-cvd-mortality-cohort",
            "laukkanen-2015-sauna-mortality-cohort",
            "pizzey-2021-heat-vascular-meta-analysis",
            "hamaya-2025-passive-heating-rct-meta-analysis",
            "debray-2023-sauna-stable-cad-rct",
            "kaiser-2023-sauna-injury-series",
            "ahokas-2025-postexercise-heat-review",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("睾酮", " ".join(by_id["leppaluoto-1986-repeated-sauna-endocrine"]["null_findings"]))
        self.assertIn("HbA1c", " ".join(by_id["hamaya-2025-passive-heating-rct-meta-analysis"]["null_findings"]))
        self.assertIn("热适应指标变化不等于", " ".join(by_id["debray-2023-sauna-stable-cad-rct"]["null_findings"]))
        self.assertIn("总使用人次分母", " ".join(by_id["kaiser-2023-sauna-injury-series"]["null_findings"]))
        for review_id in expected - {
            "leppaluoto-1986-repeated-sauna-endocrine",
            "podstawski-2021-sauna-cold-endocrine",
            "laukkanen-2018-sauna-cvd-mortality-cohort",
        }:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_breathwork_cluster_separates_mood_signal_acute_nulls_and_clinical_boundaries(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "balban-2023-structured-respiration-rct",
            "fincham-2023-breathwork-stress-meta-analysis",
            "chin-2024-brief-state-anxiety-review",
        }
        self.assertTrue(expected <= set(by_id))
        balban = by_id["balban-2023-structured-respiration-rct"]
        self.assertEqual(balban["sample_size"], 108)
        self.assertIn("没有被证明在状态焦虑下降上优于正念", " ".join(balban["null_findings"]))
        self.assertIn("睡眠时长", " ".join(balban["null_findings"]))
        self.assertIn("回顾完成", " ".join(balban["limitations"]))
        fincham = by_id["fincham-2023-breathwork-stress-meta-analysis"]
        self.assertIn("12项RCT、785名成人", fincham["sample_size"])
        self.assertIn("未见显著剂量—反应", " ".join(fincham["null_findings"]))
        chin = by_id["chin-2024-brief-state-anxiety-review"]
        self.assertIn("总体没有显著降低状态焦虑", " ".join(chin["null_findings"]))
        self.assertEqual(chin["source_scope"], "external-context")
        self.assertEqual(chin["queue_urls"], [])

    def test_daytime_energy_cluster_separates_short_term_state_sleep_and_clinical_triage(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "dempsey-2016-walking-breaks-fatigue",
            "stanyer-2024-caffeine-dose-timing-sleep",
            "kapur-2017-osa-diagnostic-guideline",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("执行功能", " ".join(by_id["dempsey-2016-walking-breaks-fatigue"]["null_findings"]))
        self.assertIn("主观感觉可能漏掉", by_id["stanyer-2024-caffeine-dose-timing-sleep"]["safe_interpretation"])
        self.assertIn("症状不能由Skill诊断", by_id["kapur-2017-osa-diagnostic-guideline"]["safe_interpretation"])
        for review_id in expected:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_insomnia_guidelines_support_cbt_i_without_universal_self_treatment(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        aasm = by_id["edinger-2021-insomnia-behavioral-guideline"]
        va_dod = by_id["va-dod-2025-insomnia-osa-guideline"]
        self.assertIn("CBT-I", aasm["result_summary"])
        self.assertIn("睡眠卫生", " ".join(aasm["null_findings"]))
        self.assertIn("驾驶", " ".join(aasm["limitations"]))
        self.assertIn("双相", va_dod["safe_interpretation"])
        self.assertIn("日间困倦", " ".join(va_dod["limitations"]) + va_dod["safe_interpretation"])
        for card in (aasm, va_dod):
            self.assertEqual(card["source_scope"], "external-context")
            self.assertEqual(card["queue_urls"], [])

    def test_ongoing_stress_cards_separate_work_conditions_self_help_and_clinical_care(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        work = by_id["who-2022-mental-health-at-work-guideline"]
        care = by_id["nice-2024-gad-panic-guideline"]
        toolkit = by_id["who-2020-doing-what-matters-stress-guide"]
        self.assertIn("过量工作", work["result_summary"])
        self.assertIn("不能被缩减", work["queue_note"])
        self.assertIn("功能损害", care["result_summary"])
        self.assertIn("非处方药", " ".join(care["null_findings"]))
        self.assertIn("过量工作", toolkit["safe_interpretation"] + " ".join(toolkit["null_findings"]))
        for card in (work, care, toolkit):
            self.assertEqual(card["source_scope"], "external-context")
            self.assertEqual(card["queue_urls"], [])

    def test_weight_cluster_keeps_user_support_eating_disorders_and_medication_safety_separate(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "nice-2025-overweight-obesity-management-guideline",
            "nice-2017-eating-disorders-recognition-treatment-guideline",
            "niddk-2023-factors-affecting-weight-health",
            "niddk-prescription-weight-management-medications",
            "fda-2026-unapproved-glp1-weight-loss-warning",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("非污名", by_id["nice-2025-overweight-obesity-management-guideline"]["result_summary"])
        self.assertIn("限制性节食可能触发暴食", by_id["nice-2017-eating-disorders-recognition-treatment-guideline"]["result_summary"])
        self.assertIn("环境、睡眠、药物、健康状况", by_id["niddk-2023-factors-affecting-weight-health"]["result_summary"])
        self.assertIn("医疗专业人员共同决定", by_id["niddk-prescription-weight-management-medications"]["result_summary"])
        self.assertIn("剂量错误", by_id["fda-2026-unapproved-glp1-weight-loss-warning"]["result_summary"])
        for review_id in expected:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_alcohol_cluster_separates_reduction_withdrawal_overdose_interactions_and_pregnancy(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "niaaa-rethinking-drinking-cut-down-or-quit",
            "asam-2020-alcohol-withdrawal-management-guideline",
            "niaaa-alcohol-overdose-danger-signs",
            "niaaa-alcohol-medication-interactions",
            "cdc-2026-alcohol-pregnancy",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("个人共同决定", by_id["niaaa-rethinking-drinking-cut-down-or-quit"]["result_summary"])
        self.assertIn("停止自行实验", by_id["asam-2020-alcohol-withdrawal-management-guideline"]["safe_interpretation"])
        self.assertIn("咖啡、冷水澡", by_id["niaaa-alcohol-overdose-danger-signs"]["null_findings"][2])
        self.assertIn("抑制呼吸", by_id["niaaa-alcohol-medication-interactions"]["result_summary"])
        self.assertIn("没有已知安全", by_id["cdc-2026-alcohol-pregnancy"]["result_summary"])
        for review_id in expected:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_phone_cluster_keeps_bedtime_reduction_attention_and_rebound_separate(self) -> None:
        by_id = {card["review_id"]: card for card in self.cards}
        expected = {
            "jeoung-2023-bedtime-procrastination-rct",
            "hill-2025-resto-bedtime-procrastination-pilot",
            "valshtein-2020-mcii-bedtime-procrastination-trials",
            "brailovskaia-2023-smartphone-reduction-vs-abstinence",
            "pieh-2025-smartphone-screen-time-reduction-rct",
            "mertens-2026-wellspent-social-media-rct",
            "stothart-2015-phone-notification-attention-experiment",
        }
        self.assertTrue(expected <= set(by_id))
        self.assertIn("开放标签", " ".join(by_id["jeoung-2023-bedtime-procrastination-rct"]["limitations"]))
        self.assertIn("活性对照", by_id["hill-2025-resto-bedtime-procrastination-pilot"]["result_summary"])
        self.assertIn("不要求数字排毒", by_id["brailovskaia-2023-smartphone-reduction-vs-abstinence"]["safe_interpretation"])
        self.assertIn("反弹", by_id["pieh-2025-smartphone-screen-time-reduction-rct"]["safe_interpretation"])
        self.assertIn("未显著改善", " ".join(by_id["mertens-2026-wellspent-social-media-rct"]["null_findings"]))
        self.assertIn("必要联络", by_id["stothart-2015-phone-notification-attention-experiment"]["safe_interpretation"])
        for review_id in expected:
            self.assertEqual(by_id[review_id]["source_scope"], "external-context")
            self.assertEqual(by_id[review_id]["queue_urls"], [])

    def test_review_card_uses_review_scope_instead_of_fake_sample_count(self) -> None:
        card = next(item for item in self.cards if item["review_id"] == "dunlosky-2013-effective-learning-techniques-review")
        self.assertEqual(card["verification_status"], "verified-review")
        self.assertIsInstance(card["sample_size"], str)
        self.assertIn("叙述性综述", card["sample_size"])

    def test_sample_size_schema_rejects_empty_review_scope_and_nonpositive_study_counts(self) -> None:
        review = dict(next(item for item in self.cards if item["verification_status"] == "verified-review"))
        review["sample_size"] = "  "
        with self.assertRaisesRegex(ValueError, "review-scope"):
            MODULE.validate_cards([review])
        study = dict(next(item for item in self.cards if item["verification_status"] == "verified-study"))
        for invalid in (0, True, "40"):
            with self.subTest(invalid=invalid):
                study["sample_size"] = invalid
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    MODULE.validate_cards([study])

    def test_stothard_card_uses_the_exact_circadian_article_url(self) -> None:
        card = next(item for item in self.cards if item["review_id"] == "stothard-2017-natural-light-seasons-weekend")
        self.assertEqual(
            MODULE.queue_urls(card),
            ["https://www.cell.com/current-biology/fulltext/S0960-9822(16)31522-6"],
        )
        self.assertEqual(card["search_aliases"], ["stothart"])
        self.assertNotIn("S0960-9822(17)30504-3", " ".join(card["provenance_urls"]))

    def test_application_is_idempotent(self) -> None:
        rows = [
            {"url": url, "verification_status": "verified-bibliographic", "evidence_notes": ""}
            for card in self.cards
            for url in MODULE.queue_urls(card)
        ]
        expected_changes = sum(len(MODULE.queue_urls(card)) for card in self.cards)
        self.assertEqual(MODULE.apply_cards(rows, self.cards), expected_changes)
        self.assertEqual(MODULE.apply_cards(rows, self.cards), 0)

    def test_pending_record_cannot_be_promoted(self) -> None:
        card = self.cards[0]
        rows = [{"url": url, "verification_status": "pending", "evidence_notes": ""} for url in card["source_urls"]]
        with self.assertRaisesRegex(ValueError, "bibliographic verification is required"):
            MODULE.apply_cards(rows, [card])

    def test_external_context_card_does_not_require_queue_mutation(self) -> None:
        card = next(item for item in self.cards if item.get("source_scope") == "external-context")
        self.assertEqual(MODULE.queue_urls(card), [])
        self.assertEqual(MODULE.apply_cards([], [card]), 0)


if __name__ == "__main__":
    unittest.main()
