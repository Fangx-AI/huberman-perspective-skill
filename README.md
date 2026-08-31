# Huberman Perspective Skill

一个非官方、可追溯、中文优先的 Codex Skill，用于在用户**明确要求**时，以 Andrew Huberman / Huberman Lab 公开材料中可验证的分析框架审视神经科学、睡眠、专注、学习、行为改变、运动、营养和健康决策。

本项目不是 Andrew Huberman、Huberman Lab、Scicomm Media 或 Stanford 的官方产品，也不代表任何上述主体。它不提供医疗诊断、处方或个体化治疗建议。

## 当前快照

- 425 个官方 Episode 元数据记录
- 424 个 canonical YouTube 视频，其中 423 个已完成批次级分析
- 34 个 B 站发现线索，其中 19 个已回链官方 Episode/YouTube
- 1,736 个 Show Notes 学术/医学来源，673 个已核验、1,063 个待核验；其中 115 条原始研究、34 条综述、21 条观察研究和 503 条仅书目确认。分母扩展来自对主流学术出版平台的分类补全，不代表证据质量下降
- 16 张结构化高关联研究证据卡：11 张连接 13 条 Show Notes 来源记录，5 张为不改变队列统计的外部反证/限定卡
- 10 条机器可读的 `challenges / qualifies / supports` 关系，覆盖睡眠—运动学习、自然明暗周期、主动提取/测试效应与习惯形成时长证据簇
- 研究证据图谱包含 16 个研究卡、79 个结果/阴性发现、107 个局限、69 个证据主题及 10 个研究关系节点，共 8,679 条可追溯关系
- 40 个脱敏的主张定位记录
- 8 个课程、讲座、AMA 或机构访谈入口

数字是研究快照，不代表已穷尽所有材料，也不代表每条来源具有同等证据强度。

## 安装

要求：Codex、Python 3.11+；只有重新采集 Stanford publications 时需要 `lxml`。

最简单的方式是从 GitHub 页面的 **Code** 按钮复制仓库 URL，并直接克隆到 Codex Skills 目录：

```bash
read -r -p "Repository URL from GitHub Code button: " REPOSITORY_URL
git clone "$REPOSITORY_URL" ~/.codex/skills/huberman-perspective
cd ~/.codex/skills/huberman-perspective
python -m pip install -r requirements.lock
python scripts/release_check.py
```

PowerShell：

```powershell
$RepositoryUrl = Read-Host "Repository URL from GitHub Code button"
$SkillPath = Join-Path $env:USERPROFILE ".codex\skills\huberman-perspective"
git clone $RepositoryUrl $SkillPath
Set-Location -LiteralPath $SkillPath
python -m pip install -r requirements.lock
python scripts/release_check.py
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

也可直接检索已人工核查的结构化研究卡；命令会连同阴性结果、局限、安全解释、一手来源及已登记的复制/反证关系一起输出：

```bash
python scripts/query_evidence.py "咖啡因 多巴胺"
python scripts/query_evidence.py "睡眠 运动学习 巩固"
python scripts/query_evidence.py "睡眠 稳定 运动学习"
python scripts/query_evidence.py "自然光 昼夜节律 周末露营"
python scripts/query_evidence.py "主动提取 测试效应 长期保持 反馈"
python scripts/query_evidence.py "习惯形成 21天 66天 自动化 情境线索"
python scripts/query_evidence.py "gratitude inflammation" --json
```

关键词命中只用于定位研究卡，不代表研究支持查询中的完整主张。

## 验证

```bash
python scripts/release_check.py
python scripts/validate_evidence_relations.py --cards references/catalog/academic-study-cards.jsonl --relations references/catalog/evidence-relations.jsonl
python scripts/quality_check.py SKILL.md
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```

`scripts/contract_check.py` 会自动选择验证模式：发布快照运行 release checks；如果本地存在不随仓库分发的原始页面缓存，则运行完整契约检查。

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

当前版本：`0.7.0`，研究预览版。公开发布前仍建议由熟悉版权、商标和平台条款的专业人士复核，尤其是仓库命名、人物名称的描述性使用，以及任何商业化场景。
