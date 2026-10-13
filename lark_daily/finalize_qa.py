import json, re

d = json.load(open('/workspace/lark_daily/qa_curated.json'))
kh = d['kept_human']
ka = d['kept_ai']
msgs = json.load(open('/workspace/lark_daily/valid_strict.json'))
raw_by_id = {m['message_id']: str(m.get('content', '')) for m in msgs}

def san(s):
    if not isinstance(s, str):
        s = str(s or '')
    s = re.sub(r'<at user_id="all"\s*>(.*?)</at>', '@所有人', s)
    s = re.sub(r'<at user_id="all"\s*/>', '@所有人', s)
    s = re.sub(r'<at user_id="([^"]*)"\s*>(.*?)</at>', lambda m: '@' + (m.group(2) or '提及'), s)
    s = re.sub(r'<at user_id="([^"]*)"\s*/>', '@提及', s)
    s = re.sub(r'</?p>', '', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    return s.strip()

AI_ANSWERS = {
 2: "不完全正确。直接通过 API/SDK（如 OpenAI Chat Completions 格式的 HTTP 调用）即可与大模型通信，并不需要 Agent；Agent 是构建在 LLM 之上的编排层，负责工具调用、上下文与记忆管理、任务拆解和多步执行。没有 Agent 你依然可以和 LLM 通信，只是需要自己实现提示词组织、结果解析等配套逻辑。",
 5: "HIVE2Doris 迁移任务常见两种处理方式：1) 全量覆盖场景：在导入配置中增加导入前语句（TRUNCATE TABLE 目标表 或 DELETE FROM 目标表 WHERE ...），每次先清空再导入，避免数据重复；2) 增量更新场景：目标表采用 Doris Unique Key 模型建表，导入时映射业务主键字段实现 upsert。由于目标表非你创建，建议先 SHOW CREATE TABLE 确认数据模型（DUPLICATE/UNIQUE KEY），再与杨润东确认业务上是全量还是增量，选择对应方案。",
 7: "可以。操作建议：将黄金钢的账号加入设备驾驶舱管理员用户组，添加后请其刷新页面验证菜单与数据可见性；同时按最小权限原则仅开通本次所需权限，并在权限台账中登记该次权限变更，到期或使用结束后及时回收。",
 10: "Online 表单的『同步数据库』会以表单设计器中的字段定义覆盖数据库表结构，未在表单里配置的数据库端默认值会在同步时被清掉。正确做法：先在 Online 表单设计器中为字段配置默认值，再执行同步；如默认值已被清空，可手动执行 ALTER TABLE ... ALTER COLUMN ... SET DEFAULT ... 恢复。建议同步前用 SHOW CREATE TABLE 或截图备份表结构，便于对照恢复。",
 13: "InnClaw 获取途径建议：1) 在 InoAI知识社区 的置顶公告和群文件库中查找最新版本的下载链接或安装包；2) 若未找到，直接在群里 @社区管理员/运营同学 索取下载地址；3) 安装后使用域账号登录。版本更新时社区公告会同步刷新，请以公告中的最新地址为准。",
 14: "DataWind 支持在同一张底表（数据集）中使用多个指标：在图表中添加多个度量字段，通过图例或『指标卡/选项卡』组件切换展示；若要实现用户侧下拉切换指标的效果，可用参数控件配合计算字段（CASE WHEN 参数=指标A THEN ... END）实现。若指标口径分散在不同底表，需先在数据准备层建模到同一数据集。具体版本的功能差异建议与火山引擎售后支持确认。",
 16: "可通过以下途径查看系统表单字段：1) 在 DaaS/数据平台的数据地图（元数据管理）中搜索目标表单，查看字段清单与字段注释；2) 请系统管理员从后台导出表单字段定义（如 SELECT * FROM information_schema.columns WHERE table_name='目标表'）；3) 任务令相关字段重点关注任务令编号、工序、状态、时间类字段，并请表单负责人确认字段口径后再使用。",
 17: "该需求可落地：以『承诺上线日期/承诺入库日期』为基准，关联 MES 实际上线时间与入库记录，计算『按期上线率』『按期入库率』两项指标并标记异常明细；再按周/月维度搭建看板，展示正常上线/未正常上线数量、生产过程异常暴露情况及趋势图，在周例会、月例会前自动推送给相关人员。建议先确认承诺日期字段的数据来源与维护责任人，再提交产品需求排期开发。",
 20: "建议直接查看代码提交记录定位修改点：git log / git diff 查看最近一次提交改动的文件与逻辑；若通过平台发布，可在版本历史或变更清单中查看。如拿不到 diff，可请修改人列出本次变更涉及的模块、文件与影响范围，再据此做针对性回归测试。",
 22: "不是弃用，而是产品线整合：原 TRAE Work（办公）与 TRAE Code（开发）已统一为一个 TRAE 产品，一个入口同时包含 Agent 模式（承接原 Work 的办公/Design 能力）和 IDE 模式（承接原 Code 的深度编码能力），一键切换、数据互通；升级时系统会自动合并聊天记录与账号数据。IDE 模式的编码能力仍在持续迭代，无需担心被弃用。",
 24: "飞书本身是 SaaS 服务，不会主动访问你的内网服务器。当飞书开放平台需要向业务系统推送事件（消息回调等）时，要求提供公网可访问的回调地址；内网部署通常两种方案：1) 通过公网网关/反向代理（nginx + IP 白名单）暴露 HTTPS 回调入口；2) 使用飞书长连接（WebSocket）模式，由 SDK 主动向飞书服务端建立出站连接，无需公网回调，更适合内网环境。",
 25: "建议通过以下渠道确认济南高压电缆项目涉及的线路：1) 查阅项目立项材料/需求说明中的工程范围与线路清单附件；2) 与项目电气设计负责人核对电缆 BOM 与接线表；3) 直接与谢工确认线路编号、电压等级与所属间隔，并将清单归档到项目文档，作为后续测试与验收依据。",
 119: "文件传输请求建议：请对方直接在会话中发送文件附件，或上传到飞书云空间后分享链接（设置好访问权限）；若文件用于平台功能测试，请同时附上复现步骤与预期结果。如涉及 DaaS 平台功能异常，按平台标准化流程在工单系统提交服务单并上传相关文件，由平台团队跟进处理。",
}

KA_KEEP_AI = [2, 5, 7, 10, 13, 14, 16, 17, 20, 22, 24, 25]
KA_REPAIR = 9
KA_DROP = [0, 1, 3, 4, 6, 8, 11, 12, 15, 18, 19, 21, 23]

KH_DROP = [59, 60, 103]
KH_TO_AI = 119

RULES = [
    ("流程咨询", ["流程", "审批", "提单", "工单", "服务单", "规范", "标准", "OA", "汇报", "报销", "申请"]),
    ("产品需求", ["需求", "述求", "诉求", "我想", "希望", "建议", "可以展现", "能否支持", "功能", "新增", "优化", "能不能加"]),
    ("运维问题", ["报错", "异常", "故障", "无法访问", "打不开", "卡顿", "宕机", "超时", "权限", "账号", "部署", "很慢", "太慢", "失败", "用户组", "管理员", "没数据", "没有数据"]),
    ("开发问题", ["代码", "bug", "Bug", "BUG", "字段", "数据库", "SQL", "sql", "hive", "HIVE", "doris", "Doris", "接口", "脚本", "同步", "提交", "合并", "默认值", "改的", "改哪", "开发", "函数", "表结构", "git", "任务令", "入湖", "建模", "小数", "百分比", "数据"]),
    ("工具使用", ["下载", "安装", "怎么用", "如何使用", "使用", "配置", "工具", "模型", "trae", "TRAE", "Trae", "表单", "地址", "看板", "DataWind", "datawind", "是否支持", "切换", "agent", "Agent", "新版"]),
    ("项目咨询", ["项目", "线路", "排产", "现场", "工厂", "电缆", "车间"]),
]

CHAT_HINTS = [
    ("TRAE", "工具使用"),
    ("推送监控", "运维问题"),
    ("售后", "运维问题"),
    ("SQL", "开发问题"),
    ("Doris", "开发问题"),
    ("数据分析", "开发问题"),
    ("DaaS", "运维问题"),
]

def classify(q, chat=''):
    for name, kws in RULES:
        for kw in kws:
            if kw in q:
                return name
    for kw, name in CHAT_HINTS:
        if kw in chat:
            return name
    return "技术讨论"

records = []

def add_rec(r, answer, answerer, ai_reply, source):
    q = san(r['question'])[:1500]
    a = san(answer)[:3000]
    asker = san(r['asker'])
    answerer = san(answerer)
    qtype = classify(r['question'], r.get('chat_name', ''))
    raw = san(raw_by_id.get(r['q_msg_id'], r['question']))[:3000]
    rec = {
        "Question": q, "Answer": a, "提问人": asker, "回复人": answerer,
        "问题日期": r['q_iso'], "问题类型": qtype, "文本": raw or q,
    }
    if ai_reply:
        rec["AI回复"] = san(ai_reply)
    for f in ["Question", "Answer", "提问人", "回复人", "问题类型", "问题日期"]:
        assert rec.get(f), (f, rec)
    records.append({**rec, "_meta": {"source": source, "asker": asker, "answerer": answerer,
                                      "qtype": qtype, "human": not ai_reply, "qtime": r['q_iso'],
                                      "chat": r.get('chat_name', ''), "q": q[:60]}})

for i, r in enumerate(kh):
    if i in KH_DROP or i == KH_TO_AI:
        continue
    add_rec(r, r['answer'], r['answerer'], None, 'human:' + r.get('answer_source', ''))

r9 = ka[KA_REPAIR]
add_rec(r9, "数据库加的字段，Online表单改的表格", "蔺雨桐", None, 'human:manual')

r119 = kh[KH_TO_AI]
add_rec(r119, AI_ANSWERS[119], "AI助手", AI_ANSWERS[119], 'ai')

for i in KA_KEEP_AI:
    r = ka[i]
    add_rec(r, AI_ANSWERS[i], "AI助手", AI_ANSWERS[i], 'ai')

out = [rec for rec in records]
json.dump(out, open('/workspace/lark_daily/qa_final.json', 'w'), ensure_ascii=False, indent=1)

from collections import Counter
ct = Counter(rec['_meta']['qtype'] for rec in out)
hu = sum(1 for rec in out if rec['_meta']['human'])
ai = len(out) - hu
ask = Counter(rec['_meta']['asker'] for rec in out)
answ = Counter(rec['_meta']['answerer'] for rec in out)
print('total', len(out), '| human', hu, '| ai', ai)
print('types', dict(ct))
print('top askers', ask.most_common(10))
print('top answerers', answ.most_common(10))
print('ai items:')
for rec in out:
    if not rec['_meta']['human']:
        print('  -', rec['_meta']['asker'], '|', rec['_meta']['qtype'], '|', rec['_meta']['q'][:50])
