#!/usr/bin/env python3
"""Lightweight structural QA for the Huberman perspective Skill."""
from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED = [
    "## 定位",
    "## 角色规则",
    "## 核心分析框架",
    "## 回答工作流",
    "## 长视频与语料规则",
    "## 医学与安全边界",
    "## 诚实边界",
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
        "references/source-registry.md",
        "references/evidence-ledger.md",
        "references/update-protocol.md",
        "references/research/01-writings.md",
        "references/research/02-conversations.md",
        "references/research/03-expression-dna.md",
        "references/research/04-external-views.md",
        "references/research/05-decisions.md",
        "references/research/06-timeline.md",
        "references/research/07-courses-lectures.md",
        "references/catalog/courses-lectures.csv",
    ]
    results.append(("research references exist", all((skill_dir / ref).exists() for ref in refs), "self-contained references"))
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
