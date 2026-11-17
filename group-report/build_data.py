import json, glob, re

chats = {c["chat_id"]: c for c in json.load(open("./chats.json"))["data"]["chats"]}
msgs = {}
for f in glob.glob("./raw_msgs/*.json"):
    for m in json.load(open(f))["data"].get("messages") or []:
        msgs[m["message_id"]] = m

def flat(content):
    if content is None:
        return ""
    s = str(content)
    try:
        o = json.loads(s)
    except Exception:
        return s
    if isinstance(o, dict):
        if isinstance(o.get("text"), str):
            return o["text"]
        if isinstance(o.get("content"), list):
            lines = []
            if o.get("title"):
                lines.append(o["title"])
            for para in o["content"]:
                for el in para:
                    if el.get("tag") == "text":
                        lines.append(el.get("text", ""))
                    elif el.get("tag") == "a":
                        lines.append(el.get("text", "") + " " + el.get("href", ""))
            return "\n".join(lines)
    return s

def sanitize(t):
    t = re.sub(r"<at[^>]*>\s*</at>", "", t or "")
    t = re.sub(r"!\[Image\]\([^)]*\)\s*", "", t)
    return t.strip()


def iso(t):
    # t like 2026-11-16 11:08
    if len(t) == 16:
        t += ":00"
    return t.replace(" ", "T") + "+08:00"

# ---------- raw messages (real user text/post, exclude self-generated report) ----------
EXCLUDE = {"om_x100b609c59f078a4b05f9f130b65b2c"}
msg_records = []
for mid, m in msgs.items():
    s = m.get("sender") or {}
    if s.get("sender_type") != "user" or m.get("msg_type") not in ("text", "post"):
        continue
    if mid in EXCLUDE:
        continue
    c = chats.get(m["chat_id"], {})
    txt = flat(m.get("content"))
    txt = sanitize(txt)
    if not txt.strip():
        continue
    msg_records.append({
        "会话ID": m["chat_id"],
        "会话名称": c.get("name", ""),
        "会话类型": c.get("chat_mode", ""),
        "消息ID": mid,
        "消息类型": m.get("msg_type", ""),
        "话题ID": m.get("thread_id") or "",
        "发送人": s.get("name", ""),
        "发送人ID": s.get("id", ""),
        "消息内容": txt[:2000],
        "发送时间": iso(m.get("create_time", "")),
    })
msg_records.sort(key=lambda r: r["发送时间"])
json.dump(msg_records, open("./tmp/msg_records.json", "w"), ensure_ascii=False, indent=1)
print("msg_records", len(msg_records))

