# -*- coding: utf-8 -*-
import json, re

msgs = json.load(open('/tmp/all_msgs_raw.json'))

def find_items(o):
    if isinstance(o, list): return o
    if isinstance(o, dict):
        if 'items' in o: return o['items']
        for v in o.values():
            r = find_items(v)
            if r: return r
    return None

chats = find_items(json.load(open('/tmp/chatlist.json')))
cmap = {c['chat_id']: c for c in chats}

def ctype(cid):
    m = (cmap.get(cid) or {}).get('chat_mode', '')
    return '群聊' if m == 'group' else ('单聊' if m == 'p2p' else m or '未知')

def cname(cid):
    return (cmap.get(cid) or {}).get('name', '') or cid

def iso(t):
    t = t.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', t):
        return t + ':00+08:00'
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', t):
        return t + '+08:00'
    return t

def clip(s, n=1800):
    s = s or ''
    return s[:n]

msg_records = []
seen_ids = set()

roots = [x for x in msgs if x.get('sender', {}).get('sender_type') == 'user' and not x.get('deleted')]
replies = []
for x in msgs:
    for r in x.get('thread_replies') or []:
        if r.get('sender', {}).get('sender_type') == 'user' and not r.get('deleted'):
            replies.append(r)

for x in roots + replies:
    mid = x.get('message_id', '')
    if mid and mid in seen_ids:
        continue
    if mid:
        seen_ids.add(mid)
    cid = x.get('chat_id', '')
    msg_records.append({
        '会话ID': cid,
        '会话名称': cname(cid),
        '会话类型': ctype(cid),
        '消息ID': mid,
        '消息类型': x.get('msg_type', '') or '',
        '话题ID': x.get('thread_id', '') or '',
        '发送人': (x.get('sender') or {}).get('name', '') or '',
        '发送人ID': (x.get('sender') or {}).get('id', '') or '',
        '消息内容': clip(x.get('content', '')),
        '发送时间': iso(x.get('create_time', '')),
    })

msg_records.sort(key=lambda r: r['发送时间'])
json.dump({'create_records': msg_records}, open('/tmp/msg_records.json', 'w'), ensure_ascii=False)
print('msg_records:', len(msg_records))

D = '2026-10-25T'
QA = []

def qa(question, answer, asker, replier, time_hm, qtype, ai='', text=''):
    QA.append({
        'Question': question,
        'Answer': answer,
        '提问人': asker,
        '回复人': replier,
        '问题日期': D + time_hm + ':00+08:00',
        '问题类型': qtype,
        'AI回复': ai,
        '文本': clip(text),
    })

root_by_idx = roots

def rtext(i):
    return roots[i].get('content', '')

qa(
 '我的任务进行了一半，快完成了，消耗了几千个积分，突然被中断显示「模型请求失败」，切换模型也不行，怎么办？能不能把积分退回来？',
 'TRAE 宝回复：3003「模型请求失败」是模型服务侧的临时性失败，建议稍后重试或新开任务重试，不要在任务中途反复切换模型（会使缓存失效、更耗积分）；积分退还属个人账号个例，需邮件联系 feedback@mail.trae.cn，附上产品与版本（TraeWork CN 3.4.7）、报错原文、发生时间及报错框「复制请求信息」的内容以便定位。',
 '黄璜', 'TRAE 宝', '03:02', '运维问题', '', rtext(3))

qa(
 '这个优惠券到月底就到期了吗？只能升级使用吗？（附截图：¥10 优惠券·连续包月会员）',
 'TRAE 宝回复：从截图确认几张「¥10 优惠券·连续包月会员」到期时间为 2026/10/31 23:59，即 10 月底到期；关于适用范围（是否仅限升级使用）官方资料无直接说明，无法确认，建议带下单页截图与账号信息邮件联系 feedback@mail.trae.cn 核实，也可在付款页勾选/取消优惠券观察结算金额变化来判断。',
 '用户257712', 'TRAE 宝', '08:49', '流程咨询', '', rtext(4))

qa(
 '如果做医学相关的内容，是不是一定要谨慎为主？',
 'TRAE 宝回复：认同该提醒。用 TRAE 处理医学相关内容时，AI 输出只能作为辅助参考，最终结论和准确性需要由专业人士复核。',
 '哈基宸', 'TRAE 宝', '09:12', '工作沟通', '', rtext(5))

