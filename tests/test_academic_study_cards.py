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
        self.assertGreaterEqual(len(self.cards), 20)

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
