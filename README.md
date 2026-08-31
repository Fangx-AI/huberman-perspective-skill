# Huberman Perspective Skill

一个非官方、可追溯、中文优先的 Codex Skill，用于在用户**明确要求**时，以 Andrew Huberman / Huberman Lab 公开材料中可验证的分析框架审视神经科学、睡眠、专注、学习、行为改变、运动、营养和健康决策。

本项目不是 Andrew Huberman、Huberman Lab、Scicomm Media 或 Stanford 的官方产品，也不代表任何上述主体。它不提供医疗诊断、处方或个体化治疗建议。

## 当前快照

- 425 个官方 Episode 元数据记录
- 424 个 canonical YouTube 视频，其中 423 个已完成批次级分析
- 34 个 B 站发现线索，其中 19 个已回链官方 Episode/YouTube
- 1,736 个 Show Notes 学术/医学来源，684 个已核验、1,052 个待核验；其中 122 条原始研究、37 条综述、23 条观察研究和 502 条仅书目确认。分母扩展来自对主流学术出版平台的分类补全，不代表证据质量下降
- 47 张结构化高关联研究证据卡：27 张连接 41 条 Show Notes 来源记录，20 张为不改变队列统计的外部反证/限定卡
- 30 条机器可读的 `challenges / qualifies / supports` 关系，覆盖睡眠—运动学习、自然明暗周期、主动提取/测试效应、习惯形成、冷暴露、红光设备、桑拿/热暴露与呼吸减压决策证据簇
- 11 个结果优先行动剧本、33 个动作，覆盖习惯执行、学习保持、睡眠节律、专注、运动起步、饮食环境、健康协议、冷暴露、红光设备、桑拿/热暴露与非紧急压力呼吸决策；每步区分证据支持、有限个人实验与框架推断
- 研究—行动图谱包含 47 个研究卡、223 个结果/阴性发现、290 个局限、218 个证据主题、30 个研究关系节点、11 个行动剧本和 33 个动作节点，共 9,529 条可追溯关系
- 41 个脱敏的主张定位记录
- 8 个课程、讲座、AMA 或机构访谈入口

数字是研究快照，不代表已穷尽所有材料，也不代表每条来源具有同等证据强度。

## 安装

要求：Codex、Python 3.11+；只有重新采集 Stanford publications 时需要 `lxml`。

最简单的方式是直接从公开仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/Fangx-AI/huberman-perspective-skill.git ~/.codex/skills/huberman-perspective
cd ~/.codex/skills/huberman-perspective
python -m pip install -r requirements.lock
python scripts/release_check.py
python scripts/release_readiness.py
```

PowerShell：

```powershell
$SkillPath = Join-Path $env:USERPROFILE ".codex\skills\huberman-perspective"
git clone https://github.com/Fangx-AI/huberman-perspective-skill.git $SkillPath
Set-Location -LiteralPath $SkillPath
python -m pip install -r requirements.lock
python scripts/release_check.py
python scripts/release_readiness.py
```

也可以从任意本地克隆目录安全安装；安装器在目标已存在时会拒绝覆盖：

```bash
python scripts/install_skill.py --dry-run
python scripts/install_skill.py
```

安装器默认目标为 `~/.codex/skills/huberman-perspective`；Windows 上对应 `%USERPROFILE%\.codex\skills\huberman-perspective`。

## 使用

该 Skill 是 explicit-only，不会自动接管普通健康问题：

```text
Use $huberman-perspective to analyze whether morning sunlight is a robust sleep intervention.
```

推荐请求包含：问题、人群、目标、已知疾病/用药边界，以及是否需要最新资料核验。

输出应区分：Huberman 的公开主张、跨 Episode 归纳、框架推断、外部研究，以及证据争议。

如果用户不是在追问更多知识，而是想今天开始行动，先检索一个最匹配的行动剧本：

```bash
python scripts/query_action_playbooks.py "收藏很多协议 执行不下去 习惯"
python scripts/query_action_playbooks.py "看完就忘 主动回忆 复习"
python scripts/query_action_playbooks.py "作息漂移 晨光 睡眠"
python scripts/query_action_playbooks.py "总被手机和网页打断 专注"
python scripts/query_action_playbooks.py "久坐很久 运动协议太多 不知怎么开始"
python scripts/query_action_playbooks.py "总点外卖 吃零食 不想算卡路里"
python scripts/query_action_playbooks.py "补剂和健康协议太多 怎么判断一个值不值得试"
python scripts/query_action_playbooks.py "冷水澡提高多巴胺和免疫 要不要每天冰浴"
python scripts/query_action_playbooks.py "红光改善血糖视力皮肤 值不值得买面板或面罩"
python scripts/query_action_playbooks.py "桑拿提高生长激素帮助长寿 值不值得买或每周硬凑"
```

每次只返回一个剧本、最多三个动作；每步带触发条件、最低版本、记录指标、复盘与失败后的调整。`evidence-supported`、`bounded-experiment` 和 `framework-inference` 必须分开，不把节目协议包装成已验证处方。

也可直接检索已人工核查的结构化研究卡；命令会连同阴性结果、局限、安全解释、一手来源及已登记的复制/反证关系一起输出：

```bash
python scripts/query_evidence.py "咖啡因 多巴胺"
python scripts/query_evidence.py "睡眠 运动学习 巩固"
python scripts/query_evidence.py "睡眠 稳定 运动学习"
python scripts/query_evidence.py "自然光 昼夜节律 周末露营"
python scripts/query_evidence.py "主动提取 测试效应 长期保持 反馈"
python scripts/query_evidence.py "习惯形成 21天 66天 自动化 情境线索"
python scripts/query_evidence.py "冷暴露 冰浴 冷水澡 训练恢复 安全"
python scripts/query_evidence.py "红光 面板 面罩 血糖 视力 皮肤 设备等效"
python scripts/query_evidence.py "桑拿 热暴露 长寿 生长激素 血压 恢复 安全"
python scripts/query_evidence.py "gratitude inflammation" --json
```

关键词命中只用于定位研究卡，不代表研究支持查询中的完整主张。

## 验证

```bash
python scripts/release_check.py
python scripts/release_readiness.py
python scripts/validate_evidence_relations.py --cards references/catalog/academic-study-cards.jsonl --relations references/catalog/evidence-relations.jsonl
python scripts/validate_action_playbooks.py --playbooks references/catalog/action-playbooks.jsonl --study-cards references/catalog/academic-study-cards.jsonl --claims references/catalog/claim-index.jsonl
python scripts/quality_check.py SKILL.md
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

