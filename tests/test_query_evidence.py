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

    def test_empty_query_returns_no_results(self) -> None:
        self.assertEqual(MODULE.query_cards(self.cards, "---"), [])


if __name__ == "__main__":
    unittest.main()
