# Huberman Health Guide

> 把 Huberman 的长视频和相关研究，变成你今天能做、之后能复盘的健康行动。

你不需要先看完几百期播客、理解神经科学，或从几十套协议里挑一个。这个 Skill 面向真实生活：当你睡不好、压力大、没精神、容易分心、久坐、饮食失控，或收藏了很多健康建议却执行不下去时，它会帮你找到一个现实的下一步。

## 你可以直接这样说

- “我最近越睡越晚，早上完全起不来，先帮我做最小调整。”
- “我现在压力很大，先帮我恢复到能继续工作的状态。”
- “我收藏了很多健康协议，但一个也坚持不住。”
- “我久坐又没体力，不想一上来就执行复杂训练计划。”
- “红光、冷水澡、桑拿和补剂太多了，帮我判断哪个根本不值得做。”

即使你没有提到 Huberman，Skill 也可以在这些生活问题上自动提供帮助。一次回答通常会告诉你：

1. 今天先做什么；
2. 状态差时的最小版本；
3. 用哪个现实结果判断有没有帮助；
4. 没做到或没效果时怎样调整；
5. 哪些情况应该停止尝试或寻求专业帮助。

默认不超过三个动作，不用论文、术语和完整协议淹没用户。

## 它怎样帮助你

1. 先理解你真正想改善的生活结果，以及时间、精力、预算、症状和环境限制。
2. 从“立即稳定、改善一个环节、判断协议、复盘调整、深入证据”中选择一种帮助模式。
3. 给出一个低摩擦、可逆、能观察结果的行动；需要时只问一个会真正改变建议的问题。
4. 根据你的实际结果继续缩小、替换或停止方案，而不是把执行失败解释成自律不足。
5. 只在证据会改变选择或安全边界时，把 Huberman 原始内容、独立研究和指南带到前台。

## 支持的生活场景

| 场景 | Skill 优先解决的问题 |
| --- | --- |
| 睡眠与作息 | 今晚或本周先稳定哪个线索，怎样看现实效果 |
| 精力与恢复 | 区分睡眠不足、安排过载、运动恢复和需要就医的信号 |
| 压力与情绪稳定 | 在非紧急情况下先恢复一个现实功能 |
| 专注与拖延 | 保护一个能完成的专注区块，减少环境摩擦 |
| 学习与记忆 | 把“看懂了”转成之后还能提取和使用 |
| 习惯 | 把目标缩到能开始，失败后调整线索和摩擦 |
| 运动 | 从当前能力出发开始，不一次塞入完整训练协议 |
| 饮食环境 | 先改变容易失控的情境，不先制造羞耻和禁令 |
| 协议、补剂与设备 | 判断是否值得、风险多大、是否有更便宜安全的替代 |

## 自动触发与显式调用

安装后，普通健康生活问题可以自动触发，无需写 Skill 名称。你也可以显式调用：

```text
$huberman-perspective 我最近每天凌晨两点才睡，别给完整协议，先帮我从今天开始。
```

概念解释会保持简洁；个人诊断、药物调整、治疗替代和急症处理不会被包装成“生活实验”。

## 安装

从 GitHub 安装：

```bash
git clone https://github.com/Fangx-AI/huberman-perspective-skill.git
cp -R huberman-perspective-skill ~/.codex/skills/huberman-perspective
```

也可以下载 Release 压缩包并解压到：

```text
~/.codex/skills/huberman-perspective/
```

安装后重新打开 Codex，或开启一个新任务。

## 为什么保留一套大型证据后台

用户体验应当简单，但建议不能只靠一个人的记忆或一段机制故事。后台证据层用于发现可用杠杆、标记不确定性、处理冲突、限制过度承诺，并支持需要来源的深入追问。

当前公开快照包括：

- 425 期官方节目索引，其中 424 期映射到官方 YouTube；
- 47 张结构化研究证据卡和 30 条研究间关系；
- 11 个行动剧本、33 个带停止条件和调整规则的动作；
- 41 个论文定位器、9,529 条引用图边；
- 1,736 个来源记录，其中 684 个已验证来源。

公开仓库只保留可复现的结构化索引、摘要、定位器和生成脚本，不分发大段第三方转录文本。

### 按问题查询后台

```bash
python scripts/query_action_playbooks.py "总是睡得越来越晚，早上起不来" --json
python scripts/query_study_cards.py "sleep timing" --json
python scripts/query_evidence_relations.py "light circadian" --json
python scripts/query_knowledge_graph.py "stress breathing" --verified-only --limit 8
```

这些命令用于维护、审计和深入研究；普通用户不需要先运行它们才能获得帮助。

## 安全边界

- 这是教育与生活方式支持，不是医疗诊断或治疗。
- 不建议自行停药、改药，也不把补剂替代专业照护。
- 胸痛、严重或新发气促、晕厥、意识或神经异常、自伤/他伤风险等情况，应先联系当地急救或危机支持。
- 呼吸、冷水、高热、禁食等做法必须遵守情境禁忌与停止条件。
- 对新产品、现行指南和可能变化的健康信息，应重新核查当前来源。

## 验证与贡献

```bash
python -m unittest discover -s tests -v
python scripts/quick_validate.py
python scripts/release_check.py
python scripts/release_readiness.py
```

进一步文档：

- [项目状态](docs/PROJECT_STATUS.md)
- [复现说明](docs/REPRODUCIBILITY.md)
- [维护手册](docs/MAINTENANCE.md)
- [发布流程](docs/PUBLISHING.md)
- [版权与数据政策](docs/COPYRIGHT_AND_DATA_POLICY.md)
- [数据字典](docs/DATA_DICTIONARY.md)
- [使用示例](docs/USAGE_EXAMPLES.md)
- [用户优先前向测试](references/evals/user-forward-tests-2026-08-31.md)

贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。

## 数据、版权与许可

代码和本项目原创结构化内容按 [MIT License](LICENSE) 发布。第三方节目、视频、论文、网页和转录文本仍归各自权利人所有；仓库中的链接、事实性元数据和短摘要不代表版权或商标归属，也不代表 Andrew Huberman 或 Huberman Lab 的认可。

当前版本：`0.16.0`
