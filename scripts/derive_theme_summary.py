#!/usr/bin/env python3
"""Derive topic coverage and candidate co-occurrences from public Episode notes."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


THEMES = {
    "sleep-circadian": r"sleep|circadian|jet lag|insomnia|melatonin|睡眠|昼夜节律",
    "focus-attention": r"focus|attention|concentration|ADHD|专注|注意力",
    "learning-memory": r"learn|learning|memory|neuroplastic|study|学习|记忆|神经可塑",
    "motivation-goals": r"motivation|dopamine|drive|goal|procrastinat|willpower|动机|目标|多巴胺|拖延",
    "stress-emotions": r"stress|anxiety|emotion|trauma|resilien|压力|焦虑|情绪|创伤",
    "exercise-recovery": r"exercise|fitness|strength|muscle|endurance|recovery|训练|运动|肌肉|恢复",
    "nutrition-metabolism": r"nutrition|diet|food|metabolism|blood sugar|gut|营养|饮食|代谢|肠道",
    "hormones-sexual-health": r"hormone|testosterone|estrogen|fertility|sexual|激素|睾酮|雌激素|生育",
    "breath-meditation-nsdr": r"breath|breathing|meditation|NSDR|mindfulness|呼吸|冥想",
    "supplements-drugs": r"supplement|caffeine|nicotine|peptide|drug|药物|补剂|咖啡因|尼古丁|肽",
    "vision-neuroscience": r"vision|visual|brain|neural|nervous system|眼|视觉|大脑|神经系统",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    theme_counts: Counter[str] = Counter()
    pairs: Counter[str] = Counter()
    episode_rows = []
    for item in records:
        text = " ".join([item.get("title", ""), item.get("show_notes", ""), item.get("timestamps", "")])
        matched = sorted(name for name, pattern in THEMES.items() if re.search(pattern, text, re.I))
        for name in matched:
            theme_counts[name] += 1
        for i, left in enumerate(matched):
            for right in matched[i + 1:]:
                pairs[f"{left}__{right}"] += 1
        episode_rows.append({"episode_id": item.get("episode_id", ""), "title": item.get("title", ""), "themes": matched})
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "theme_counts": [{"theme": k, "episode_count": v} for k, v in theme_counts.most_common()],
        "theme_cooccurrences": [{"pair": k, "episode_count": v} for k, v in pairs.most_common(50)],
        "episode_theme_assignments": episode_rows,
        "method_note": "Keyword candidate extraction from official titles, public Show Notes and timestamps; candidates require source-level review before entering SKILL.md.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "themes": len(theme_counts), "pairs": len(pairs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
