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

    def test_empty_query_returns_no_results(self) -> None:
        self.assertEqual(MODULE.query_cards(self.cards, "---"), [])


if __name__ == "__main__":
    unittest.main()
