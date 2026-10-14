import json, subprocess, sys, os

BASE = "KezfbQ2fDaNBonskSTZcM3YVnWf"
TABLE = "tblmbeQPFVKFR2Tb"
SRC = sys.argv[1] if len(sys.argv) > 1 else "msg_batch_1.json"
CHUNK = int(sys.argv[2]) if len(sys.argv) > 2 else 20

recs = json.load(open(SRC))["create_records"]
os.makedirs("chunks", exist_ok=True)
failed = []
written = 0


def call(items, tag):
    fn = f"chunks/{tag}.json"
    json.dump({"create_records": items}, open(fn, "w"), ensure_ascii=False)
    p = subprocess.run(
        ["lark-cli", "base", "+record-batch-create", "--base-token", BASE,
         "--table-id", TABLE, "--as", "user", "--json", "@" + fn, "--format", "json"],
        capture_output=True, text=True, timeout=300)
    out = p.stdout.strip()
    try:
        d = json.loads(out)
    except Exception:
        return False, (out or p.stderr)[:300]
    if d.get("ok"):
        data = d.get("data") or {}
        n = len(data.get("record_id_list") or data.get("records") or [])
        return True, n
    return False, json.dumps(d.get("error"), ensure_ascii=False)[:300]


def attempt(items, tag):
    global written
    ok, info = call(items, tag)
    if ok:
        written += len(items)
        print(f"[OK] {tag} n={len(items)} created={info}", flush=True)
        return
    print(f"[FAIL] {tag} n={len(items)} err={info}", flush=True)
    if len(items) == 1:
        failed.append({"tag": tag, "record": items[0], "error": info})
        return
    mid = len(items) // 2
    attempt(items[:mid], tag + "a")
    attempt(items[mid:], tag + "b")


for i in range(0, len(recs), CHUNK):
    attempt(recs[i:i + CHUNK], f"c{i:04d}")

json.dump(failed, open("failed_records.json", "w"), ensure_ascii=False, indent=1)
print("WRITTEN", written, "FAILED", len(failed))
