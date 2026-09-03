#!/usr/bin/env python3
"""Evaluate natural-language playbook routing against durable user cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from query_action_playbooks import query_playbooks
    from validate_action_playbooks import load_jsonl
except ModuleNotFoundError:  # pragma: no cover
    from scripts.query_action_playbooks import query_playbooks
    from scripts.validate_action_playbooks import load_jsonl


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "references" / "evals" / "routing-user-language-v1.jsonl"
DEFAULT_PLAYBOOKS = ROOT / "references" / "catalog" / "action-playbooks.jsonl"


def evaluate(cases_path: Path = DEFAULT_CASES, playbooks_path: Path = DEFAULT_PLAYBOOKS) -> dict:
    cases = load_jsonl(cases_path)
    playbooks = load_jsonl(playbooks_path)
    results = []
    for case in cases:
        matches = query_playbooks(playbooks, case["prompt"])
        actual = matches[0]["playbook_id"] if matches else None
        results.append(
            {
                **case,
                "actual_playbook": actual,
                "passed": actual == case["expected_playbook"],
            }
        )
    passed = sum(item["passed"] for item in results)
    return {
        "schema": "huberman-routing-eval-v1",
        "passed": passed,
        "total": len(results),
        "accuracy": passed / len(results) if results else 0.0,
        "results": results,
    }


def render(report: dict) -> str:
    lines = [
        "| Case | Category | Expected | Actual | Result |",
        "|---|---|---|---|---|",
    ]
    for item in report["results"]:
        lines.append(
            f"| {item['case_id']} | {item['category']} | "
            f"{item['expected_playbook'] or 'no-match'} | {item['actual_playbook'] or 'no-match'} | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            f"Routing accuracy: {report['passed']}/{report['total']} ({report['accuracy']:.1%})",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--playbooks", type=Path, default=DEFAULT_PLAYBOOKS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = evaluate(args.cases, args.playbooks)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render(report))
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