`scripts/contract_check.py` 会自动选择验证模式：发布快照运行 release checks；如果本地存在不随仓库分发的原始页面缓存，则运行完整契约检查。

## 项目导航

- [使用示例](docs/USAGE_EXAMPLES.md)：从真实问题出发，说明应当怎样回答、哪些边界不能丢。
- [项目状态](docs/PROJECT_STATUS.md)：把长期目标映射到仓库证据，并公开尚未完成的研究缺口。
- [可复现构建](docs/REPRODUCIBILITY.md)：验证、重建公开快照和维护者工作流。
- [维护路线图](docs/MAINTENANCE.md)：发布门槛、更新节奏和 1.0 退出条件。
- [发布流程](docs/PUBLISHING.md)：GitHub 预检、打标和发布步骤。
- [版权与数据政策](docs/COPYRIGHT_AND_DATA_POLICY.md)与[数据字典](docs/DATA_DICTIONARY.md)：可公开内容、禁止载荷和字段语义。

## 数据与版权边界

仓库不包含：完整字幕、完整转录、音视频、图片、付费 AMA 内容、论文全文或抓取的完整 Show Notes。公开目录只保存必要的来源标识、URL、时间戳、事实型元数据和独立证据评价。

原始页面缓存只能由研究者在本地、遵守来源网站条款的前提下重建，并已被 `.gitignore` 与发布检查排除。详见 [版权与数据政策](docs/COPYRIGHT_AND_DATA_POLICY.md) 和 [数据字典](docs/DATA_DICTIONARY.md)。

## 许可证

- `scripts/`、`tests/` 和 CI 配置：MIT License。
- 原创研究笔记与人工证据注释：CC BY-NC 4.0，详见 `DATA-LICENSE.md`。
- 第三方名称、标题、URL、DOI、PMID、平台 ID 和其他来源元数据不因进入本仓库而被重新许可。

## 贡献

提交来源或修改证据等级前，请阅读 `CONTRIBUTING.md`。每个健康主张都必须给出来源定位、研究设计、适用人群、主要结局、外推边界和医学安全说明。

## 发布状态

当前版本：`0.15.0`，已在 GitHub 公开发布的研究预览版。公开发布不等于法律许可；仍建议由熟悉版权、商标和平台条款的专业人士复核，尤其是人物名称的描述性使用和任何商业化场景。