qa(
 '【分享飞书 wiki 文档链接】https://lcnziv86vkx6.feishu.cn/wiki/Sae6wjbFti6yyok3gfecVBSWnqe',
 'TRAE 宝回复：收到分享的文档，但飞书 wiki 链接无法直接打开查看内容，请说明希望协助的具体问题（涉及 TRAE Work / IDE / 插件及现象）再跟进。',
 '哈基宸', 'TRAE 宝', '09:45', '工作沟通', '', rtext(6))

qa(
 '【分享 TRAE.ai 公众号文章：10 月插件热榜】https://mp.weixin.qq.com/s/pqttA3pv-tQ8KUYDedFajA',
 'TRAE 宝回复：确认这是 TRAE.ai 公众号 10 月插件热榜推文，如需了解榜单中某个插件的用法、安装方式或 Conf 功能点可继续提问。群友小当家、漫川、杜昔月、哈基宸在话题内就群吉祥物「哈吉米」改名「小菠」等进行了闲聊互动。',
 '哈基宸', 'TRAE 宝', '11:08', '工作沟通', '', rtext(7))

qa(
 '叮咚～签到小提醒来咯！今日100积分等你领，动动手指就到手，愿你把周日的悠闲进行到底！🌼（由豆包发送）',
 'TRAE 宝回复：收到啦～积分提醒已看到，周日愉快 🌼 有 TRAE 相关的问题随时喊我。',
 '吴于飞', 'TRAE 宝', '12:28', '工作沟通', '', rtext(0))

qa(
 '叮咚～签到小提醒来咯！今日100积分等你领，动动手指就到手，愿你把周日的悠闲进行到底！🌼（由豆包发送）',
 'TRAE 宝回复：收到啦，周日愉快～有 TRAE 相关的问题随时找我。',
 '吴于飞', 'TRAE 宝', '12:28', '工作沟通', '', rtext(8))

qa(
 '怎么查一个付费是哪个账号啊？我都取消自动订阅了，为什么还是会扣款？有没有电话等更快捷的联系方式？',
 'TRAE 宝回复：属个人账号订单与扣款问题，无法直接查询，建议邮件联系 feedback@mail.trae.cn（国内版）/ feedback@mail.trae.ai（国际版），说明扣款时间、金额和支付方式以定位订单。群友用户030912 人工回复：退费需要发邮件（工作留痕）；只要不再使用，把自动续费关闭即可避免后续扣款。',
 '陈昭', '用户030912', '14:02', '流程咨询', '', rtext(9))

qa(
 '【分享抖音视频】用AI，让经典活起来 https://v.douyin.com/U00BNlYivto',
 'TRAE 宝回复：收到分享，「用AI，让经典活起来」方向有意思，后续想聊如何用 TRAE 做类似内容创作或工具可随时提出。',
 '哈基宸', 'TRAE 宝', '19:37', '工作沟通', '', rtext(10))

qa(
 '在新版的 TRAE 里，怎么用 Work 模式？',
 'TRAE 宝回复：新版 Work 模式属于独立产品 TRAE Work（提供网页/桌面/移动版，内置 Work 与 Code 双模式）：打开后在左上角模式切换处选择 Work，在「Work with TRAE」输入区直接描述任务，可使用网页读取、调研分析、数据挖掘、文件管理等内置模板；网页版入口 https://work.trae.cn/。群友哈基宸、漫川建议用 Agent 模式/右上角 agent，提问人反馈当前 agent 模式默认即 code。',
 '用户924813', '哈基宸', '19:39', '工具使用', '', rtext(11))

ai_ans_3025 = '目前 TRAE 移动端 App 暂不支持在对话中直接上传本地文件，该诉求已在群内 @高旋 反馈给产品负责人。短期替代方案：1) 在手机浏览器使用网页版 work.trae.cn，网页端支持上传文件，可临时处理居家办公的紧急文件任务；2) 先将文件同步至云文档/云盘，在对话中以链接形式引用；3) 建议将正式功能诉求发布到 TRAE 社区论坛产品建议板块（https://forum.trae.cn/c/8-category/8）并附上使用场景，便于官方评估排期。'
qa(
 '希望 Trae 移动端可以上传文件，我在家办公呢（附移动端「添加到对话」界面截图，@高旋）',
 ai_ans_3025,
 '电商用户3025', 'AI助手', '20:29', '产品需求', ai_ans_3025, rtext(12))

