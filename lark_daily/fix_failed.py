import json, re, subprocess

BASE="KezfbQ2fDaNBonskSTZcM3YVnWf"; TABLE="tblmbeQPFVKFR2Tb"
recs = json.load(open("raw_records.json"))
FAILED = [329,337,590,600]

def san(s):
    s = re.sub(r'<at user_id="all"\s*>(.*?)</at>', '@所有人', s)
    s = re.sub(r'<at user_id="all"\s*/>', '@所有人', s)
    s = re.sub(r'<at user_id="([^"]*)"\s*>(.*?)</at>', lambda m: '@'+(m.group(2) or '提及'), s)
    s = re.sub(r'<at user_id="([^"]*)"\s*/>', '@提及', s)
    return s

fixed = []
for i in FAILED:
    r = dict(recs[i])
    before = r["消息内容"]
    r["消息内容"] = san(before)
    changed = before != r["消息内容"]
    print(i, "changed:", changed, "| has_at:", "<at" in before, "->", "<at" in r["消息内容"])
    fixed.append(r)

payload = json.dumps({"create_records": fixed}, ensure_ascii=False)
print("payload bytes", len(payload.encode()))
p = subprocess.run(["lark-cli","base","+record-batch-create","--as","user",
    "--base-token",BASE,"--table-id",TABLE,"--json",payload,"--format","json"],
    capture_output=True, text=True)
print("exit", p.returncode)
out = p.stdout.strip()
try:
    d = json.loads(out)
    print("ok", d.get("ok"), "created", len(d.get("data",{}).get("record_id_list",[])))
    if not d.get("ok"): print(json.dumps(d.get("error",{}),ensure_ascii=False)[:300])
except Exception:
    print("RAW:", out[:300], p.stderr[:300])
