#!/usr/bin/env python3
"""Build fix payloads: batch-update wrong 发送时间 (+8h) and create missing morning records."""
import json, os, collections

WORK = "/workspace/lark_work"
FIX = os.path.join(WORK, "batches_fix")
os.makedirs(FIX, exist_ok=True)
for f in os.listdir(FIX):
    os.remove(os.path.join(FIX, f))

existing = {}
for l in open(os.path.join(WORK, "existing_msg_records.ndjson"), encoding="utf-8"):
    r = json.loads(l)
    existing[r["消息ID"]] = r

kept = [json.loads(l) for l in open(os.path.join(WORK, "messages_kept.ndjson"), encoding="utf-8")]

FIELDS = ["会话ID", "会话名称", "会话类型", "消息ID", "消息类型", "话题ID",
          "发送人", "发送人ID", "消息内容", "发送时间"]

updates = {}
creates = []
seen = set()
for r in kept:
    mid = r["消息ID"]
    if mid in seen:
        continue
    seen.add(mid)
    bj = r["发送时间"].strip().replace(" ", "T") + ":00+08:00"
    if mid in existing:
        rec = existing[mid]
        old = rec.get("发送时间") or ""
        if old.split(".")[0] != bj.split(".")[0].replace("T", "T"):
            pass
        updates[rec["record_id"]] = {"发送时间": bj}
    else:
        rec = {k: r[k] for k in FIELDS}
        rec["发送时间"] = bj
        creates.append(rec)

orphans = [m for m in existing if m not in seen]
print("kept:", len(kept), "existing:", len(existing), "updates:", len(updates),
      "creates:", len(creates), "orphan_table_records:", len(orphans))
if orphans:
    print("orphan ids:", orphans[:5])

items = list(updates.items())
n = 0
for i in range(0, len(items), 50):
    n += 1
    chunk = dict(items[i:i + 50])
    p = os.path.join(FIX, "upd_%02d.json" % n)
    json.dump({"update_records": chunk}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
print("update batches:", n)

if creates:
    p = os.path.join(FIX, "new_01.json")
    json.dump({"create_records": creates}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print("create batches: 1 (", len(creates), "records )")
