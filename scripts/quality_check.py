#!/usr/bin/env python3
"""Lightweight structural QA for the Huberman Health Guide entrypoint."""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED = [
    "## 使命",
    "## 何时使用",
    "## 每次回答先完成的判断",
    "## 五种帮助模式",
    "## 默认回答契约",
    "## 指导原则",
    "## 行动路由",
    "## 医学与安全边界",
    "## 来源与诚实边界",
]


def check(skill_file: Path) -> list[tuple[str, bool, str]]:
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = text.startswith("---\n") and "\nname:" in text and "\ndescription:" in text
    desc = re.search(r"^description:\s*(.+)$", text, re.M)
    results = [("frontmatter", frontmatter, "name and description present")]
    results.append(("description length", bool(desc and len(desc.group(1)) <= 1024), "loader-safe description"))
    for heading in REQUIRED:
        results.append((heading, heading in text, "required section"))
    forbidden = ["TODO", "<person-name>", "[person-name]"]
    results.append(("no scaffold placeholders", not any(token in text for token in forbidden), "finished entrypoint"))
    skill_dir = skill_file.parent
    refs = [
        "references/coaching-guide.md",
        "references/catalog/action-playbooks.jsonl",
        "references/catalog/academic-study-cards.jsonl",
        "references/catalog/evidence-relations.jsonl",
    ]
    results.append(("progressive references exist", all((skill_dir / ref).exists() for ref in refs), "action, coaching and evidence layers available"))
    results.append(("concise entrypoint", len(text.splitlines()) < 180, "progressive-disclosure entrypoint"))
    maintenance_commands = ("collect_episode_pages.py", "build_knowledge_graph.py", "release_check.py")
    results.append(("no maintenance workflow", not any(command in text for command in maintenance_commands), "user journey stays in the entrypoint"))
    return results


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("SKILL.md")
    results = check(path)
    failed = 0
    for name, ok, note in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {note}")
        failed += not ok
    print(f"summary: {len(results) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
