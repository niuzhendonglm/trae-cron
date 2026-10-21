#!/usr/bin/env python3
"""Aggregate per-chat raw message dumps into one NDJSON of yesterday's real-user messages."""
import json, os, glob, collections, sys
from datetime import datetime, timedelta

WORK = "/workspace/lark_work"
RAW = os.path.join(WORK, "msgs_raw")
WIN_LO = "2026-10-20 16:00"
WIN_HI = "2026-10-21 15:59"

def to_beijing(ct):
    return (datetime.strptime(ct, "%Y-%m-%d %H:%M") + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

meta = json.load(open(os.path.join(WORK, "chat_meta.json"), encoding="utf-8"))

BOT_NAME_HINTS = ("智能助手", "机器人", "助手", "Bot", "bot", "通知", "小助手")

stats = collections.Counter()
kept = []
sender_kinds = collections.Counter()
msg_types = collections.Counter()

for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
    cid = os.path.basename(path)[:-5]
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        stats["parse_error"] += 1
        continue
    if not d.get("ok"):
        stats["not_ok"] += 1
        continue
    msgs = (d.get("data") or {}).get("messages") or []
    if not msgs:
        stats["empty_chat"] += 1
        continue
    stats["chat_with_msgs"] += 1
    m = meta.get(cid, {})
    cname = m.get("name") or ""
    cmode = m.get("mode") or ""
    ctype = "群聊" if cmode == "group" else ("单聊" if cmode == "p2p" else (cmode or "未知"))
    for msg in msgs:
        ct = (msg.get("create_time") or "").strip()
        if not (WIN_LO <= ct <= WIN_HI):
            stats["out_of_range"] += 1
            continue
        ct_bj = to_beijing(ct)
        mt = msg.get("msg_type") or ""
        msg_types[mt] += 1
        if mt == "system":
            stats["drop_system"] += 1
            continue
        if msg.get("deleted"):
            stats["drop_deleted"] += 1
            continue
        snd = msg.get("sender") or {}
        stype = snd.get("sender_type") or ""
        sid = snd.get("id") or ""
        sname = snd.get("name") or ""
        sender_kinds[stype or "(none)"] += 1
        if stype != "user":
            stats["drop_non_user_sender"] += 1
            continue
        if not sname and not sid.startswith("ou_"):
            stats["drop_no_sender"] += 1
            continue
        content = msg.get("content")
        if content is None:
            content = ""
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        kept.append({
            "会话ID": cid,
            "会话名称": cname,
            "会话类型": ctype,
            "消息ID": msg.get("message_id") or "",
            "消息类型": mt,
            "话题ID": msg.get("thread_id") or "",
            "发送人": sname or sid,
            "发送人ID": sid,
            "消息内容": content,
            "发送时间": ct_bj,
            "_create_time_utc": ct,
            "_sender_type": stype,
            "_position": msg.get("message_position") or "",
        })

kept.sort(key=lambda r: (r["会话ID"], r["发送时间"], r["_position"]))
with open(os.path.join(WORK, "messages_kept.ndjson"), "w", encoding="utf-8") as f:
    for r in kept:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("=== stats ===")
for k, v in stats.most_common():
    print(f"  {k}: {v}")
print("=== msg_type dist (in-range) ===")
for k, v in msg_types.most_common():
    print(f"  {k}: {v}")
print("=== sender_type dist (in-range) ===")
for k, v in sender_kinds.most_common():
    print(f"  {k}: {v}")
print("=== kept:", len(kept), "===")
bychat = collections.Counter((r["会话ID"], r["会话名称"], r["会话类型"]) for r in kept)
print("=== chats with kept msgs:", len(bychat), "===")
for (cid, nm, tp), n in bychat.most_common():
    print(f"  [{tp}] {nm} ({cid}) -> {n}")
