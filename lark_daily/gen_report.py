import json, glob, subprocess, os
from collections import Counter, OrderedDict

NOW = subprocess.check_output(
    ['date', '+%Y-%m-%d %H:%M:%S'],
    env=dict(os.environ, TZ='Asia/Shanghai')).decode().strip()

# ---- load yesterday's 62 QA records (full fields) from the batch files we wrote ----
yest = []
for f in sorted(glob.glob('/tmp/batches/qa_*.json')):
    d = json.load(open(f))
    for r in d['create_records']:
        yest.append(r['fields'])
assert len(yest) == 62, len(yest)

# ---- load full table for 7-day trend ----
allrows = []
with open('/tmp/qa_all.ndjson') as fh:
    for line in fh:
        line = line.strip()
        if line:
            try: allrows.append(json.loads(line))
            except: pass
def day(r): return (r.get('问题日期') or '')[:10]

TOTAL = len(yest)
def is_ai(r): return (r.get('回复人') or '') == 'AI助手'
ai_rows = [r for r in yest if is_ai(r)]
AI_N = len(ai_rows)
PENDING = AI_N            # 无人工回复、由AI补充、待人工跟进
ANSWERED = TOTAL - PENDING

# ---- distributions ----
tc = Counter(r.get('问题类型') or '未分类' for r in yest)
ac = Counter(r.get('提问人') or '?' for r in yest)
rc = Counter(r.get('回复人') or '?' for r in yest)
def pct(n, d=TOTAL): return f"{n*100.0/d:.1f}%"

# ---- 7-day trend ----
days = ['2026-10-%02d' % d for d in range(20, 27)]
dc = Counter(day(r) for r in allrows)
last7 = [r for r in allrows if day(r) in days]
tc7 = Counter(r.get('问题类型') or '未分类' for r in last7)
prev_n = dc.get('2026-10-25', 0)
cur_n = dc.get('2026-10-26', 0)
delta = ((cur_n - prev_n) * 100.0 / prev_n) if prev_n else 0

def trunc(s, n):
    s = (s or '').replace('\n', ' ').replace('|', '／').strip()
    return s if len(s) <= n else s[:n] + '…'

# ---- build detail section grouped by type ----
type_order = [t for t, _ in tc.most_common()]
detail_lines = []
for t in type_order:
    recs = [r for r in yest if (r.get('问题类型') or '未分类') == t]
    # priority: AI/pending first, then others
    recs.sort(key=lambda r: (0 if is_ai(r) else 1))
    detail_lines.append(f"### {t} ({len(recs)} 个)")
    show = recs[:10]
    for i, r in enumerate(show, 1):
        mark = "🤖 ⏳待跟进" if is_ai(r) else "✅"
        q = trunc(r.get('Question'), 34)
        a = trunc(r.get('Answer'), 60)
        detail_lines.append(f"{i}. **{q}** - {r.get('提问人')} → {r.get('回复人')}：{a} {mark}")
    if len(recs) > 10:
        detail_lines.append(f"另有 {len(recs)-10} 条同类问题，详见多维表格")
    detail_lines.append("")

# ---- todo section from AI/pending rows ----
hi_types = {'运维问题', '开发问题', '技术讨论'}
todo_lines = []
for r in ai_rows:
    pri = "高" if (r.get('问题类型') in hi_types) else "中"
    todo_lines.append(f"- [ ] **{pri}**: {r.get('提问人')} - {trunc(r.get('Question'),40)}（AI 回复：{trunc(r.get('Answer'),70)}）")

# ---- assemble report ----
L = []
L.append("# 运维日报 - 2026-10-26")
L.append("")
L.append("## 📊 今日概览")
L.append(f"- **总问题数**: {TOTAL}")
L.append(f"- **已回答**: {ANSWERED}")
L.append(f"- **待跟进**: {PENDING}")
L.append(f"- **AI 补充回复**: {AI_N}")
L.append("")
L.append("## 📋 问题分类统计")
L.append("| 问题类型 | 数量 | 占比 |")
L.append("|----------|------|------|")
for t, n in tc.most_common():
    L.append(f"| {t} | {n} | {pct(n)} |")
L.append("")
L.append("## 📋 提问人员统计")
L.append("| 提问人 | 数量 | 占比 |")
L.append("|----------|------|------|")
multi_a = [(k, v) for k, v in ac.most_common() if v >= 2]
single_a = [k for k, v in ac.items() if v == 1]
for k, v in multi_a:
    L.append(f"| {k} | {v} | {pct(v)} |")
if single_a:
    L.append(f"| 其他（{len(single_a)} 人各 1 条） | {len(single_a)} | {pct(len(single_a))} |")
L.append("")
L.append("## 📋 回复人员统计")
L.append("| 回复人 | 数量 | 占比 |")
L.append("|----------|------|------|")
multi_r = [(k, v) for k, v in rc.most_common() if v >= 2]
single_r = [k for k, v in rc.items() if v == 1]
for k, v in multi_r:
    L.append(f"| {k} | {v} | {pct(v)} |")
if single_r:
    L.append(f"| 其他（{len(single_r)} 人各 1 条） | {len(single_r)} | {pct(len(single_r))} |")
L.append("")
L.append("## 📝 详细问题及回复记录")
L.extend(detail_lines)
L.append("## 🔔 待办事项")
L.extend(todo_lines)
L.append("")
L.append("## 📈 趋势分析")
top3_7 = tc7.most_common(3)
top3_str = "、".join(f"{k}({v})" for k, v in top3_7)
L.append(f"- **问题量变化**: 昨日({cur_n} 条)较前日 10-25({prev_n} 条)上升 {delta:.0f}%，为近 7 天峰值；近 7 天日问题量为 " + "、".join(f"{d[5:]}:{dc.get(d,0)}" for d in days) + "。")
L.append(f"- **高频类型**: 昨日以「{tc.most_common(1)[0][0]}」({tc.most_common(1)[0][1]} 条, {pct(tc.most_common(1)[0][1])})居首；近 7 天累计三大高频类型为 {top3_str}，运维与工具类问题持续占主导。")
top_asker = ac.most_common(1)[0]
top_replier = rc.most_common(1)[0]
L.append(f"- **活跃人员变化**: 提问端「{top_asker[0]}」最活跃({top_asker[1]} 条)，回复端「{top_replier[0]}」承担最多答疑({top_replier[1]} 条)；AI 助手补充回复 {AI_N} 条(占 {pct(AI_N)})，即无人工跟进比例 {pct(PENDING)}，需相关责任人及时认领。")
L.append("")
L.append(f"*日报生成时间：{NOW}*")
L.append("*数据来源：AI学习记录多维表格（https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot）*")
L.append("")
L.append("---")
L.append("")

open('report.md', 'w').write("\n".join(L))
print("report.md written, lines:", len(L))
print("TOTAL",TOTAL,"ANSWERED",ANSWERED,"PENDING",PENDING,"AI",AI_N)
print("types",dict(tc))
print("delta%",round(delta))
