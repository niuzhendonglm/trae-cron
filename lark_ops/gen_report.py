# -*- coding: utf-8 -*-
import json
from collections import Counter, OrderedDict

REPORT_DATE = "2026-10-14"
GEN_TIME = "2026-10-15 04:36"
DOC_URL = "https://inovance.feishu.cn/docx/SgW7dMmFcoHd3Tx8CoGcgl5VnGg"
BASE_URL = "https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot"

recs = [json.loads(l)["fields"] for l in open("qa_records.ndjson", encoding="utf-8") if l.strip()]
total = len(recs)
ai_n = sum(1 for r in recs if r.get("AI回复"))
human_n = total - ai_n
follow = ai_n

def pct(n):
    return f"{n/total*100:.1f}%"

tc = Counter(r["问题类型"] for r in recs)
ac = Counter(r["提问人"] for r in recs)
rc = Counter(r["回复人"] for r in recs)

L = []
L.append(f"# 运维日报 - {REPORT_DATE}")
L.append("")
L.append("## 📊 今日概览")
L.append(f"- **总问题数**: {total}")
L.append(f"- **已回答**: {human_n}")
L.append(f"- **待跟进**: {follow}")
L.append(f"- **AI 补充回复**: {ai_n}")
L.append("")
L.append("## 📋 问题分类统计")
L.append("| 问题类型 | 数量 | 占比 |")
L.append("|----------|------|------|")
for k, v in tc.most_common():
    L.append(f"| {k} | {v} | {pct(v)} |")
L.append("")
L.append("## 📋 提问人员统计")
L.append("| 提问人 | 数量 | 占比 |")
L.append("|----------|------|------|")
for k, v in ac.most_common():
    L.append(f"| {k} | {v} | {pct(v)} |")
L.append("")
L.append("## 📋 回复人员统计")
L.append("| 回复人 | 数量 | 占比 |")
L.append("|----------|------|------|")
for k, v in rc.most_common():
    L.append(f"| {k} | {v} | {pct(v)} |")
L.append("")
L.append("## 📝 详细问题及回复记录")

groups = OrderedDict()
for k, _ in tc.most_common():
    groups[k] = [r for r in recs if r["问题类型"] == k]

def brief(s, n):
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"

gi = 0
for gname, rows in groups.items():
    L.append(f"### {gname}问题 ({len(rows)} 个)")
    for r in rows:
        gi += 1
        mark = " 🤖" if r.get("AI回复") else ""
        L.append(f"{gi}. **{brief(r['Question'], 40)}** - {r['提问人']} → {r['回复人']}：{brief(r['Answer'], 90)}{mark}")
    L.append("")

L.append("## 🔔 待办事项")
todos = [
    ("高", "熊暾", "济南服务器 hvrd.inovance.com（10.76.248.68）https 切换后还剩一项配置待修改，改后需内外网/手机端回归验证", None),
    ("高", "牛振东/马海峰", "OMS 履行订单表授权方案拉通：确定直接授表还是建视图，对接 IT 侧李波", None),
    ("高", "蔺雨桐", "防接反检测系统 token 失效后未自动跳转登录页（首页数据全 0），扫码问题已优化、该项待改", None),
    ("高", "马海峰", "OMS 主要业务表 E-R 图待补（关联关系复杂，计划数据入湖后完善；表清单与 SQL 已交付）", None),
    ("中", "李守东/杨润东", "订单 IOC 应用架构与技术架构规划输出内容待明确，次日上午会议对齐（约万工参加）", None),
    ("中", "郭文庆", "InoAI 可用模型变为 Qwen3.5、Qwen3.7 可用性异常确认（余梦圆私聊跟进）", None),
    ("中", "徐翼", "智能会议纪要未收到问题排查（AI 回复：检查会议录制/纪要开关、确认自己在可见范围、在妙记中按日期搜索，仍无则提供会议号后台排查）", "AI"),
    ("中", "周明明", "DaaS 数据源连接数参数调整（生产建议 initialSize=100、maxActive=200），并为武销南/黄翔/杜彦永添加管理员", None),
    ("中", "蒋静芳/孙桦君/刘宏宇", "ST 驾驶舱报告解读数据对齐会（10-15 下午），对齐表字段翻译与指标口径", None),
    ("中", "何荣福", "业务方案 3.2 版补充杨威澄清内容；群发权限受限问题需解决", None),
    ("低", "金垠博", "编码属性资料确认与 SOP 生成字段映射（AI 回复：先对辨识属性四字段做完整性/唯一性校验，再与 SOP 模板字段对齐、确认取值口径）", "AI"),
    ("低", "葛士祺", "张兴建 AI IDE token 额度用尽（AI 回复：查账单额度与重置周期，紧急可管理员追加或付费扩容，日常缩短上下文省 token）", "AI"),
]
for pri, owner, desc, is_ai in todos:
    L.append(f"- [ ] **{pri}**: {owner} - {desc}")
L.append("")
L.append("## 📈 趋势分析")
L.append("- **问题量连续三日回落**：近 7 天有效 QA 量为 10-12 的 155 条 → 10-13 的 63 条（-59.4%）→ 10-14 的 46 条（-27.0%），周一高峰后逐步回归常态，收敛趋势明显。")
L.append("- **「工具使用」连续两日居首**：10-13 为 17 条（27.0%）、10-14 为 13 条（28.3%），主要来自 TRAE 用户群（计费/支付/套餐/客户端异常）与 DataWind、AI IDE 用户提问；而 10-12 的高频类型「技术讨论」（43 条）与「开发问题」（32 条）昨日分别回落至 4 条与 0 条，说明集中开发攻坚告一段落。")
L.append("- **AI 补充回复占比上升**：由 10-13 的 20.6%（13/63）升至 10-14 的 32.6%（15/46），无人回答的问题集中在外部用户群（TRAE 11/12 群、DataWind 沟通群、AI IDE 用户群），此类群缺少内部接口人实时答疑，建议安排轮值或接入自动答疑机器人。")
L.append("- **活跃人员变化**：提问侧牛振东升至第一（9 条，19.6%，10-13 为 6 条），主要围绕任务令异常订单项目、防接反检测与看板需求；刘宏宇由 6 条降至 3 条；回复侧 AI助手 15 条居首，人工回复以牛振东（6 条）、刘宏宇（4 条）为主，两人合计承担近 1/3 的人工答疑。")
L.append("- **运维类问题聚焦网络与访问链路**：昨日 7 条运维问题中 4 条与网络/访问相关（ERR_TIMED_OUT×2、InoAI 页面卡死、会议纪要未生成），其中 https 切换引发的访问异常涉及多个系统入口，建议对飞书应用首页地址统一巡检一遍 http/https 配置。")
L.append("")
L.append(f"*日报生成时间：{GEN_TIME}*")
L.append(f"*数据来源：AI学习记录多维表格（{BASE_URL}）*")

open("daily_report.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("lines:", len(L))
print(f"total={total} answered={human_n} follow={follow} ai={ai_n}")
