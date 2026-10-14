import json, glob, os, re
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET_DATE = "2026-10-14"
CN = timezone(timedelta(hours=8))

chats = json.load(open(os.path.join(BASE, "chats_map.json")))["chats"]

def parse_ct(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    m = re.match(r"^(\d{13})$", s)
    if m:
        return datetime.fromtimestamp(int(s) / 1000, tz=timezone.utc)
    return None

NOISE_CONTENT = re.compile(r"^\s*(\[Invalid (text|image) JSON\]|\[nonsupport\])\s*$")

records = []
stats = {"total": 0, "system": 0, "app": 0, "deleted": 0, "out_of_range": 0, "noise": 0, "kept": 0}
skipped_files = []

for path in sorted(glob.glob(os.path.join(BASE, "raw", "*.json"))):
    try:
        d = json.load(open(path))
    except Exception:
        skipped_files.append(path)
        continue
    if not d.get("ok"):
        skipped_files.append(path)
        continue
    msgs = (d.get("data") or {}).get("messages") or []
    for m in msgs:
        stats["total"] += 1
        mt = m.get("msg_type") or ""
        snd = m.get("sender") or {}
        stype = (snd.get("sender_type") or "").lower()
        if m.get("deleted"):
            stats["deleted"] += 1
            continue
        if mt == "system":
            stats["system"] += 1
            continue
        if stype != "user":
            stats["app"] += 1
            continue
        content = (m.get("content") or "").strip()
        if not content or NOISE_CONTENT.match(content):
            stats["noise"] += 1
            continue
        dt = parse_ct(m.get("create_time"))
        if dt is None:
            stats["noise"] += 1
            continue
        dt_cn = dt.astimezone(CN)
        if dt_cn.strftime("%Y-%m-%d") != TARGET_DATE:
            stats["out_of_range"] += 1
            continue
        cid = m.get("chat_id") or os.path.basename(path)[:-5]
        chat = chats.get(cid, {})
        mode = chat.get("chat_mode") or ""
        ctype = "群聊" if mode == "group" else ("单聊" if mode == "p2p" else (mode or "未知"))
        records.append({
            "fields": {
                "会话ID": cid,
                "会话名称": chat.get("name") or "",
                "会话类型": ctype,
                "消息ID": m.get("message_id") or "",
                "消息类型": mt,
                "话题ID": m.get("thread_id") or "",
                "发送人": snd.get("name") or "",
                "发送人ID": snd.get("id") or "",
                "消息内容": content[:2000],
                "发送时间": dt_cn.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            },
            "_sort": (dt_cn.strftime("%Y-%m-%dT%H:%M:%S"), cid, int(m.get("message_position") or 0)),
        })
        stats["kept"] += 1

records.sort(key=lambda r: r["_sort"])
for r in records:
    r.pop("_sort", None)

with open(os.path.join(BASE, "msg_records.ndjson"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

json.dump(stats, open(os.path.join(BASE, "msg_stats.json"), "w"), ensure_ascii=False, indent=2)
print(json.dumps(stats, ensure_ascii=False, indent=2))
print("skipped files:", len(skipped_files))
chats_kept = sorted({r["fields"]["会话ID"] for r in records})
print("active chats kept:", len(chats_kept))
by_type = {}
for r in records:
    by_type[r["fields"]["消息类型"]] = by_type.get(r["fields"]["消息类型"], 0) + 1
print("by msg_type:", json.dumps(by_type, ensure_ascii=False))
by_sender = {}
for r in records:
    by_sender[r["fields"]["发送人"]] = by_sender.get(r["fields"]["发送人"], 0) + 1
top = sorted(by_sender.items(), key=lambda x: -x[1])[:20]
print("top senders:", json.dumps(top, ensure_ascii=False))
