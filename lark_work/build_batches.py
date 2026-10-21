#!/usr/bin/env python3
"""Build batch payloads for the 消息记录 table and a human-readable transcript."""
import json, os, collections

WORK = "/workspace/lark_work"
BATCH = os.path.join(WORK, "batches_msg")
os.makedirs(BATCH, exist_ok=True)
for f in os.listdir(BATCH):
    os.remove(os.path.join(BATCH, f))

rows = [json.loads(l) for l in open(os.path.join(WORK, "messages_kept.ndjson"), encoding="utf-8")]

FIELDS = ["会话ID", "会话名称", "会话类型", "消息ID", "消息类型", "话题ID",
          "发送人", "发送人ID", "消息内容", "发送时间"]

records = []
for r in rows:
    t = r["发送时间"].strip()          # "2026-10-21 09:10"
    dt = t.replace(" ", "T") + ":00+08:00"
    rec = {k: r[k] for k in FIELDS}
    rec["发送时间"] = dt
    records.append(rec)

SIZE = 50
n = 0
for i in range(0, len(records), SIZE):
    chunk = records[i:i + SIZE]
    n += 1
    p = os.path.join(BATCH, "msg_batch_%02d.json" % n)
    json.dump({"create_records": chunk}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
print("total records:", len(records), "batches:", n)

# readable transcript grouped by chat
bychat = collections.OrderedDict()
for r in rows:
    key = (r["会话ID"], r["会话名称"], r["会话类型"])
    bychot = bychat.setdefault(key, [])
    bychot.append(r)

with open(os.path.join(WORK, "transcript.txt"), "w", encoding="utf-8") as f:
    for (cid, name, ctype), msgs in sorted(bychat.items(), key=lambda kv: -len(kv[1])):
        f.write("\n" + "=" * 90 + "\n")
        f.write("会话: %s | 类型: %s | chat_id: %s | 消息数: %d\n" % (name, ctype, cid, len(msgs)))
        f.write("=" * 90 + "\n")
        for m in msgs:
            th = (" [thread:%s]" % m["话题ID"]) if m["话题ID"] else ""
            content = m["消息内容"].replace("\n", "\n      ")
            f.write("[%s] %s (%s)%s: %s\n" % (m["发送时间"], m["发送人"], m["消息类型"], th, content))
print("transcript written")
