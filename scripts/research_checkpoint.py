#!/usr/bin/env python3
"""Summarize durable research dimensions before framework synthesis."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIMENSIONS = (
    ("01-writings.md", "著作与系统思考"),
    ("02-conversations.md", "长对话与长视频"),
    ("03-expression-dna.md", "表达结构"),
    ("04-external-views.md", "外部评价与批评"),
    ("05-decisions.md", "决策与行动"),
    ("06-timeline.md", "时间线"),
    ("07-courses-lectures.md", "课程与公开教学"),
)
UNCERTAINTY_MARKERS = ("待扩展", "待补", "初版假设", "信息不足", "待核查")
URL_PATTERN = re.compile(r"https?://[^\s<>()\]；，、]+")
HEADING_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def normalize_url(value: str) -> str:
    return value.rstrip(".,;:!?'")


def inspect_dimension(path: Path, label: str) -> dict:
    if not path.is_file():
        return {
            "file": path.name,
            "label": label,
            "exists": False,
            "locator_urls": 0,
            "sections": [],
            "unresolved_markers": [],
            "status": "missing",
        }

    content = path.read_text(encoding="utf-8")
    urls = {normalize_url(match) for match in URL_PATTERN.findall(content)}
    markers = [marker for marker in UNCERTAINTY_MARKERS if marker in content]
    sections = HEADING_PATTERN.findall(content)
    return {
        "file": path.name,
        "label": label,
        "exists": True,
        "locator_urls": len(urls),
        "sections": sections,
        "unresolved_markers": markers,
        "status": "needs-review" if markers else "ready-for-synthesis",
    }


def build_checkpoint(root: Path = ROOT) -> dict:
    research_dir = root / "references" / "research"
    dimensions = [
        inspect_dimension(research_dir / filename, label)
        for filename, label in RESEARCH_DIMENSIONS
    ]
    all_urls: set[str] = set()
    for filename, _label in RESEARCH_DIMENSIONS:
        path = research_dir / filename
        if path.is_file():
            all_urls.update(normalize_url(match) for match in URL_PATTERN.findall(path.read_text(encoding="utf-8")))
    return {
        "schema": "huberman-research-checkpoint-v1",
        "root": str(root.resolve()),
        "dimensions": dimensions,
        "summary": {
            "expected_dimensions": len(RESEARCH_DIMENSIONS),
            "present_dimensions": sum(item["exists"] for item in dimensions),
            "needs_review": sum(item["status"] == "needs-review" for item in dimensions),
            "unique_locator_urls": len(all_urls),
        },
        "note": "URL locators measure traceability, not evidence quality or support.",
    }


def render_markdown(checkpoint: dict) -> str:
    lines = [
        "# Research checkpoint",
        "",
        "| Dimension | File | URL locators | Status | Unresolved markers |",
        "|---|---|---:|---|---|",
    ]
    for item in checkpoint["dimensions"]:
        markers = ", ".join(item["unresolved_markers"]) or "—"
        lines.append(
            f"| {item['label']} | `{item['file']}` | {item['locator_urls']} | {item['status']} | {markers} |"
        )
    summary = checkpoint["summary"]
    lines.extend(
        [
            "",
            f"Present dimensions: {summary['present_dimensions']}/{summary['expected_dimensions']}",
            f"Dimensions needing review: {summary['needs_review']}",
            f"Unique URL locators: {summary['unique_locator_urls']}",
            "",
            f"Note: {checkpoint['note']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    checkpoint = build_checkpoint(args.root)
    if args.json:
        print(json.dumps(checkpoint, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(checkpoint))
    return 0 if checkpoint["summary"]["present_dimensions"] == checkpoint["summary"]["expected_dimensions"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
