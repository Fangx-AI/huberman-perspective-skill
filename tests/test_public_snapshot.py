from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicSnapshotTests(unittest.TestCase):
    def test_explicit_only_policy(self) -> None:
        policy = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(policy, r"allow_implicit_invocation:\s*false")

    def test_skill_keeps_identity_and_medical_boundaries(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("不冒充", "不能诊断", "证据阶梯", "不把受版权保护的完整转录"):
            self.assertIn(phrase, skill)

    def test_academic_statuses_are_typed(self) -> None:
        path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 749)
        statuses = {row["verification_status"] for row in rows}
        self.assertTrue({"pending", "verified-study", "verified-review", "verified-observational", "verified-bibliographic"} <= statuses)
        self.assertEqual(sum(row["verification_status"] != "pending" for row in rows), 674)

    def test_claim_index_is_locator_only(self) -> None:
        path = ROOT / "references" / "catalog" / "claim-index.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        self.assertEqual(len(records), 40)
        self.assertTrue(all("claim_text" not in record for record in records))
        self.assertTrue(all(record.get("source_urls") and record.get("youtube_ids") for record in records))
        self.assertEqual(sum(bool(record.get("timestamps")) for record in records), 19)

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
        self.assertEqual(graph["schema"], "public-claim-v1")
        self.assertEqual(graph["stats"]["episode_nodes"], 425)
        self.assertEqual(graph["stats"]["claim_nodes"], 40)
        self.assertEqual(graph["stats"]["verified_academic_resource_nodes"], 673)

    def test_repair_queue_matches_pending_urls(self) -> None:
        academic_path = ROOT / "references" / "catalog" / "academic-verification-queue.csv"
        repair_path = ROOT / "references" / "catalog" / "academic-repair-queue.csv"
        with academic_path.open(encoding="utf-8-sig", newline="") as handle:
            pending_urls = {row["url"] for row in csv.DictReader(handle) if row["verification_status"] == "pending"}
        with repair_path.open(encoding="utf-8-sig", newline="") as handle:
            repair_urls = {row["url"] for row in csv.DictReader(handle)}
        self.assertEqual(repair_urls, pending_urls)


if __name__ == "__main__":
    unittest.main()
