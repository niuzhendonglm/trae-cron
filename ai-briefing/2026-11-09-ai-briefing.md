# 每日 AI 新闻简报【Trae】

**数据日期**：2026-11-09（周一）
**本次收录**：8 条新闻
**覆盖时段**：最近 24 小时（2026-11-08 12:00 ~ 2026-11-09 12:00，北京时间）

---

## 1.【融资】Anthropic 被曝 34 亿美元采购 1.7GW 燃气发电机组

据 FT 独家、Reuters 同日跟进，Anthropic 于 9 月下旬与德州圣安东尼奥供应商 OnePWR Solutions 达成协议，采购总装机 1.7GW 的重型燃气发电机组（含安装工程所需的工程设计与施工能力），折合约 200 万美元/MW，是目前已知 AI 实验室最大单笔发电设备采购；Anthropic 未收购 OnePWR，供应商也无员工转移，交易与其 S-1/A 中披露的「电力供给受限」风险项相互印证。

**来源**：Financial Times（首发）／ Reuters（The Star、TipRanks The Fly、新浪财经转载）
**时间**：2026-11-08（FT 首发），11-09 中文媒体跟进

---

## 2.【标准】美国联邦 AI 标准机构 CAISSI 人员被要求非正式向白宫汇报

AP 报道，商务部下设「超级智能创新与标准促进中心」（CAISSI，前身为美国 AI 标准与创新中心）官员近期被要求非正式向白宫某办公室汇报；该中心目前无常任负责人、已停止公开发布研究成果、年预算约 1,000 万美元（约为英国 AI Security Institute 的 1/8）。白宫回应称 Trump 已正式设立由 DNI Jay Clayton 领衔的 Super Intelligence Force，并已委托 PCAST 出具 AI 风险报告。

**来源**：AP News（记者 Garance Burke）
**时间**：2026-11-08

---

## 3.【安全】Anthropic 首次回应 Claude Code「Don't Ask Again」明文密钥泄露

安全公司 Apiiro 研究发现，公开 GitHub 仓库中的 `.claude/settings.local.json` 存在明文密钥：媒体口径为 1,122 份公开文件含 1,379 个真实密钥（379 个数据库口令、43 个 SSH、42 个 GitHub/GitLab/npm token、23 个 AWS key，涉及 63 家组织），计入 git 历史版本、fork 与共享 settings.json 后聚合口径为 2,539 个密钥 / 1,994 个仓库。Claude Code 负责人 Boris Cherny 于 11-08 在 Hacker News 回应称该文件「本应只在本地」、权限规则属旧机制应改用 auto mode 并开启 secret scanning；Anthropic 尚未发布官方博客或声明。

**来源**：The Hacker News／Apiiro 研究原文／Slashdot
**时间**：2026-11-07 报道，2026-11-08 厂商回应

---

## 4.【产品】LG AI Research 免费开放 K-EXAONE 2.5 API

LG AI 研究院在首尔「NVIDIA AI Day Seoul 2026」宣布，K-EXAONE 2.5（8 月版本基础上追加训练的技术验证模型）API 经 docs.exaone.ai 免费开放，任何人可申领 key。LG 称其在 24 项指标上于 8 周内综合性能提升 70% 以上，agentic 自评分数为 AutomationBench 74.6、Claw-Eval 77.3、BrowseComp 78.0、SWE-Bench Pro 59.2（对比 DeepSeek V4.1 Flash 与 GLM 5.3 max）。上述数字均为厂商基于开放数据集自测，无第三方独立复测。

**来源**：LG 官方新闻稿／Chosun English／新浪科技
**时间**：2026-11-09

---

## 5.【融资】AI+材料研发公司「清析智研」完成近亿元天使轮

成立不到半年的 AI for Materials 公司清析智研披露近亿元天使轮融资，投资方包括中芯聚源、高瓴创投、智元机器人、风物资本、东方嘉富及多家产业基金，多维资本担任独家财务顾问。产业资本（半导体、机器人）与一线 VC 同时进入材料研发 AI 早期项目，是本笔交易的主要信号。

**来源**：36氪（首发）／新浪财经（独家）
**时间**：2026-11-09

