from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("action_playbook_validator", ROOT / "scripts" / "validate_action_playbooks.py")
QUERY = load_module("action_playbook_query", ROOT / "scripts" / "query_action_playbooks.py")
CATALOG = ROOT / "references" / "catalog"


class ActionPlaybookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playbooks = VALIDATOR.load_jsonl(CATALOG / "action-playbooks.jsonl")
        cls.cards = VALIDATOR.load_jsonl(CATALOG / "academic-study-cards.jsonl")
        cls.claims = VALIDATOR.load_jsonl(CATALOG / "claim-index.jsonl")

    def test_committed_catalog_is_valid_and_action_limited(self) -> None:
        VALIDATOR.validate_playbooks(self.playbooks, self.cards, self.claims)
        self.assertGreaterEqual(len(self.playbooks), 3)
        for playbook in self.playbooks:
            self.assertLessEqual(len(playbook["actions"]), 3)
            self.assertTrue({"evidence-supported", "bounded-experiment", "framework-inference"} & {
                action["classification"] for action in playbook["actions"]
            })

    def test_queries_route_to_the_expected_single_playbook(self) -> None:
        cases = {
            "收藏很多协议 执行不下去 习惯": "start-and-sustain-one-habit",
            "看完就忘 主动回忆 复习": "retain-what-you-learn",
            "作息漂移 晨光 睡眠": "stabilize-sleep-wake-timing",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                matches = QUERY.query_playbooks(self.playbooks, query)
                self.assertTrue(matches)
                self.assertEqual(matches[0]["playbook_id"], expected)

    def test_concise_output_keeps_execution_fields_without_evidence_dump(self) -> None:
        selected = QUERY.concise_playbook(self.playbooks[1])
        self.assertEqual(len(selected["actions"]), 3)
        for action in selected["actions"]:
            self.assertTrue({"trigger", "minimum_version", "metric", "review_after_days", "adaptation"} <= set(action))
        serialized_keys = str(selected.keys()) + str(selected["actions"][0].keys())
        for excluded in ("study_design", "sample_size", "result_summary", "provenance_urls"):
            self.assertNotIn(excluded, serialized_keys)

    def test_summaries_reject_universal_habit_deadlines_and_fixed_light_doses(self) -> None:
        by_id = {item["playbook_id"]: item for item in self.playbooks}
        habit = by_id["start-and-sustain-one-habit"]["safe_summary"]
        sleep = by_id["stabilize-sleep-wake-timing"]["safe_summary"]
        self.assertIn("不要用 21 或 66 天", habit)
        self.assertIn("不要直视太阳", sleep)
        self.assertIn("固定分钟数", sleep)

    def test_validator_rejects_more_than_three_actions_and_unknown_refs(self) -> None:
        too_many = copy.deepcopy(self.playbooks)
        extra = copy.deepcopy(too_many[0]["actions"][0])
        extra["action_id"] = "fourth"
        extra["priority"] = 4
        too_many[0]["actions"].append(extra)
        with self.assertRaisesRegex(ValueError, "one to three actions"):
            VALIDATOR.validate_playbooks(too_many, self.cards, self.claims)

        unknown = copy.deepcopy(self.playbooks)
        unknown[0]["actions"][0]["evidence_refs"] = ["unknown-evidence"]
        with self.assertRaisesRegex(ValueError, "unknown or empty evidence_refs"):
            VALIDATOR.validate_playbooks(unknown, self.cards, self.claims)

    def test_skill_forbids_invented_protocol_numbers_after_routing(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for rule in ("不得拆成更多步骤", "固定时长", "复测日程", "正确率阈值", "不是最佳处方", "替代部分重读", "可调整检查点", "即时感觉不等于长期结果", "即时成绩较低不等于长期保持更差"):
            self.assertIn(rule, skill)

    def test_renderer_labels_review_days_as_adjustable_not_optimal(self) -> None:
        rendered = QUERY.render(self.playbooks[1])
        self.assertIn("可调整的复盘点", rendered)
        self.assertIn("不是最佳间隔", rendered)


if __name__ == "__main__":
    unittest.main()
