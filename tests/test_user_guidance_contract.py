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
            "最近的安全地点停车",
            "不要让用户第二天自行猜",
            "今天不额外加码，也不突然取消原有摄入",
            "“睡不着”不等于“作息后移”",
            "只有在离床安全时",
            "不要让用户自行执行睡眠限制",
            "询问 CBT-I/简短行为治疗",
            "当天联系医生或精神健康专业人员",
            "就按反复发生处理",
            "转向当地紧急医疗评估",
            "持续几周或几个月的紧绷",
            "不能说明个人皮质醇高低",
            "不想醒来",
            "不得据此直接断言“不需要急救”",
            "不把体重当品格",
            "不继续输出后面的减重生活实验",
            "不先给热量、断食",
            "不套固定“几点后不能吃”的钟点规则",
            "不替用户决定开始、停用、调量或从非正规渠道购买",
            "摄入约 15 克快速吸收糖，15 分钟后复测",
            "立即呼叫当地急救且不要强行喂食",
            "不得让用户自行改胰岛素或靠断食减重",
            "用户想少喝但不想完全戒时",
            "酒精不能作为助眠方案",
            "可叠加抑制呼吸，可能导致昏迷或死亡",
            "不能只说“不要混用”",
            "不能因为用户没有先报药名就省略这一条",
            "同一回答还必须把戒断分成两级",
            "不要求独自在家突然停酒",
            "不要让其开车或独处",
            "咖啡、冷水澡、走路或催吐",
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
        self.assertIn("普通睡眠、精力、压力、专注、习惯、运动、饮食、体重/食欲和少喝酒问题也可以自动触发", readme)

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
