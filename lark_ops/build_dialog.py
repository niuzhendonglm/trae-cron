import json, os, re
from collections import OrderedDict

BASE = os.path.dirname(os.path.abspath(__file__))
recs = [json.loads(l) for l in open(os.path.join(BASE, "msg_records.ndjson"), encoding="utf-8") if l.strip()]

AT = re.compile(r'<at user_id="([^"]*)"\s*>(.*?)</at>')


def clean(t):
    t = AT.sub(lambda m: "@" + (m.group(2) or ("所有人" if m.group(1) == "all" else "成员")), t)
    t = re.sub(r"!\[Image\]\(([^)]+)\)", "[图片]", t)
    t = re.sub(r"\[Image: [^\]]+\]", "[图片]", t)
    t = re.sub(r"<file key=\"[^\"]*\" name=\"([^\"]*)\"/>", r"[文件:\1]", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


groups = OrderedDict()
for r in recs:
    f = r["fields"]
    cid = f["会话ID"]
    groups.setdefault(cid, {"name": f["会话名称"], "type": f["会话类型"], "msgs": []})
    groups[cid]["msgs"].append(f)

for g in groups.values():
    g["msgs"].sort(key=lambda m: m["发送时间"])

items = sorted(groups.items(), key=lambda kv: -len(kv[1]["msgs"]))

lines = []
for cid, g in items:
    lines.append("=" * 90)
    lines.append(f"CHAT: {g['name']} | {g['type']} | {cid} | {len(g['msgs'])} msgs")
    for m in g["msgs"]:
        c = clean(m["消息内容"])
        if not c:
            c = f"[{m['消息类型']}]"
        lines.append(f"  [{m['发送时间'][11:16]}] {m['发送人']} ({m['消息类型']}): {c[:500]}")

open(os.path.join(BASE, "dialog.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("chats", len(items), "lines", len(lines), "msgs", len(recs))
for cid, g in items:
    print(f"{len(g['msgs']):4d}  {g['type']}  {g['name']}")
