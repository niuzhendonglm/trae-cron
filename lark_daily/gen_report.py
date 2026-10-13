import json, collections, datetime

DATE = "2026-10-12"
recs = json.load(open('/workspace/lark_daily/qa_final.json'))
metas = [r['_meta'] for r in recs]

total = len(metas)
ai_recs = [r for r in recs if not r['_meta']['human']]
human_n = total - len(ai_recs)
pending_n = len(ai_recs)

types = collections.Counter(m['qtype'] for m in metas)
askers = collections.Counter(m['asker'] for m in metas)
answerers = collections.Counter(m['answerer'] for m in metas)

hist = [json.loads(l) for l in open('/workspace/lark_daily/qa_history_all.ndjson') if l.strip()]
hist = [h for h in hist if str(h.get('问题日期', ''))[:10] != DATE]
hist_types = collections.Counter(h.get('问题类型', '') for h in hist)

def pct(n, d=total):
    return f"{n/d*100:.1f}%" if d else "0%"

def one_line(s, n):
    s = ' '.join(str(s).split())
    return s[:n] + ('…' if len(s) > n else '')

def title_of(q):
    return one_line(q, 32)

L = []
L.append(f"# 运维日报 - {DATE}")
L.append("")
L.append("## 📊 今日概览")
L.append(f"- **总问题数**: {total}")
L.append(f"- **已回答**: {human_n}")
L.append(f"- **待跟进**: {pending_n}（AI 已补充回复，待人工确认跟进）")
L.append(f"- **AI 补充回复**: {len(ai_recs)}")
L.append("")
L.append("## 📋 问题分类统计")
L.append("| 问题类型 | 数量 | 占比 |")
L.append("|----------|------|------|")
for t, c in types.most_common():
    L.append(f"| {t} | {c} | {pct(c)} |")
L.append("")
L.append("## 📋 提问人员统计")
L.append("| 提问人 | 数量 | 占比 |")
L.append("|----------|------|------|")
for a, c in askers.most_common():
    L.append(f"| {a} | {c} | {pct(c)} |")
L.append("")
L.append("## 📋 回复人员统计")
L.append("| 回复人 | 数量 | 占比 |")
L.append("|----------|------|------|")
for a, c in answerers.most_common():
    L.append(f"| {a} | {c} | {pct(c)} |")
L.append("")
L.append("## 📝 详细问题及回复记录")
by_type = collections.OrderedDict()
for r in recs:
    by_type.setdefault(r['_meta']['qtype'], []).append(r)
for t, rs in by_type.items():
    L.append(f"### {t}问题 ({len(rs)} 个)")
    for i, r in enumerate(rs, 1):
        m = r['_meta']
        mark = " 🤖" if not m['human'] else ""
        ans = one_line(r['Answer'], 100)
        q = title_of(r['Question'])
        L.append(f"{i}. **{q}** - {m['asker']} → {m['answerer']}：{ans}{mark}")
    L.append("")
L.append("## 🔔 待办事项")
PRI = {"运维问题": "高", "开发问题": "高", "产品需求": "中"}
for r in ai_recs:
    m = r['_meta']
    pri = PRI.get(m['qtype'], "中")
    L.append(f"- [ ] **{pri}**: {m['asker']} - {one_line(m['q'], 40)}（AI 回复：{one_line(r['Answer'], 60)}）")