# ---------- QA ----------
# (message_id, 问题类型, 回复人, answer, is_ai, pending)
AI = "AI助手"
QA_DEFS = [
 ("om_x100b6093728fc4b0c0a3ff4dd50d521", "运维问题", "高旋", "官方确认部分用户出现“系统未知错误，请稍后重试”（错误码 4000104/4000103）；11:29 公告正在修复，11:52 已恢复，请重试。", False, False),
 ("om_x100b6093244a54b4c30b1c2afc31b0e", "运维问题", "李云鹏", "自有模型同样报错，属于平台侧故障，与模型来源无关；服务已于 11:52 恢复。", False, False),
 ("om_x100b6093382db4a0c4e4eec91dc5375", "运维问题", "高旋", "4000103 和 4000104 都是本次服务异常产生的系统未知错误码，只是触发路径不同，统一修复，11:52 已恢复。", False, False),
 ("om_x100b609337bee4accfe705aec615d6e", "运维问题", "高旋", "11:29 官方公告正在修复，11:52 已恢复，请刷新后重试。", False, False),
 ("om_x100b6093667b5440ce43be4b453846c", "运维问题", "吴于飞", "官方 11:08 公告服务异常正在处理；高旋 11:29 说明 4000104/4000103 修复中，11:52 已恢复。", False, False),
 ("om_x100b60935dc0e0accfd7926de5499d4", "运维问题", "高旋", "并非 DeepSeek 单独不可用，是平台侧 4000104/4000103 服务异常；11:52 已恢复。", False, False),
 ("om_x100b60919513a4a4cfd3225022bb526", "工具使用", AI,
  "企业旗舰账号的“Trae 移动端”设置项由租户管理员在管理后台统一策略控制，个人账号与企业账号并不同步。建议：1）将客户端升级到最新版并重新登录；2）让租户管理员在管理后台“企业设置-功能开关”中确认移动端能力已开启；3）同企业其他同事可见说明是分批灰度，可提交工单附账号、租户 ID 和截图核对灰度名单。", True, False),
 ("om_x100b6092848990b0dd171f30775ee9b", "工具使用", AI,
  "目前 Trae CN 仅支持平台内置模型，不支持指定自定义模型或自建模型接入；模型调用按积分/额度计费，不能绕过积分。企业如有个性化模型需求，可走企业版/客户成功渠道提交评估。", True, False),
 ("om_x100b609c2f959ca0de16bee62b3c136", "产品需求", AI,
  "Trae 面向开发者，核心是 Agent 编程（读仓库、改代码、跑命令）；豆包面向通用对话与办公创作。两者产品定位和账号体系独立，入口与用量规则因此不统一，按任务类型选型即可。", True, False),
 ("om_x100b609df0da68b0cf3021f4bca37cb", "工具使用", AI,
  "模型直接复制旧 SDK 通常是指令范围不清或上下文过大。建议：1）在提示中明确“禁止复制现有文件，逐文件对比差异后重写”；2）指定目标目录与参考文件清单，分模块生成；3）用 Diff 视图核对每个文件。若确认模型未按要求执行并产生异常扣费，可在客户端“帮助-反馈”提交会话 ID 与积分流水申请核查/返还。", True, False),
 ("om_x100b609f7c332484cea208bc6ed5a52", "工具使用", AI,
  "会话记录消失一般有三类原因：客户端升级后本地缓存目录变更、切换了登录账号/租户、或本地数据被清理。可先在设置中核对账号与租户，再检查本地 ~/.trae 缓存目录是否存在，重要会话及时导出；仍无法恢复可提交日志给官方排查。", True, False),
 ("om_x100b609fbee1bca0b37a276d85ffd89", "开发问题", AI,
  "Agent→IDE 切换时开两个窗口，通常是切换过程重复拉起窗口进程。建议先完全退出 Trae（任务管理器结束所有 Trae 进程）再重开，并升级到 3.4.20 后复测；若仍复现，提交版本号与复现步骤给官方。", True, False),
 ("om_x100b6098777a9cb8b0722766dbd5684", "产品需求", AI,
  "WPS 直连目前不在已发布能力内，Trae 通过浏览器或本地文件方式处理表格。短期可把表格另存为 xlsx 后用本地文件方式处理；该需求可提交官方需求池，按版本规划评估。", True, False),
 ("om_x100b60981653ecb4c483dad41766e6d", "运维问题", AI,
  "拖入数据表格后 WPS 死机，多为大表格解析占用内存或 WPS 与 Electron 剪贴板冲突。建议：1）升级 WPS 与 Trae 到最新版；2）表格先精简行数或另存 xlsx 再拖入；3）关闭 WPS 云同步后复测；4）抓取两边日志提交工单。", True, False),
 ("om_x100b60983a9548a8df7fc958b660795", "流程咨询", AI,
  "积分按模型调用的 token 消耗折算，不同模型单价不同，没有固定的“1 积分=N token”。可在“设置-用量/积分明细”查看每次调用的模型与消耗；估算时用当次请求的输入+输出 token 乘对应模型倍率。", True, False),
 ("om_x100b60992e775ca4ce74c03cc51320d", "工具使用", AI,
  "Trae CLI 目前未在公开版本上线，官方尚未发布正式 CLI 安装包，可关注官方公告。现阶段可用 IDE/Agent 模式配合终端命令完成同类工作。", True, False),
 ("om_x100b609161836ca4de32dcff94675b4", "运维问题", "顾洪杰", "先关闭 InoClaw、等待后重新打开即可恢复登录；已安排跟踪日志定位根因。", False, False),
 ("om_x100b609314a7c8b0ce34a176d9aa747", "运维问题", "李炎杰", "请求中包含敏感信息、涉及敏感词，被安全护栏拦截导致任务中断；移除敏感内容后重试即可。", False, False),
 ("om_x100b609fbd4b88acb3c7ab2b7e8ee06", "运维问题", AI,
  "飞书无响应可先确认网络与飞书客户端版本，退出重进或切换网络复测；若仅 InoAI 机器人无响应，可能是后端服务或长连接断开，建议 @管理员 并提供发生时间与截图便于查日志。", True, False),
 ("om_x100b6098c7fa98a4b4980d94672fff1", "工具使用", "单呈祥", "先检查系统默认浏览器设置，确认域账号登录链接在默认浏览器中打开；仍无法跳转可反馈客户端日志。", False, False),
 ("om_x100b609a33cb2ca4b4a6edf26ade35a", "流程咨询", AI,
  "InoClaw 机器人默认可邀请进群，但需群主或管理员操作，且机器人要在应用可用范围内；部门群涉及数据权限，建议先确认群成员可见范围，再由管理员添加。", True, False),
 ("om_x100b609ac0f604acb490ef688ed8ea2", "流程咨询", AI,
  "飞书机器人权限（可见范围、进群、消息读取）由应用管理员在飞书开放平台“权限管理”中申请，并由企业管理员审批；具体审批人可在开放平台应用权限页查看。", True, False),
 ("om_x100b609ee5638480c1dca3903d5d725", "运维问题", "杜彦永", "字段超长导致任务积压，杜彦永已接手处理。", False, False),
 ("om_x100b609eb75144a4c33e4da57a802ac", "运维问题", "武销南", "着急可先重建；本次需发版修复前端回写问题。无需重建，重新取消并连接字段映射即可触发前端保存变更。", False, False),
 ("om_x100b609817df38a8de382bba6a5d45b", "运维问题", "武销南", "在字段映射处取消原连线再重新连接；因为建表语句是手动在查询模块改的，抽取任务可能识别不到。", False, False),
 ("om_x100b609a1956fca0dc026e49713a01d", "运维问题", AI,
  "任务下游依赖可在 DaaS 任务编排的“依赖关系/血缘”视图查看：打开任务详情→依赖管理，分别看上游触发与下游订阅；若列表为空但仍有堵塞，检查是否被调度分组或同表单任务隐式依赖，必要时用任务 ID 在元数据表查询依赖记录。", True, False),
 ("om_x100b60924f76a534c0c4d2f8a6d371b", "开发问题", AI,
  "导出字段与页面展示不一致，常见原因是导出使用默认视图/全字段模板，而页面展示的是当前视图（含隐藏列、计算字段、格式化）。建议核对导出模板是否与当前视图一致；计算字段、关联字段导出时可能取原始值。若仍不一致，提供模型 ID、视图与导出文件给 DaaS 支持排查。", True, False),
 ("om_x100b60926d38e8b8cf66a96328b51e9", "运维问题", "穆潇", "陈工已帮我们配置好，正常调度即可；穆潇在 D 区忙完后继续处理剩余部分。", False, False),
 ("om_x100b609e7c5db4a8de9dc3d18dc11d7", "运维问题", "穆潇", "dws 表接口可以一起配置，明天弄完；新链接发牛振东找他协调 IT 授权。", False, True),
 ("om_x100b609ff7b624acc0e64ba5217e07d", "运维问题", "穆潇", "明天（11-17）弄完，明天没有其他事情。", False, True),
 ("om_x100b6098317008acdf7264e1c1c8d87", "运维问题", AI,
  "按当前排期，除在岗履历表（预计 18 号开发完成）外，其余表接口计划明天（11-17）提供；建议明天上午与穆潇确认接口清单和授权链接，避免遗漏 dws 表。", True, False),
 ("om_x100b6092491ccca0cfef11eb559785a", "工作沟通", "李家伟", "这周会更新一版报告。", False, False),
 ("om_x100b6092364c80a8b4bb5ce06d6c416", "运维问题", "李岳林", "周末产线双休，14 号早上 8:30 后断电，今天早上才上电，恢复供电后数据即可恢复。", False, False),
 ("om_x100b609286b51ca8de69a2462c5d857", "运维问题", "李岳林", "固定密码 111111，设备 ID：1970603759。", False, False),
 ("om_x100b609edb1968b8ddb46fe3ce09f8e", "开发问题", AI,
  "可视化建模运行结果与输出数据集不一致，先排查：1）运行后是否点击“写入输出数据集”并等任务完成；2）是否存在增量/覆盖模式差异；3）输出数据集是否被下游任务覆盖。建议保留运行实例 ID、输入输出行数截图，提交火山引擎售后按实例日志定位。", True, False),
 ("om_x100b60981e961ca0dfc8be72f5e4b97", "产品需求", AI,
  "透视表暂不支持一键隐藏空值/0 维度，可先在数据源用筛选器过滤空值与 0，或在计算字段中将 0 转为空再聚合；也可向售后提交“隐藏空值维度”需求评估。", True, False),
 ("om_x100b60931163e5b4df01c32a6300c8e", "开发问题", "牛振东", "上周五已变更完成、QA 验证通过；复测轮播到网页组件标签页不再请求两次，但轮播仍会预请求相邻标签页，已请代威确认是否平台特性。", False, True),
 ("om_x100b6091c0ce54a0c1cbab91d843804", "开发问题", "商轩赫", "NG 标签设为 bool 型、SN 设为 string 型，在符号配置中勾选并重新编译下载；参照武山湖配置，远程读取验证，11:16 已可读。", False, False),
 ("om_x100b60929b1c4ca4c06021f446373cb", "开发问题", "商轩赫", "勾选编译后仍读不到，需参照武山湖统一符号配置；商轩赫远程方山湖读取，11:16 已可读，军山湖仿照此模式重做。", False, False),
 ("om_x100b6091b458c0a0c4f16241ae84b4a", "工作沟通", "马芳", "近期项目比较忙，预计 12 月中；最晚 12 月 20 日两边系统要完成调试。", False, True),
 ("om_x100b60937f9748a8c4f3245573c3f14", "工作沟通", "何荣福", "review 前先和金工对齐思路，明天下午的会已加上金工。", False, False),
 ("om_x100b6091d459eca8df7cca58f408998", "工作沟通", "何洁", "周五何老师和聪哥不行，何老师周三开始出差，所以只能安排周一。", False, False),
 ("om_x100b60936e3b5cb4cfdba5ffcc3c578", "流程咨询", "牛振东", "群仍在、权限未取消，确认是消息未推送，已核对。", False, False),
 ("om_x100b609f94e370a0b09f090ec644e06", "工作沟通", "方智", "今天要忙领导演示汇报，明后天开好测试账号并讲解。", False, True),
 ("om_x100b609d811f40a0c1f9d904f07c7c8", "工作沟通", "牛振东", "先等对方介绍方案，再基于材料让 AI 出 PRD 和代码；目前缺工具和方向，需要摸索。", False, True),
 ("om_x100b609213f718accd101cefe1b0961", "运维问题", "陈秀迪", "11 月 16 日共提交 23 台上电前自检通报（青岛科钛、罗斯达、温州赢合等），陈秀迪对已上电批次照片标签逐批确认无误，全天测试按流程推进。", False, False),
 ("om_x100b609268cabc88dde724d39a0b0d1", "产品需求", AI,
  "建议将提示文案统一为：“由于拍摄角度或光线等原因，未识别出相关机柜标签或线缆标签，请调整拍摄位置后重试”；文案在前端配置中集中维护，便于后续统一调整。", True, False),
 ("om_x100b6092dfdf84a0b37460c5e9bf6d1", "运维问题", AI,
  "建议今天先拉取恢复润滑后的振动、温度等关键测点数据，与润滑失效前基线对比，确认异常特征是否消失；同时保留润滑失效时段样本用于模型回归，验证告警准确性。", True, False),
]