---

## 6.【融资】AI 药物设计公司「途深智合」完成 Pre-A 及 Pre-A+ 轮数亿元融资

无锡途深智合人工智能科技（ToursynClaw 蛋白质/药物设计平台）披露 Pre-A 与 Pre-A+ 两轮合计数亿元人民币融资：Pre-A 由上海科创集团领投，中生引领、舟山途毅参投；Pre-A+ 由金鼎资本、镁伽科技、清科控股联合投资；凯乘资本任独家 FA。具体单笔金额与估值未披露。

**来源**：投资界／新浪科技
**时间**：2026-11-08

---

## 7.【产品】Nous Research 为 Hermes Agent 上线官方 Security 插件

Nous Research 发布官方安全审查插件 hermes-security（v0.1.2，Apache-2.0，需 Hermes ≥ 0.21.5）：先建立威胁模型与信任边界，按约 4,000 行/块切分代码，最多 10 个并行 subagent 复核并回查攻击者可达性；提供 standard/deep/diff 三种模式，standard 模式覆盖上限 90 块（约 36 万行），超限按路由、输入、shell、SQL、反序列化、auth、webhook 风险排序；集成 Google osv-scanner（SHA-256 pin 校验）与 endoflife.date，报告可导出 Markdown/JSON/CSV/SARIF，并映射 OWASP Top 10:2025 与 ASVS 5.0.0。未公布任何 benchmark 分数。

**来源**：Nous Research 官方 X／Hermes Agent 官方插件文档
**时间**：2026-11-08

---

## 8.【标准】上海新增 5 款已登记生成式 AI 服务，累计达 264 款

据「网信上海」，截至 11 月 9 日上海新增 5 款已完成登记的生成式人工智能服务，累计 264 款。已上线应用须在显著位置标明上线编号，并按《人工智能生成合成内容标识办法》添加生成合成内容标识。（网信办「第十九批深度合成算法备案公告」为 11-04，不在本期窗口内。）

**来源**：网信上海／界面新闻（腾讯新闻转载）
**时间**：2026-11-09

---

## 今日趋势点评

周末为新闻低谷，主线落在「算力—资本—治理」三角：Anthropic 34 亿美元锁定 1.7GW 燃气发电机组，把「AI 缺电」从 S-1 里的风险提示变成真实采购订单，也为其 IPO 前的成本叙事加注（Bloomberg 11-06 报道称潜在买家讨论的估值区间已降至 1.1–1.3 万亿美元）。治理端一紧一稳——美国 CAISSI 被要求非正式向白宫汇报引发评估独立性担忧，中国则以生成式 AI 服务登记与内容标识延续「备案 + 标识」的合规路径。技术侧因 arXiv 周末无新公告批次而缺少重量级论文，资金明显转向 AI for Science 早期项目与编码代理的安全工程能力。

---

## 附：核查说明

- 本期已剔除的传闻/旧闻：OpenAI 110 亿美元融资（1.25 万亿估值，Reuters/Bloomberg 首发日为 11-06，窗口外，仅作点评背景）；Anthropic 估值「腰斩至约 1 万亿」（仅 X 账号说法，无一手来源）；Maritaca S5-nano、小米 MiMo 新架构、OpenAI Dots 提取 2FA 验证码、Factory 上线 Microsoft Teams（均只有单一 X 帖，官方渠道无法复核）；Claude Opus 5.5（09-22）、GPT-6（10-07）、Anthropic S-1（10-26）、Cursor Voice Chat（11-06）、Nous Arete-27B（11-06）、Thinking Machines Inkling 2 Small（11-05）。
- 「物理 AI 公司 DeepMind 完成数亿元 B 轮、晶科能源领投」经核查为线索混淆：实为**深度智控（DeepCtrls）**2026-07-09 的 B 轮（晶科能源战略投资）与**深度原理（Deep Principle）**2026-07 的 A 系列近 10 亿元，两家均非 DeepMind，且均为 4 个月前旧闻，不予采用。
- 本期无【论文】维度条目：arXiv cs.CL / cs.LG 最新公告批次停留在 2026-11-06（周五），周末无新批次。
