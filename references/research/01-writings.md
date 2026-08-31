# 01 · 著作与系统思考

## 当前结论

Huberman 的公开系统性文字主要不是传统学术专著，而是 Huberman Lab Episode Show Notes、Protocol/Toolkit PDF、Newsletter、FAQ 以及 Stanford/实验室论文页面。研究阶段应把“播客协议文档”和“学术论文”分开，不把前者自动当作后者的等价物。

Stanford 实验室公开出版物分页目录已采集 59 条（见 `references/catalog/publications.csv`）。目前可见研究重心集中在视觉系统、视网膜/视觉回路、神经发育与修复、神经可塑性、压力/威胁与人类视觉诱发威胁；这些论文可支持其学术背景与部分机制解释，但不能自动验证播客中所有营养、补剂、激素或生活方式协议。

Episode Show Notes 当前展平为 7,262 条资源记录，其中 1,913 条被统一分类器识别为学术/医学链接；这些记录属于 6,024 个去重资源节点的一部分。原始 `episode-resources.csv` 只保留在本地研究缓存，公开仓库发布去重核查队列与脱敏图谱；下一阶段继续按主题与主张建立“播客主张—原始论文—外部复核”三联关系。

其中 1,736 个去重后的 Show Notes 学术/医学 URL 已进入 `references/catalog/academic-verification-queue.csv`，当前 673 条已核验、1,063 条待核验；已核验队列行由 115 条原始研究、34 条综述、21 条观察研究和 503 条仅书目确认组成。队列扩展来自补全 Annual Reviews、Wiley、Springer、OUP、PNAS、JAMA、BMJ、Lancet 等主流学术平台，旧分母低估了真实待核验量；它不代表已核验证据质量下降。队列按被多个 Episode 引用的次数排序；“被引用次数”只表示内容关联度，不表示研究质量或结论强度。研究级记录会把样本、设计、主要结局、阴性结果、争议与外推边界写入备注、证据台账和 `academic-study-cards.jsonl`；`verified-bibliographic` 只确认出处存在，不能直接支撑疗效或协议。当前 16 张研究卡中有 11 张连接 13 条 Show Notes 来源记录，另有 5 张不属于该队列的外部反证/限定卡，以 `external-context` 单独标记，不改变上述队列统计。

首批核查示例已经显示证据层差异：85% 规则来自计算/模型研究；主动提取现由两项实验与一篇叙述性综述组成关系簇，既支持延迟保持，也保留即时测验可能不占优、无反馈低正确率、集中重复测验、迁移和固定间隔外推等边界；习惯形成关系簇显示 21 天是待检验的节目实践框架而非形成定律，66 天只是特定筛选样本的中位模型估计，系统综述则显示 4–335 天的高度异质范围且前后效应不能当作受控因果效果；有氧训练—海马研究来自特定老年成人 RCT；短睡眠、急性运动、处方“聪明药”、认知训练长期随访和饮食—睡眠关系各自来自不同的人体研究设计；循环叹息来自短期人体随机研究；视觉威胁与视网膜修复来自动物研究。Skill 输出时必须保留这些证据类型，不能把 Huberman 对论文的科普翻译成统一强度的“人体有效”。

## 已确认入口

- 官方 Episode 目录：https://www.hubermanlab.com/all-episodes
- 官方主题目录：https://www.hubermanlab.com/topics
- 实验室论文：https://hubermanlab.stanford.edu/publications
- 目标设定 Episode：https://www.hubermanlab.com/episode/the-science-of-setting-and-achieving-goals
- 日常工具 Episode：https://www.hubermanlab.com/episode/maximizing-productivity-physical-and-mental-health-with-daily-tools

## 待扩展

按主题抽取重复出现的定义、机制—工具链、协议条件、证据等级和反例：睡眠/昼夜节律、专注/学习、动机/目标、压力/情绪、运动/恢复、营养/补剂、神经可塑性、呼吸/NSDR、激素/性健康、嘉宾观点。