qa_records = []
for mid, typ, replier, answer, is_ai, pending in QA_DEFS:
    m = msgs[mid]
    s = m.get("sender") or {}
    q = flat(m.get("content")).strip()
    # strip leading images / mentions
    q = sanitize(q)
    q = q.strip() or flat(m.get("content")).strip()
    rec = {
        "Question": q[:1000],
        "Answer": answer,
        "提问人": s.get("name", ""),
        "回复人": replier,
        "问题日期": iso(m.get("create_time", "")),
        "问题类型": typ,
        "AI回复": answer if is_ai else "",
        "文本": sanitize(flat(m.get("content")))[:1000],
    }
    assert all(rec[k] for k in ["Question", "Answer", "提问人", "回复人", "问题类型", "问题日期"])
    qa_records.append(rec)
json.dump(qa_records, open("./tmp/qa_records.json", "w"), ensure_ascii=False, indent=1)
print("qa_records", len(qa_records), "ai", sum(1 for r in qa_records if r["AI回复"]))
from collections import Counter
print(Counter(r["问题类型"] for r in qa_records))
print(Counter(r["提问人"] for r in qa_records).most_common())
print(Counter(r["回复人"] for r in qa_records).most_common())
# save pending flags for report
json.dump([{"q": r["Question"], "p": p} for r, (_, _, _, _, _, p) in zip(qa_records, QA_DEFS)], open("./tmp/pending.json", "w"), ensure_ascii=False, indent=1)