L.append("")
L.append("## 📈 趋势分析")
top2 = types.most_common(2)
L.append(f"- 问题量变化：昨日新增 {total} 条 QA 记录；「群消息抓取」表近 7 天（2026-10-06 ~ 2026-10-11）无历史数据，本次为该周期首次自动收集，暂无日环比。表内既有历史基线为 2025-10-13/14 共 {len(hist)} 条（约 {len(hist)/2:.0f} 条/天），昨日问题量约为该基线日均的 {total/(len(hist)/2):.1f} 倍，群内讨论活跃度显著提升。")
L.append(f"- 高频类型：{top2[0][0]}（{top2[0][1]} 条，{pct(top2[0][1])}）与 {top2[1][0]}（{top2[1][1]} 条，{pct(top2[1][1])}）合计占比超五成；与历史基线（技术讨论 {hist_types.get('技术讨论',0)} 条、工具使用 {hist_types.get('工具使用',0)} 条）结构基本一致，但开发问题由历史 {hist_types.get('开发问题',0)} 条升至 {types.get('开发问题',0)} 条，反映数据开发/任务令相关讨论明显增多。")
top_ask = askers.most_common(3)
L.append(f"- 活跃人员变化：提问 Top3 为 {top_ask[0][0]}（{top_ask[0][1]} 条）、{top_ask[1][0]}（{top_ask[1][1]} 条）、{top_ask[2][0]}（{top_ask[2][1]} 条）；回复 Top3 为 牛振东（{answerers.get('牛振东',0)} 条）、蔺雨桐（{answerers.get('蔺雨桐',0)} 条）、刘宏宇（{answerers.get('刘宏宇',0)} 条），核心贡献者与历史基线（牛振东/蔺雨桐/刘宏宇 同列前排）保持一致；人工回答率 {pct(human_n)}，其余 {len(ai_recs)} 条由 AI 助手补充回复（{pct(len(ai_recs))}）。")
L.append("")
gen_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
L.append(f"*日报生成时间：{gen_time}（北京时间）*")
L.append("*数据来源：AI学习记录多维表格（https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot）*")

report = "\n".join(L)
open('/workspace/lark_daily/daily_report.md', 'w').write(report)

core = []
core.append(f"# 运维日报 - {DATE}")
core.append("")
core.append("## 📊 今日概览")
core.append(f"- **总问题数**: {total}")
core.append(f"- **已回答**: {human_n}")
core.append(f"- **待跟进**: {pending_n}（AI 已补充回复，待人工确认）")
core.append(f"- **AI 补充回复**: {len(ai_recs)}")
core.append("")
core.append("## 📋 问题分类统计")
core.append("| 问题类型 | 数量 | 占比 |")
core.append("|----------|------|------|")
for t, c in types.most_common():
    core.append(f"| {t} | {c} | {pct(c)} |")
core.append("")
core.append("## 🔔 待办事项")
for r in ai_recs:
    m = r['_meta']
    pri = PRI.get(m['qtype'], "中")
    core.append(f"- [ ] **{pri}**: {m['asker']} - {one_line(m['q'], 40)}（AI 回复：{one_line(r['Answer'], 50)}）")
core.append("")
core.append("## 📈 趋势分析")
core.append(f"- 昨日新增 {total} 条 QA，近 7 天无历史数据（首次自动收集）；较表内 2025-10 基线日均 {len(hist)/2:.0f} 条提升约 {total/(len(hist)/2):.1f} 倍。")
core.append(f"- 高频类型：{top2[0][0]}（{pct(top2[0][1])}）、{top2[1][0]}（{pct(top2[1][1])}），开发问题讨论较历史明显增多。")
core.append(f"- 活跃 Top3：提问 {top_ask[0][0]}/{top_ask[1][0]}/{top_ask[2][0]}，回复 牛振东/蔺雨桐/刘宏宇；人工回答率 {pct(human_n)}。")
core.append("")
core.append("📄 完整日报（含全部 QA 明细）：https://inovance.feishu.cn/docx/SgW7dMmFcoHd3Tx8CoGcgl5VnGg")
core.append("📊 多维表格数据：https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot")
core_msg = "\n".join(core)
open('/workspace/lark_daily/chat_message.md', 'w').write(core_msg)

print("report bytes:", len(report.encode()), "| chat msg bytes:", len(core_msg.encode()))
print("detail entries:", sum(len(v) for v in by_type.values()), "| todos:", len(ai_recs))
