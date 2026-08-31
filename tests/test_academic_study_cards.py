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
        self.assertGreaterEqual(len(self.cards), 7)

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
