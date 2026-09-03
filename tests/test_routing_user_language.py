from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("evaluate_routing", ROOT / "scripts" / "evaluate_routing.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class UserLanguageRoutingTests(unittest.TestCase):
    def test_market_language_cases_route_without_unrelated_playbooks(self) -> None:
        report = MODULE.evaluate()
        failures = [
            f"{item['case_id']}: {item['actual_playbook']} != {item['expected_playbook']}"
            for item in report["results"]
            if not item["passed"]
        ]
        self.assertEqual(failures, [])
        self.assertGreaterEqual(report["total"], 30)

    def test_unsupported_generic_request_fails_open_to_framework_help(self) -> None:
        report = MODULE.evaluate()
        case = next(item for item in report["results"] if item["case_id"] == "route-031")
        self.assertIsNone(case["actual_playbook"])


if __name__ == "__main__":
    unittest.main()
