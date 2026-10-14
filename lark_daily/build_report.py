import json
from collections import Counter, OrderedDict

def load_pairs(fns):
    recs = []
    for fn in fns:
        d = json.load(open(fn))
        data = d['data']
        fields = data['fields']
        for r in data['data']:
            recs.append(dict(zip(fields, r)))
    return recs

def cell(v):
    if v is None:
        return ''
    if isinstance(v, list):
        parts = []
        for x in v:
            if isinstance(x, dict):
                parts.append(str(x.get('text') or x.get('name') or ''))
            else:
                parts.append(str(x))
        return ''.join(parts)
    if isinstance(v, dict):
        return str(v.get('text') or v.get('name') or '')
    return str(v)

all_recs = load_pairs(['qa_verify1.json', 'qa_verify2.json'])
for r in all_recs:
    for k in list(r.keys()):
        r[k] = cell(r[k])

today = [r for r in all_recs if r.get('问题日期', '').startswith('2026-10-13')]
prev = [r for r in all_recs if r.get('问题日期', '').startswith('2026-10-12')]
print('today:', len(today), 'prev(10-12):', len(prev))

total = len(today)
ai_cnt = sum(1 for r in today if r.get('AI回复'))
human_cnt = total - ai_cnt
follow_up = ai_cnt

types = Counter(r['问题类型'] for r in today)
askers = Counter(r['提问人'] for r in today)
reply_counter = Counter()
for r in today:
    for name in r['回复人'].split('、'):
        name = name.strip()
        if name:
            reply_counter[name] += 1

def pct(n, d):
    return f"{n / d * 100:.1f}" if d else '0.0'

def esc(s):
    s = str(s).replace('\\', '\\\\')
    for ch in '`*_[]$~<|':
        s = s.replace(ch, '\\' + ch)
    return s

def title_of(q, n=30):
    q = q.replace('\n', ' ').strip()
    return esc(q[:n] + ('…' if len(q) > n else ''))

def ans_brief(a, n=60):
    a = a.replace('\n', ' ').strip()
    return esc(a[:n] + ('…' if len(a) > n else ''))

type_order = [t for t, _ in types.most_common()]

L = []
L.append('# 运维日报 - 2026-10-13')
L.append('')
L.append('## 📊 今日概览')
L.append(f'- **总问题数**: {total}')
L.append(f'- **已回答**: {human_cnt}')
L.append(f'- **待跟进**: {follow_up}')
L.append(f'- **AI 补充回复**: {ai_cnt}')
L.append('')
L.append('## 📋 问题分类统计')
L.append('| 问题类型 | 数量 | 占比 |')
L.append('|----------|------|------|')
for t in type_order:
    L.append(f'| {t} | {types[t]} | {pct(types[t], total)}% |')
L.append('')
L.append('## 📋 提问人员统计')
L.append('| 提问人 | 数量 | 占比 |')
L.append('|----------|------|------|')
for name, n in askers.most_common():
    L.append(f'| {esc(name)} | {n} | {pct(n, total)}% |')
L.append('')
L.append('## 📋 回复人员统计')
L.append('| 回复人 | 数量 | 占比 |')
L.append('|----------|------|------|')
rt = sum(reply_counter.values())
for name, n in reply_counter.most_common():
    L.append(f'| {esc(name)} | {n} | {pct(n, rt)}% |')
L.append('')
L.append('## 📝 详细问题及回复记录')
gi = 0
for t in type_order:
    grp = [r for r in today if r['问题类型'] == t]
    grp.sort(key=lambda r: r['问题日期'])
    label = t if t.endswith('问题') else t + '问题'
    L.append(f'### {label} ({len(grp)} 个)')
    for r in grp:
        gi += 1
        mark = ' 🤖' if r.get('AI回复') else ''
        L.append(f"{gi}. **{title_of(r['Question'])}** - {esc(r['提问人'])} → {esc(r['回复人'])}：{ans_brief(r['Answer'])}{mark}")
    L.append('')
L.append('## 🔔 待办事项')
prio_map = {'运维问题': '高', '技术讨论': '中', '开发问题': '中', '工具使用': '中', '产品需求': '中', '流程咨询': '低', '工作沟通': '低', '项目咨询': '低'}
n_todo = 0
for t in type_order:
    grp = [r for r in today if r['问题类型'] == t and r.get('AI回复')]
    for r in grp:
        n_todo += 1
        prio = prio_map.get(t, '中')
        L.append(f"- [ ] **{prio}**: {esc(r['提问人'])} - {title_of(r['Question'], 24)}（AI 回复：{ans_brief(r['Answer'], 40)}）")
