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

    def test_external_counterevidence_becomes_a_bounded_relation_node(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            episode_path = work / "episodes.jsonl"
            cards_path = work / "cards.jsonl"
            relations_path = work / "relations.jsonl"
            output_path = work / "graph.json"
            episode_path.write_text(
                json.dumps(
                    {
                        "fetch_ok": True,
                        "episode_id": "demo",
                        "url": "https://www.hubermanlab.com/episode/demo",
                        "title": "Demo",
                        "resource_urls": [],
                        "topics": [],
                        "youtube_urls": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            base = {
                "doi": "10.0000/demo",
                "provenance_urls": ["https://example.org/source"],
                "verification_status": "verified-study",
                "evidence_level": "A-Direct",
                "topic_tags": ["sleep"],
                "study_design": "experiment",
                "sample_size": 10,
                "population": "adults",
                "intervention_exposure": "training",
                "comparator": "control",
                "outcomes": ["performance"],
                "result_summary": "result",
                "null_findings": ["null"],
                "limitations": ["bounded"],
                "safe_interpretation": "bounded",
                "queue_note": "reviewed",
                "reviewed_at": "2026-08-31",
            }
            target = {**base, "review_id": "target", "title": "Target", "source_urls": ["https://example.org/target"]}
            source = {
                **base,
                "review_id": "source",
                "title": "Source",
                "source_urls": ["https://example.org/external"],
                "source_scope": "external-context",
                "queue_urls": [],
            }
            cards_path.write_text(
                json.dumps(target) + "\n" + json.dumps(source) + "\n",
                encoding="utf-8",
            )
            evidence_relation = {
                "relation_id": "source-challenges-target",
                "source_review_id": "source",
                "relation": "challenges",
                "target_review_id": "target",
                "claim_scope": "enhancement",
                "rationale": "controlled analysis",
                "boundary": "does not reject stabilization",
                "provenance_urls": ["https://example.org/external"],
                "reviewed_at": "2026-08-31",
            }
            relations_path.write_text(json.dumps(evidence_relation) + "\n", encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_knowledge_graph.py"),
                    "--input",
                    str(episode_path),
                    "--output",
                    str(output_path),
                    "--study-cards",
                    str(cards_path),
                    "--evidence-relations",
                    str(relations_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            graph = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(graph["schema"], "episode-topic-platform-claim-study-relation-v5")
            self.assertEqual(graph["stats"]["evidence_relation_nodes"], 1)
            external_resource = next(
                node for node in graph["nodes"] if node.get("url") == "https://example.org/external"
            )
            self.assertEqual(external_resource["source_scope"], "external-context")
            edge_relations = {edge["relation"] for edge in graph["edges"]}
            self.assertTrue({"has_evidence_relation", "challenges"} <= edge_relations)

    def test_action_playbook_becomes_executable_graph_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            episode_path = work / "episodes.jsonl"
            cards_path = work / "cards.jsonl"
            claims_path = work / "claims.jsonl"
            playbooks_path = work / "playbooks.jsonl"
            output_path = work / "graph.json"
            episode_path.write_text(
                json.dumps({"fetch_ok": True, "episode_id": "demo", "url": "https://example.org/episode", "topics": [], "youtube_urls": [], "resource_urls": []}) + "\n",
                encoding="utf-8",
            )
            card = {
                "review_id": "demo-study", "title": "Demo", "source_urls": [], "provenance_urls": [],
                "verification_status": "verified-study", "evidence_level": "A-Direct", "topic_tags": [],
                "study_design": "experiment", "sample_size": 10, "population": "adults",
                "intervention_exposure": "practice", "comparator": "control", "outcomes": ["outcome"],
                "result_summary": "result", "null_findings": ["null"], "limitations": ["limit"],
                "safe_interpretation": "bounded", "reviewed_at": "2026-08-31",
            }
            cards_path.write_text(json.dumps(card) + "\n", encoding="utf-8")
            claims_path.write_text(json.dumps({"claim_id": "demo-claim", "claim_text": "context"}) + "\n", encoding="utf-8")
            playbook = {
                "playbook_id": "demo-plan", "title": "Demo plan", "user_goal": "act", "aliases": [],
                "scope": "low risk", "first_questions": [], "baseline_checks": [], "safe_summary": "start",
                "not_for": [], "escalation": [], "last_reviewed": "2026-08-31",
                "evidence_links": [{"review_id": "demo-study"}], "claim_links": [{"claim_id": "demo-claim"}],
                "actions": [{"action_id": "do-one", "priority": 1, "classification": "bounded-experiment",
                             "action": "Do one", "why": "test", "trigger": "after cue", "minimum_version": "one",
                             "metric": "done", "review_after_days": 7, "adaptation": "adjust", "stop_conditions": ["stop"],
                             "evidence_refs": ["demo-study", "demo-claim"]}],
            }
            playbooks_path.write_text(json.dumps(playbook) + "\n", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_knowledge_graph.py"), "--input", str(episode_path),
                 "--output", str(output_path), "--claims", str(claims_path), "--study-cards", str(cards_path),
                 "--action-playbooks", str(playbooks_path)],
                check=True, capture_output=True, text=True,
            )
            graph = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(graph["schema"], "episode-topic-platform-claim-study-relation-action-v6")
            self.assertEqual(graph["stats"]["action_playbook_nodes"], 1)
            self.assertEqual(graph["stats"]["action_step_nodes"], 1)
            relations = {edge["relation"] for edge in graph["edges"]}
            self.assertTrue({"has_action", "uses_study_evidence", "uses_claim_context", "grounded_in"} <= relations)


if __name__ == "__main__":
    unittest.main()