qa(
 '【分享社区论坛文章：用Trae也能快速搞定动作迁移人物替换？积累提示词！】https://forum.trae.cn/t/topic/410932 CC@曹翔 他偷偷摸摸交出焚诀了！！不枉大家鞭挞这么久（没有的事，我们很友好催更）',
 'TRAE 宝回复：收到～动作迁移+人物替换这套提示词挺实用，期待经验贴；建议同步发到 TRAE 社区论坛技巧分享板块分享给更多人。曹翔以表情包回应。',
 '冯梦龙', 'TRAE 宝', '21:40', '工作沟通', '', rtext(13))

ai_ans_307498 = '建议先别急着换工具，可按以下步骤定位：1) 整理该 bug 的原始提示词、所用模型版本与失败环节，在 TRAE 中新开任务重试，排除上下文过长或缓存干扰；2) 将 bug 描述、复现步骤及报错框「复制请求信息」内容发送至 feedback@mail.trae.cn，或在社区论坛帮助与支持板块（https://forum.trae.cn/c/7-category/7）发帖，便于官方判断是配置、用法还是产品问题；3) 也可在群里补充具体 bug 细节（报错原文/截图），群友可协助对比分析。'
qa(
 '天塌了，同样的 bug、同样的模型，dsh 解决了，TRAE 没解决，我要转 dsh 了，有点舍不得 TRAE。',
 ai_ans_307498,
 '用户307498', 'AI助手', '22:17', '开发问题', ai_ans_307498, rtext(14))

ai_ans_0409 = '该问题为 GenerateImage MCP 工具当前未暴露 image_paths（图生图）参数，导致 solo-image-edit 技能流程 blocked，TRAE 宝亦确认未查到官方支持说明。建议：1) 短期改用其他支持图生图的图像处理工具或第三方 MCP 作为替代链路；2) 将该场景发布到社区论坛产品建议板块（https://forum.trae.cn/c/8-category/8），请求为 GenerateImage 暴露 image_paths 参数；3) 群内已 @高旋，建议后续在话题中跟进官方确认是否排期支持。'
qa(
 'GenerateImage MCP 工具没有暴露 image_paths 参数，导致图生图走不通，solo-image-edit 技能因此停在 blocked（附截图，@高旋 @TRAE 宝）',
 ai_ans_0409,
 '飞书用户0409KK', 'AI助手', '22:48', '产品需求', ai_ans_0409, rtext(15))

qa(
 '各位晚安[天色已晚]',
 '群友用户456741 回复「晚安哈吉宸」；TRAE 宝回复：晚安～有 TRAE 相关的问题随时来找我，明天见 🌙',
 '哈基宸', '用户456741', '23:00', '工作沟通', '', rtext(16))

qa(
 '工作树是怎么用呀？（附 TRAE Work 界面截图）',
 'TRAE 宝回复：工作树（Worktree）是 TRAE Work 基于 Git 原生机制的功能，让同一项目的多个任务在相互隔离的 Git 环境（专属目录、依赖、分支）中执行，适合并行开发新功能、同时修紧急 bug；前置条件为任务在本地环境运行且已安装 Git。用法：发起任务前在对话输入框左下角将模式设为「工作树」，任务启动后自动创建专属分支与目录；编码完成后在顶部工作树分支栏点按钮走 AI 自动合并，或点「···」选择手动合并（冲突需先解决）。',
 '用户852152', 'TRAE 宝', '23:16', '工具使用', '', rtext(17))

img030912 = '【发送积分签到入口截图】'
qa(
 img030912,
 'TRAE 宝回复：这张截图是积分签到的入口，询问是想了解加入会员后每日积分的领取规则，还是签到本身遇到了问题，请说明具体想问的点。',
 '用户030912', 'TRAE 宝', '00:00', '工作沟通', '', rtext(1))

for r in QA:
    for f in ['Question', 'Answer', '提问人', '回复人', '问题类型', '问题日期']:
        assert r.get(f), 'EMPTY FIELD: ' + f

json.dump({'create_records': QA}, open('/tmp/qa_records.json', 'w'), ensure_ascii=False)
print('qa_records:', len(QA))
from collections import Counter
print('types:', Counter(r['问题类型'] for r in QA))
print('askers:', Counter(r['提问人'] for r in QA))
print('repliers:', Counter(r['回复人'] for r in QA))
