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
        self.assertEqual(report["total"], 99)

    def test_unsupported_generic_request_fails_open_to_framework_help(self) -> None:
        report = MODULE.evaluate()
        case = next(item for item in report["results"] if item["case_id"] == "route-031")
        self.assertIsNone(case["actual_playbook"])

    def test_sleep_safety_cases_route_to_playbooks_with_the_required_exit(self) -> None:
        playbooks = MODULE.load_jsonl(MODULE.DEFAULT_PLAYBOOKS)
        by_id = {item["playbook_id"]: item for item in playbooks}
        expectations = {
            "route-045": ("support-trouble-falling-or-staying-asleep", "CBT-I"),
            "route-046": ("restore-daytime-energy-without-stimulant-stacking", "驾驶"),
            "route-047": ("support-trouble-falling-or-staying-asleep", "今天联系"),
            "route-048": ("decide-whether-to-try-one-health-protocol", "药师"),
            "route-049": ("manage-an-acute-stress-spike-without-overclaiming-breathwork", "危机"),
            "route-050": ("manage-an-acute-stress-spike-without-overclaiming-breathwork", "急救"),
            "route-053": ("support-ongoing-stress-worry-and-work-overload", "专业"),
            "route-064": ("manage-an-acute-stress-spike-without-overclaiming-breathwork", "急救"),
            "route-065": ("manage-an-acute-stress-spike-without-overclaiming-breathwork", "危机"),
            "route-072": ("support-weight-and-appetite-without-restrictive-protocols", "急救"),
            "route-073": ("support-weight-and-appetite-without-restrictive-protocols", "进食障碍"),
            "route-074": ("decide-whether-to-try-one-health-protocol", "医生/药师"),
            "route-075": ("decide-whether-to-try-one-health-protocol", "医生/药师"),
            "route-078": ("support-weight-and-appetite-without-restrictive-protocols", "进食障碍"),
            "route-079": ("support-weight-and-appetite-without-restrictive-protocols", "进食障碍"),
            "route-080": ("support-weight-and-appetite-without-restrictive-protocols", "医生"),
            "route-081": ("support-weight-and-appetite-without-restrictive-protocols", "妊娠"),
            "route-082": ("support-weight-and-appetite-without-restrictive-protocols", "儿童"),
            "route-083": ("support-weight-and-appetite-without-restrictive-protocols", "肾病"),
            "route-084": ("decide-whether-to-try-one-health-protocol", "受监管药房"),
            "route-088": ("reduce-alcohol-use-with-withdrawal-and-overdose-safety", "戒断"),
            "route-091": ("reduce-alcohol-use-with-withdrawal-and-overdose-safety", "安眠药"),
            "route-094": ("reduce-alcohol-use-with-withdrawal-and-overdose-safety", "孕期"),
            "route-097": ("reduce-alcohol-use-with-withdrawal-and-overdose-safety", "立即呼叫当地急救"),
        }
        report = MODULE.evaluate()
        cases = {item["case_id"]: item for item in report["results"]}
        for case_id, (playbook_id, required_text) in expectations.items():
            with self.subTest(case_id=case_id):
                self.assertEqual(cases[case_id]["actual_playbook"], playbook_id)
                self.assertIn(required_text, " ".join(by_id[playbook_id]["escalation"]))


if __name__ == "__main__":
    unittest.main()
