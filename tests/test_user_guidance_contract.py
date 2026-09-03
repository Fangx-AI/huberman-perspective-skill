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
            "行动类快速回答也要用一两句压缩地保留闭环",
            "目标不清楚时默认暂不购买",
            "明确停止相关活动并尽快接受专业评估",
            "不要替用户决定下一剂该继续、暂停还是改变",
            "区分失败发生在忘记、没开始、中途被打断、动作太难",
            "在用户回答前不要让他列出或整理全部问题",
            "持续或原因不明的疲劳",
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
        self.assertLess(readme.index("## 30 秒开始"), readme.index("## 给维护者：证据后台"))
        self.assertLess(readme.index("## 回答会是什么样"), readme.index("## 给维护者：证据后台"))
        self.assertIn("npx skills add Fangx-AI/huberman-perspective-skill", readme[:1800])
        self.assertIn("最小版本", readme[:1800])
        self.assertNotIn("当前公开快照包括", readme[:1800])
        self.assertIn("普通睡眠、精力、压力、专注、习惯、运动和饮食问题也可以自动触发", readme)

    def test_readme_does_not_send_users_to_missing_scripts(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for stale_command in (
            "query_study_cards.py",
            "query_evidence_relations.py",
            "query_knowledge_graph.py",
            "quick_validate.py",
        ):
            self.assertNotIn(stale_command, readme)
        for live_command in ("query_action_playbooks.py", "query_evidence.py", "quality_check.py"):
            self.assertIn(live_command, readme)
            self.assertTrue((ROOT / "scripts" / live_command).is_file())

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
