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
        self.assertGreaterEqual(len(self.relations), 7)

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
