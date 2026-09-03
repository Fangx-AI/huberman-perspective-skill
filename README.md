# Huberman Health Guide

> 睡不好、压力大、没精神、总坚持不住？说一句你的情况，先拿到今天能做的一步。

这不是“Huberman 知识百科”，也不要求你先懂神经科学。它把长视频、播客和相关研究放在后台，前台只帮助你解决真实生活问题。

## 30 秒开始

在终端运行：

```bash
npx skills add Fangx-AI/huberman-perspective-skill -g -a codex -s huberman-perspective -y
```

安装完成后打开一个新的 Codex 任务，直接说你的困扰。不必写提示词，也不必提 Huberman：

```text
我最近每天越睡越晚，白天没精神。别给我完整协议，先告诉我今天做什么。
```

## 回答会是什么样

**你说：**

> 我收藏了很多健康建议，越看越焦虑，但一条也坚持不住。

**它会像这样帮助你：**

> 先暂停收集新建议，今天只决定一个你最想恢复的生活结果。
>
> 最小版本：写下一句“这周我最想改善的是____”，然后只保留一个与它直接相关、十分钟内能开始的动作。
>
> 判断有没有帮助：今晚是否更容易开始，而不是你懂了多少。三次仍做不起来，就继续缩小动作或改变环境，不再叠加新协议。

你得到的不是一份更长的清单，而是：一个优先动作、状态差时的最小版本、一个现实结果、失败后的调整办法，以及必要的停止或求助边界。默认不超过三个动作。

## 你可以直接这样说

- “我最近压力很大，先帮我恢复到能继续工作的状态。”
- “作息没变，但我躺下很久睡不着，今晚先做什么？”
- “我久坐又没体力，想从最容易坚持的一步开始。”
- “下午三点就没精神，只能靠咖啡，先帮我安全恢复下一段工作。”
- “我做了三天又乱了，是不是我自律太差？”
- “红光、冷水澡、桑拿和补剂这么多，哪个根本不值得做？”
- “我试过一个方法但没效果，帮我复盘，只改一个变量。”
- “我想深入看看这个建议到底有什么证据。”

即使你没有提到 Huberman，普通睡眠、精力、压力、专注、习惯、运动和饮食问题也可以自动触发。你也可以显式调用：

```text
$huberman-perspective 我最近每天凌晨两点才睡，先帮我做最小调整。
```

## 它怎样服务你的生活

| 你的处境 | 它优先做什么 |
| --- | --- |
| 躺下睡不着、夜醒或早醒 | 先区分普通睡眠困难、作息后移和紧急信号，给今晚能做的一步；反复困扰时转向 CBT-I 等有效照护 |
| 整套作息越来越晚 | 找到本周最值得稳定的一件事，不把它与失眠混为一谈 |
| 午后没精神、总靠咖啡 | 先区分普通低谷和需要评估的困倦/疲劳，再给一个不叠加兴奋剂的起点 |
| 压力突然冲上来 | 先排除危险，再用一个可停止的动作恢复眼前功能 |
| 长期紧绷、反复担忧或工作耗竭 | 先看安全和受损功能；能改现实负荷就先减负，持续影响生活时把专业求助变成今天能发出的消息 |
| 分心、拖延、学完就忘 | 保护一个能完成的区块，让结果可观察 |
| 习惯总失败 | 缩小动作、减少环境摩擦，不责备自律 |
| 想开始运动或改善饮食 | 从当前能力和生活环境出发，不塞完整协议 |
| 想买补剂或设备 | 先看目标、证据、风险、成本和更简单的替代方案 |
| 已经尝试过但没效果 | 一次只调整一个变量，知道何时停止 |

需要改变建议时，它最多先问一个关键问题；信息已经足够时会直接给安全起点，不让你先填长问卷。

## 适合与不适合

适合：日常生活方式选择、低风险行为尝试、协议取舍、执行困难和复盘调整。

不适合：个人诊断、开药、停药、改药、替代治疗或急症处理。胸痛、严重或新发气促、晕厥、意识或神经异常、自伤/他伤风险等情况，应先联系当地急救或危机支持。症状持续、明显影响功能或快速恶化时，应寻求合格医疗专业人员评估。

这是独立、非官方项目，不代表 Andrew Huberman 或 Huberman Lab。建议不会因为来自名人、播客或一段机制解释就被当成医疗事实。

## 其他安装方式

如果不使用 `npx skills`，可以手动安装：

```bash
git clone https://github.com/Fangx-AI/huberman-perspective-skill.git
cp -R huberman-perspective-skill ~/.codex/skills/huberman-perspective
```

也可以下载 GitHub Release 压缩包，解压到 `~/.codex/skills/huberman-perspective/`，然后重新打开 Codex 或开启新任务。

## 给维护者：证据后台

普通用户不需要运行本节中的任何命令。后台的作用是核查来源、保留冲突、限制过度承诺，并在证据会改变决定时支持深入追问。

当前公开快照包括：425 期官方节目索引、55 张结构化研究证据卡、34 条研究间关系、14 个行动剧本、42 个带停止条件和调整规则的动作，以及 1,736 个来源记录。公开仓库只保留可复现的结构化索引、摘要、定位器和生成脚本，不分发大段第三方转录文本。

按问题查询：

```bash
python scripts/query_action_playbooks.py "总是睡得越来越晚，早上起不来" --json
python scripts/query_action_playbooks.py "作息规律，但躺下一个小时还睡不着" --json
python scripts/query_action_playbooks.py "下午没精神，只能靠咖啡" --json
python scripts/query_evidence.py "sleep timing" --json
```

验证项目：

```bash
python -m unittest discover -s tests -v
python scripts/quality_check.py SKILL.md
python scripts/release_check.py
python scripts/release_readiness.py
```

项目借鉴了 [Nuwa Skill](https://github.com/alchaincyf/nuwa-skill) 的多维研究、提炼与独立评测思路，并针对健康指导增加了用户结果、证据诚实和医学安全门槛。方法只约束后台，不增加用户负担。

进一步文档：

- [使用示例](docs/USAGE_EXAMPLES.md)
- [项目结构](docs/ARCHITECTURE.md)
- [项目状态](docs/PROJECT_STATUS.md)
- [复现说明](docs/REPRODUCIBILITY.md)
- [维护手册](docs/MAINTENANCE.md)
- [发布流程](docs/PUBLISHING.md)
- [版权与数据政策](docs/COPYRIGHT_AND_DATA_POLICY.md)
- [数据字典](docs/DATA_DICTIONARY.md)
- [用户优先前向测试](references/evals/user-forward-tests-2026-08-31.md)
- [最新独立质量报告](FIDELITY.md)
- [质量评分标准](references/fidelity-scorecard.md)

贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。

## 数据、版权与许可

代码和本项目原创结构化内容按 [MIT License](LICENSE) 发布。第三方节目、视频、论文、网页和转录文本仍归各自权利人所有；仓库中的链接、事实性元数据和短摘要不代表版权或商标归属。

当前版本：`0.20.0`