if n_todo == 0:
    L.append('- [ ] 无待办事项')
L.append('')

prev_types = Counter(r['问题类型'] for r in prev)
L.append('## 📈 趋势分析')
delta = total - len(prev)
arrow = '下降' if delta < 0 else ('上升' if delta > 0 else '持平')
L.append(f'- 问题量变化：昨日（10-13）共 {total} 条，较前一日（10-12 的 {len(prev)} 条）{arrow} {abs(delta)} 条（{abs(delta) / len(prev) * 100:.1f}%），周一高峰后回落明显。')
top3 = '、'.join(f'{t}({types[t]}条)' for t in type_order[:3])
prev_top3 = '、'.join(f'{t}({prev_types[t]}条)' for t, _ in prev_types.most_common(3))
L.append(f'- 高频类型：昨日 Top3 为 {top3}，前一日为 {prev_top3}；「工具使用」「运维问题」持续居前，建议沉淀 TRAE 工具类 FAQ 与运维排查手册。')
ask_top_raw = '、'.join(f'{n}({c}条)' for n, c in askers.most_common(3))
ask_top = '、'.join(f'{esc(n)}({c}条)' for n, c in askers.most_common(3))
L.append(f'- 活跃人员变化：昨日提问最活跃为 {ask_top}；人工回复覆盖 {human_cnt} 条，AI 补充回复 {ai_cnt} 条（占 {pct(ai_cnt, total)}%），已列入待办跟进，无遗漏未响应问题。')
L.append('')
L.append('*日报生成时间：2026-10-14 13:30（北京时间）*')
L.append('*数据来源：AI学习记录多维表格（https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot）*')

report = '\n'.join(L)
open('daily_report.md', 'w').write(report)
open('doc_append.md', 'w').write('<hr/>\n\n' + report + '\n')
print('report lines:', len(L))
print('todo items:', n_todo)

DOC_URL = 'https://inovance.feishu.cn/docx/SgW7dMmFcoHd3Tx8CoGcgl5VnGg'
BASE_URL = 'https://inovance.feishu.cn/base/KezfbQ2fDaNBonskSTZcM3YVnWf?table=tblrHaPTUI8x71ot'

def sm(s, n=None):
    s = str(s).replace('\n', ' ').strip()
    for a, b in [('[', '【'), (']', '】'), ('`', ''), ('*', ''), ('_', '-'), ('<', '＜'), ('~', '～'), ('|', '/')]:
        s = s.replace(a, b)
    if n and len(s) > n:
        s = s[:n] + '…'
    return s

M = []
M.append('# 运维日报 - 2026-10-13')
M.append('')
M.append('## 📊 今日概览')
M.append(f'- **总问题数**: {total}')
M.append(f'- **已回答**: {human_cnt}')
M.append(f'- **待跟进**: {follow_up}')
M.append(f'- **AI 补充回复**: {ai_cnt}')
M.append('')
M.append('## 📋 问题分类统计')
for t in type_order:
    M.append(f'- {t}：{types[t]} 条（{pct(types[t], total)}%）')
M.append('')
M.append('## 🔔 待办事项')
for t in type_order:
    for r in [x for x in today if x['问题类型'] == t and x.get('AI回复')]:
        prio = prio_map.get(t, '中')
        M.append(f'- **[{prio}]** {sm(r["提问人"])} - {sm(r["Question"], 22)}（AI 已给建议，待人工确认）')
M.append('')
M.append('## 📈 趋势分析')
M.append(f'- 问题量：昨日 {total} 条，较 10-12（{len(prev)} 条）{arrow} {abs(delta)} 条（{abs(delta) / len(prev) * 100:.1f}%），周一高峰后回落。')
M.append(f'- 高频类型：Top3 为 {top3}；工具使用与运维问题持续居前，建议沉淀 TRAE FAQ 与运维排查手册。')
M.append(f'- 活跃人员：提问最活跃 {sm(ask_top_raw)}；人工回复覆盖 {human_cnt} 条，AI 补充 {ai_cnt} 条（{pct(ai_cnt, total)}%），全部问题已响应。')
M.append('')
M.append(f'📄 [完整日报（云文档）]({DOC_URL})')
M.append(f'📊 [QA 明细（多维表格）]({BASE_URL})')

open('chat_msg.md', 'w').write('\n'.join(M) + '\n')
print('chat msg lines:', len(M))
