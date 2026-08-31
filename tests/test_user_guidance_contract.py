from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class UserGuidanceContractTests(unittest.TestCase):
    def test_entrypoint_is_a_concise_user_journey(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "帮助用户过得更好",
            "无需先说“Huberman”",
            "一次只问一个问题",
            "默认不超过三个动作",
            "最小版本",
            "没用怎么办",
            "何时停止或求助",
        ):
            self.assertIn(phrase, skill)
        self.assertLess(len(skill.splitlines()), 180)

    def test_research_pipeline_is_not_the_user_entrypoint(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for maintenance_command in (
            "collect_episode_pages.py",
            "build_knowledge_graph.py",
            "release_check.py",
        ):
            self.assertNotIn(maintenance_command, skill)
        self.assertNotIn("仅在用户明确要求", skill)
        self.assertNotIn("不触发：普通睡眠", skill)

    def test_readme_leads_with_user_value_before_research_counts(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertLess(readme.index("## 你可以直接这样说"), readme.index("## 为什么保留一套大型证据后台"))
        self.assertNotIn("## 当前快照", readme[:1500])
        self.assertIn("普通健康生活问题可以自动触发", readme)

    def test_ui_policy_allows_automatic_lifestyle_invocation(self) -> None:
        policy = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(policy, r"allow_implicit_invocation:\s*true")
        self.assertIn("今天能做的最小行动", policy)

    def test_coaching_guide_supports_adjustment_not_knowledge_dumping(self) -> None:
        guide = (ROOT / "references" / "coaching-guide.md").read_text(encoding="utf-8")
        for phrase in ("现实结果", "一次只调整一个变量", "不像论文审稿人", "没做成", "症状加重或出现风险"):
            self.assertIn(phrase, guide)


if __name__ == "__main__":
    unittest.main()
