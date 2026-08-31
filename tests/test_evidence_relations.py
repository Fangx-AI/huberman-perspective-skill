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
        self.assertGreaterEqual(len(self.relations), 3)

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
