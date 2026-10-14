import json
import glob
import os

chats_meta = json.load(open("chats.json", encoding="utf-8"))["data"]["chats"]
chat_by_id = {c["chat_id"]: c for c in chats_meta}

search_chats = json.load(open("active_chats.json", encoding="utf-8"))

all_msgs = []
for path in sorted(glob.glob("perchat/*.json")):
    cid = os.path.basename(path)[:-5]
    d = json.load(open(path, encoding="utf-8"))
    if not d.get("ok"):
        print("FAIL", cid, json.dumps(d, ensure_ascii=False)[:200])
        continue
    msgs = (d.get("data") or {}).get("messages") or []
    meta = chat_by_id.get(cid) or {}
    name = meta.get("name") or (search_chats.get(cid) or {}).get("name")
    mode = meta.get("chat_mode") or (search_chats.get(cid) or {}).get("type")
    for m in msgs:
        m["_chat_id"] = cid
        m["_chat_name"] = name
        m["_chat_mode"] = mode
        m["_peer_type"] = meta.get("p2p_target_type")
        all_msgs.append(m)

print("total fetched messages:", len(all_msgs))
from collections import Counter

print("by msg_type:", Counter(m.get("msg_type") for m in all_msgs).most_common())
print("by sender_type:", Counter((m.get("sender") or {}).get("sender_type") for m in all_msgs).most_common())
print("chats covered:", len(set(m["_chat_id"] for m in all_msgs)))
print("deleted:", sum(1 for m in all_msgs if m.get("deleted")))

with open("all_msgs.json", "w", encoding="utf-8") as fh:
    json.dump(all_msgs, fh, ensure_ascii=False)
