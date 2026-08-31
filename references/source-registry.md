# Huberman 语料来源登记（首版）

更新时间：2026-08-31。来源分层：A=本人/官方或原始论文；B=权威外部来源；C=转载、剪辑、二手评论，仅用于发现线索或批评，不作为独立证据。B站登记表额外保存 BV 号、YouTube ID、官方 Episode 回链、UP 主、时长和字幕类型；当前 34 条记录中 19 条已完成原视频回链，其余保留待确认、合集、账号注销或衍生实践状态。

## A 类入口

| 来源 | 用途 | 备注 |
|---|---|---|
| https://www.hubermanlab.com/all-episodes | 全量 Episode 目录、类型、日期、主题 | 当前页面显示 200+ Episodes；持续更新 |
| https://www.hubermanlab.com/topics | 主题目录与相关 Episode | 适合按睡眠、学习、专注、运动、营养等聚类 |
| https://www.hubermanlab.com/podcast | 播客总入口与平台链接 | 指向 YouTube、Apple Podcasts、Spotify、X |
| https://www.hubermanlab.com/about | 人物自述、研究/教学背景 | 作为本人/官方叙述，不当作外部验证 |
| https://www.hubermanlab.com/faq/how-can-i-access-episode-transcripts | 转录访问规则 | 公开说明：完整 Episode transcripts 为 Premium 功能；不得绕过访问控制 |
| https://www.youtube.com/@hubermanlab | 原始长视频、描述、章节、字幕 | YouTube 主语料库 |
| https://hubermanlab.stanford.edu/publications | 实验室论文与 DOI 清单 | 研究强项与论文索引 |
| https://med.stanford.edu/profiles/andrew-huberman | Stanford 官方学术档案 | 职务、研究兴趣、学术背景 |
| https://hubermanlab.stanford.edu/courses | Stanford 课程目录 | 课程号、任期和授课关系；课程元数据不等于完整讲义 |
| https://ed.stanford.edu/events/science-stress-calm-and-sleep | Stanford 公开讲座 | 记录压力、平静与睡眠主题的机构活动页；录像可访问性需单独核验 |
| https://med.stanford.edu/news/insights/2022/10/ask-me-anything-neuroscience-with-andrew-huberman.html | Stanford Medicine AMA | 公开编辑问答与直接表述；不等于个体化医学建议 |
| https://www.gsb.stanford.edu/insights/hacking-your-speaking-anxiety-how-lessons-neuroscience-can-help-you-communicate | Stanford GSB 访谈 | 公开访谈/文字稿；用于表达与压力框架核对 |

## B/C 类入口

| 来源 | 等级 | 用途 |
|---|---|---|
| https://www.bilibili.com/video/BV1YJ4m187LQ/ | C | 中文合集/外挂字幕发现入口；页面自称“搬运”，字幕多为机翻，不能和原 YouTube 重复计数 |
| https://www.bilibili.com/video/BV1tuun6FEUz/ | A-Platform | 页面账号为 Andrew_Huberman，发布“我来B站了”欢迎视频；待确认后续账号视频是否均为官方同步 |
| https://www.bilibili.com/video/BV1SfPCziEeM/ | C | ADHD/专注力长视频中文字幕样本；页面显示约 2 小时 16 分，需回链官方 Episode |
| https://www.bilibili.com/video/BV1eePpeXEMc/ | C | 学习效率/学习习惯中文长视频样本；标注“未经作者授权，禁止转载” |
| https://www.bilibili.com/video/BV1xh411a787/ | C | 早期 43 集合集样本；转载/自译，不能视为独立来源 |
| https://www.bilibili.com/video/BV1a2421Z7Rb/ | C | 学习与记忆双语字幕样本；页面注明 AI 识别字幕，存在识别错误 |
| https://www.bilibili.com/video/BV1XRtjzoEo4/ | C | 双语合集/压力、睡眠、专注样本；需逐项回链与去重 |
| https://www.bilibili.com/video/BV14dkGBQEWR/ | C | ADHD Essentials 中文字幕与附文稿样本；涉及处方药，必须医学核查 |
| https://www.bilibili.com/video/BV1aBEWzJE9i/ | C | YouTube 精译/中文介绍样本；转载性质明显 |
| https://www.bilibili.com/video/BV1NkRUBnEKo/ | C | 睡眠、学习与代谢中文配音长视频；页面给出 YouTube q-H_A_dQUxQ 回链，但配音/字幕仍是镜像层 |
| https://www.bilibili.com/video/BV1nk4y1A7zW/ | C | 睡眠学习系列汇编；包含多个 Episode，不能当作单一原始视频 |
| https://www.bilibili.com/video/BV1vSPCzkEVX/ | C | 每日工具与生产力中文长视频；涉及饮食、激素和补剂，尚未确认唯一原始视频 |
| https://www.bilibili.com/video/BV1z7gPzXEob/ | C | Marc Berman 双语长视频；章节超过两小时，尚未确认原始 YouTube ID |

Stanford 公开出版物目录已分页采集为 `references/catalog/publications.csv`，首轮共 59 条；它是“实验室研究语料”，与播客协议证据分开管理。
| https://time.com/6290594/andrew-hubman-lab-podcast-interview/ | B | 2023 年外部采访与科学传播/商业化争议 |
| https://doi.org/10.1057/s41599-020-0415-6 | B | 营养畅销书证据与商业激励背景；不是对 Huberman 的直接审查 |

## 去重和纳入规则

1. 主记录以 YouTube video ID 或官方 Episode URL 为键；B 站 BV 号作为镜像/翻译字段。
2. 同一 Episode 的 YouTube、官方网页、B 站搬运、Podcast 音频只算一个主张来源；不同嘉宾或不同年份的独立研究才另建记录。
3. 长视频优先：完整 Episode、正式嘉宾访谈、AMA、Journal Club；短剪辑仅做线索。
4. 语料最小元数据：标题、平台、原始发布者、日期、时长、URL/ID、字幕类型、是否完整、主题、证据状态。
5. 只有在来源身份、内容完整性和主张位置都能复核时，才把内容写入证据台账。

## B站专项登记原则

官方账号是平台同步证据，不代表 B 站字幕本身是学术证据；翻译版、机翻版和合集版都必须保留原始 YouTube/官方 Episode 回链。对未授权转载仅记录元数据和短摘要，不抓取或再分发完整字幕。当前映射由契约级 QA 逐条校验 YouTube ID 与 Episode URL 的同一性。
