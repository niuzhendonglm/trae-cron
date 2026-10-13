import json, collections

TARGET = "2026-10-12"

v = json.load(open("valid.json"))
v = [m for m in v if (m.get("create_time") or "").startswith(TARGET)]
print("strict 2026-10-12 valid msgs:", len(v))

chats = json.load(open("chats_all.json"))["data"]["chats"]
cmap = {}
for c in chats:
    cmap[c["chat_id"]] = (c.get("name") or "", c.get("chat_mode") or "")

def to_iso(ct):
    # "2026-10-12 08:14" -> "2026-10-12T08:14:00+08:00"
    d, t = ct.split(" ")
    if len(t) == 5:
        t = t + ":00"
    return f"{d}T{t}+08:00"

records = []
for m in v:
    cid = m.get("chat_id") or m.get("_chat_id")
    name, mode = cmap.get(cid, ("", ""))
    sender = m.get("sender") or {}
    content = m.get("content") or ""
    rec = {
        "会话ID": cid or "",
        "会话名称": name,
        "会话类型": mode,
        "消息ID": m.get("message_id") or "",
        "消息类型": m.get("msg_type") or "",
        "话题ID": m.get("thread_id") or "",
        "发送人": sender.get("name") or "",
        "发送人ID": sender.get("id") or "",
        "消息内容": content,
        "发送时间": to_iso(m.get("create_time") or ""),
    }
    records.append(rec)

print("records built:", len(records))
print("chat_mode dist:", collections.Counter(r["会话类型"] for r in records))
print("msg_type dist:", collections.Counter(r["消息类型"] for r in records))

json.dump(records, open("raw_records.json", "w"), ensure_ascii=False, indent=1)

# also save strict valid for QA step
json.dump(v, open("valid_strict.json", "w"), ensure_ascii=False)
print("saved raw_records.json, valid_strict.json")
