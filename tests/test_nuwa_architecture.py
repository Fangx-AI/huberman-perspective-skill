from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_checkpoint", ROOT / "scripts" / "research_checkpoint.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class NuwaArchitectureTests(unittest.TestCase):
    def test_all_research_dimensions_are_durable_and_traceable(self) -> None:
        checkpoint = MODULE.build_checkpoint(ROOT)
        self.assertEqual(checkpoint["schema"], "huberman-research-checkpoint-v1")
        self.assertEqual(checkpoint["summary"]["present_dimensions"], 7)
        self.assertGreaterEqual(checkpoint["summary"]["unique_locator_urls"], 10)
        self.assertTrue(all(item["sections"] for item in checkpoint["dimensions"]))

    def test_missing_dimension_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = MODULE.build_checkpoint(Path(directory))
        self.assertEqual(checkpoint["summary"]["present_dimensions"], 0)
        self.assertTrue(all(item["status"] == "missing" for item in checkpoint["dimensions"]))

    def test_architecture_links_research_model_action_and_evaluation(self) -> None:
        architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for phrase in (
            "references/research/",
            "extraction-framework.md",
            "huberman-operating-model.md",
            "action-playbooks.jsonl",
            "independent scoring Agent",
            "不以第一人称扮演 Huberman",
        ):
            self.assertIn(phrase, architecture)

    def test_operating_models_include_evidence_application_and_limits(self) -> None:
        model = (ROOT / "references" / "huberman-operating-model.md").read_text(encoding="utf-8")
        self.assertEqual(model.count("## 模型"), 5)
        self.assertEqual(model.count("**怎样帮助用户**"), 5)
        self.assertEqual(model.count("**局限**"), 5)
        self.assertIn("核心张力", model)
        self.assertIn("不冒充 Andrew Huberman", model)

    def test_fidelity_scorecard_prioritizes_user_value_and_safety(self) -> None:
        scorecard = (ROOT / "references" / "fidelity-scorecard.md").read_text(encoding="utf-8")
        for phrase in ("用户结果效用", "医疗与安全", "答题 Agent 与评分 Agent 必须独立", "安全封顶规则"):
            self.assertIn(phrase, scorecard)
        self.assertIn("| 用户结果效用 | 30 |", scorecard)
        self.assertIn("| 医疗与安全 | 20 |", scorecard)

    def test_latest_fidelity_report_is_independent_and_records_residual_risk(self) -> None:
        report = (ROOT / "FIDELITY.md").read_text(encoding="utf-8")
        self.assertIn("94/100 · 等级 A", report)
        self.assertIn("两个独立 Agent", report)
        self.assertIn("## 残余风险", report)
        self.assertIn("不能全部归因于代码改动", report)


if __name__ == "__main__":
    unittest.main()
