from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class KnowledgeGraphBuilderTests(unittest.TestCase):
    def test_study_cards_become_auditable_graph_relations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            episode_path = work / "episodes.jsonl"
            queue_path = work / "queue.csv"
            cards_path = work / "cards.jsonl"
            output_path = work / "graph.json"
            resource_url = "https://example.org/paper"
            episode_path.write_text(
                json.dumps(
                    {
                        "fetch_ok": True,
                        "episode_id": "demo",
                        "url": "https://www.hubermanlab.com/episode/demo",
                        "title": "Demo",
                        "resource_urls": [resource_url],
                        "topics": [],
                        "youtube_urls": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with queue_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "url",
                        "episode_count",
                        "episode_ids",
                        "episode_title_sample",
                        "verification_status",
                        "evidence_notes",
                    ],
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "url": resource_url,
                        "episode_count": "1",
                        "episode_ids": "demo",
                        "episode_title_sample": "Demo",
                        "verification_status": "verified-study",
                        "evidence_notes": "reviewed",
                    }
                )
            card = {
                "review_id": "demo-study",
                "title": "Demo study",
                "doi": "10.0000/demo",
                "source_urls": [resource_url],
                "provenance_urls": [resource_url],
                "verification_status": "verified-study",
                "evidence_level": "A-Direct",
                "topic_tags": ["sleep"],
                "study_design": "randomized",
                "sample_size": 10,
                "population": "healthy adults",
                "intervention_exposure": "demo",
                "comparator": "control",
                "outcomes": ["outcome"],
                "result_summary": "bounded result",
                "null_findings": ["null result"],
                "limitations": ["small sample"],
                "safe_interpretation": "do not generalize",
                "reviewed_at": "2026-08-31",
            }
            cards_path.write_text(json.dumps(card) + "\n", encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_knowledge_graph.py"),
                    "--input",
                    str(episode_path),
                    "--output",
                    str(output_path),
                    "--academic",
                    str(queue_path),
                    "--study-cards",
                    str(cards_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            graph = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(graph["schema"], "episode-topic-platform-claim-study-v4")
            self.assertEqual(graph["stats"]["study_card_nodes"], 1)
            self.assertEqual(graph["stats"]["study_finding_nodes"], 2)
            self.assertEqual(graph["stats"]["study_limitation_nodes"], 1)
            relations = [edge["relation"] for edge in graph["edges"]]
            for relation in ("reviews_resource", "reports_result", "reports_null_finding", "has_limitation"):
                self.assertIn(relation, relations)


if __name__ == "__main__":
    unittest.main()
