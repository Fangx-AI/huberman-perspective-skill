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
