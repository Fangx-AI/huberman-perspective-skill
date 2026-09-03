from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(
    (ROOT / "references" / "catalog" / "episode-pages.jsonl").exists(),
    "public snapshot assertions do not apply to the maintainer's full local cache",
)
class PublicSnapshotTests(unittest.TestCase):
    def test_automatic_lifestyle_invocation_policy(self) -> None:
        policy = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(policy, r"allow_implicit_invocation:\s*true")

    def test_skill_keeps_identity_and_medical_boundaries(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("帮助用户过得更好", "即使用户没有提到 Huberman", "不冒充", "不能诊断", "默认不超过三个动作", "付费转录内容不绕过访问控制"):
            self.assertIn(phrase, skill)

    def test_academic_statuses_are_typed(self) -> None:
        path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1736)
        statuses = {row["verification_status"] for row in rows}
        self.assertTrue({"pending", "verified-study", "verified-review", "verified-observational", "verified-bibliographic"} <= statuses)
        self.assertEqual(sum(row["verification_status"] != "pending" for row in rows), 684)
        self.assertEqual(sum(row["verification_status"] == "verified-study" for row in rows), 122)
        self.assertEqual(sum(row["verification_status"] == "verified-review" for row in rows), 37)
        self.assertEqual(sum(row["verification_status"] == "verified-observational" for row in rows), 23)
        self.assertEqual(sum(row["verification_status"] == "verified-bibliographic" for row in rows), 502)

    def test_claim_index_is_locator_only(self) -> None:
        path = ROOT / "references" / "catalog" / "claim-index.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        self.assertEqual(len(records), 46)
        self.assertTrue(all("claim_text" not in record for record in records))
        self.assertTrue(all(record.get("source_urls") and record.get("youtube_ids") for record in records))
        self.assertEqual(sum(bool(record.get("timestamps")) for record in records), 25)

    def test_identifier_overrides_are_traceable(self) -> None:
        path = ROOT / "references" / "catalog" / "academic-identifier-overrides.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 1)
        for row in rows:
            self.assertTrue(row["provenance_url"].startswith("https://"))
            self.assertTrue(any(row[field] for field in ("pmcid", "pmid", "doi", "pii")))

    def test_public_graph_has_no_show_notes_payload(self) -> None:
        path = ROOT / "references" / "catalog" / "knowledge-graph.json"
        raw = path.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r'"show_notes"\s*:', raw))
        graph = json.loads(raw)
        self.assertEqual(graph["schema"], "public-evidence-v2")
        self.assertEqual(graph["stats"]["episode_nodes"], 425)
        self.assertEqual(graph["stats"]["claim_nodes"], 46)
        self.assertEqual(graph["stats"]["verified_academic_resource_nodes"], 726)
        cards_path = ROOT / "references" / "catalog" / "academic-study-cards.jsonl"
        cards = [json.loads(line) for line in cards_path.read_text(encoding="utf-8").splitlines() if line]
        expected_findings = sum(1 + len(card["null_findings"]) for card in cards)
        expected_limitations = sum(len(card["limitations"]) for card in cards)
        evidence_relations = [
            json.loads(line)
            for line in (ROOT / "references" / "catalog" / "evidence-relations.jsonl").read_text(encoding="utf-8").splitlines()
            if line
        ]
        self.assertEqual(graph["stats"]["study_card_nodes"], len(cards))
        self.assertEqual(graph["stats"]["study_finding_nodes"], expected_findings)
        self.assertEqual(graph["stats"]["study_limitation_nodes"], expected_limitations)
        self.assertEqual(graph["stats"]["evidence_relation_nodes"], len(evidence_relations))
        relations = [edge["relation"] for edge in graph["edges"]]
        self.assertEqual(relations.count("reports_null_finding"), sum(len(card["null_findings"]) for card in cards))
        self.assertEqual(relations.count("has_limitation"), expected_limitations)
        self.assertEqual(relations.count("has_evidence_relation"), len(evidence_relations))
        self.assertEqual(
            sum(relations.count(kind) for kind in {"replicates", "supports", "qualifies", "challenges", "contradicts"}),
            len(evidence_relations),
        )

    def test_repair_queue_matches_pending_urls(self) -> None:
        academic_path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        repair_path = ROOT / "references" / "catalog" / "academic-repair-queue.csv"
        with academic_path.open(encoding="utf-8-sig", newline="") as handle:
            pending_urls = {row["url"] for row in csv.DictReader(handle) if row["verification_status"] == "pending"}
        with repair_path.open(encoding="utf-8-sig", newline="") as handle:
            repair_urls = {row["url"] for row in csv.DictReader(handle)}
        self.assertEqual(repair_urls, pending_urls)

    def test_study_cards_preserve_negative_findings_and_match_queue(self) -> None:
        cards_path = ROOT / "references" / "catalog" / "academic-study-cards.jsonl"
        queue_path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        cards = [json.loads(line) for line in cards_path.read_text(encoding="utf-8").splitlines() if line]
        with queue_path.open(encoding="utf-8-sig", newline="") as handle:
            by_url = {row["url"]: row for row in csv.DictReader(handle)}
        self.assertGreaterEqual(len(cards), 26)
        for card in cards:
            self.assertTrue(card["null_findings"])
            self.assertTrue(card["limitations"])
            self.assertTrue(card["safe_interpretation"])
            self.assertTrue(all(url.startswith("https://") for url in card["provenance_urls"]))
            queue_urls = card.get("queue_urls", card["source_urls"])
            for url in queue_urls:
                self.assertEqual(by_url[url]["verification_status"], card["verification_status"])
                self.assertEqual(by_url[url]["evidence_notes"], card["queue_note"])
        external = [card for card in cards if card.get("source_scope") == "external-context"]
        self.assertGreaterEqual(len(external), 9)
        self.assertTrue(all(card.get("queue_urls") == [] for card in external))


if __name__ == "__main__":
    unittest.main()
