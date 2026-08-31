# 长期更新协议

## 每周/每次更新

1. 运行官方目录更新脚本，按 Episode URL 去重；用 `episode-resources.csv` 作为 `build_academic_queue.py --input`，重建学术核验队列时脚本会按 URL 增量保留既有 `verification_status` 与 `evidence_notes`，YouTube 队列则按 Episode ID/视频 ID保留 `downloaded/analyzed`、字幕来源和时间戳状态，不得因刷新目录而将已核验记录重置为 `pending`。
2. 只处理新增或发生内容变化的 Episode；保存元数据，不默认保存完整受版权保护的转录。
3. 定期运行 Stanford 出版物目录脚本；新论文先进入文献目录和 `01-writings.md`，再与对应播客主张建立关系。
4. 运行 Show Notes 资源展平脚本，优先筛出论文/医学数据库链接，建立待核查队列。
5. 运行学术核查队列脚本；核查时记录研究类型、人群、样本量、主要结局、局限、利益冲突和是否支持播客的具体表述。
   可先用 `verify_academic_batch.py --limit N` 对 PMC/PMID/DOI/Elsevier PII 做断点式公开书目核对；结果追加到 `academic-metadata.jsonl`，该工具最多只写入 `verified-bibliographic`，不把书目命中自动升级为研究或疗效证据。人工核对一手全文/权威索引后，把设计、样本、主要与阴性结局、局限、安全解释和 provenance 写入 `academic-study-cards.jsonl`，再用 `apply_academic_study_cards.py` 确定性回写队列；不得直接手改状态而遗漏证据卡。若复制、反证或限定研究不在 Episode Show Notes 队列中，证据卡必须标为 `source_scope=external-context` 且 `queue_urls=[]`，并在 `evidence-relations.jsonl` 中登记它具体支持或挑战的主张范围；外部来源不得改变 Show Notes 队列计数。
6. 对新增长视频记录 YouTube ID；如果发现 B 站版本，记录 BV 号、UP 主、字幕/翻译质量和对应原视频。
   官网偶尔会把 YouTube 平台链接渲染成 `https://<11位视频ID>`；采集器应将其规范化为 `https://www.youtube.com/watch?v=...`，并在修复 ID 后重新探测字幕，不能把截断 ID 永久记为视频不可用。
7. 将新内容先写入 `references/research/02-conversations.md`，再把可跨主题复现的模式升级到 `SKILL.md`。
   重建 `knowledge-graph.json` 时同时传入学术核验队列、研究卡和研究间关系；资源节点应保留 `verification_status`、`evidence_notes`、来源范围和关联 Episode 数，不能让图谱把待核验或外部复核资源伪装成 Episode 已引用来源。
8. 新观点只有在至少两个独立场景中出现，并且不是嘉宾单独观点时，才考虑更新心智模型。

## 每月/每 10-20 集

- 复核睡眠、运动、营养、补剂、激素、心理健康、冷/热暴露和学习类主张的证据等级。
- 查找原始论文、系统综述、指南和反驳研究；把“播客主张”和“外部证据”分列。
- 更新 `evidence-ledger.md`、`04-external-views.md`、`06-timeline.md`。
- 检查商业赞助、产品推荐、嘉宾身份、免责声明和平台政策变化。

## 版本升级门槛

- 强化已有模型：新增至少两个独立 A 类场景。
- 新增模型：跨两个主题复现，且能解释一个未直接讨论的问题；否则降级为“启发式”。
- 立场改变：必须有时间顺序、直接表述或连续内容证据；B 站剪辑或单篇评论不能证明改变。
- 争议：保留双方主张、原始证据和不确定性；不以粉丝共识或批评者单篇文章裁决。
