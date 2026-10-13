import json, subprocess, sys

BASE = "KezfbQ2fDaNBonskSTZcM3YVnWf"
TABLE = "tblrHaPTUI8x71ot"
MAX_ARG_BYTES = 120000
BATCH = 200

recs = json.load(open('/workspace/lark_daily/qa_final.json'))
recs = [{k: v for k, v in r.items() if k != '_meta'} for r in recs]
for r in recs:
    for f in ["Question", "Answer", "提问人", "回复人", "问题类型", "问题日期"]:
        assert r.get(f), (f, r)

created_ids = []
failures = []

def payload_bytes(chunk):
    return len(json.dumps({"create_records": chunk}, ensure_ascii=False).encode('utf-8'))

def try_create(chunk):
    payload = json.dumps({"create_records": chunk}, ensure_ascii=False)
    p = subprocess.run(
        ["lark-cli", "base", "+record-batch-create", "--as", "user",
         "--base-token", BASE, "--table-id", TABLE, "--json", payload, "--format", "json"],
        capture_output=True, text=True)
    out = p.stdout.strip()
    if p.returncode == 0 and out:
        try:
            j = json.loads(out)
            data = j.get('data', j)
            ids = data.get('record_id_list') or []
            if not ids:
                ids = [r.get('record_id') for r in data.get('records', []) if r.get('record_id')]
            if ids or j.get('ok') is True:
                return True, ids, ''
        except Exception:
            pass
    return False, [], (out + p.stderr)[:400]

def process(a, b):
    chunk = recs[a:b]
    if (payload_bytes(chunk) > MAX_ARG_BYTES or len(chunk) > BATCH) and b - a > 1:
        mid = (a + b) // 2
        process(a, mid)
        process(mid, b)
        return
    ok, ids, err = try_create(chunk)
    if ok:
        created_ids.extend(ids)
        print(f"[{a}:{b}] OK {len(ids)}", flush=True)
        return
    if b - a == 1:
        failures.append((a, recs[a], err))
        print(f"[{a}:{b}] FAIL {err[:200]}", flush=True)
        return
    mid = (a + b) // 2
    process(a, mid)
    process(mid, b)

process(0, len(recs))
print("created:", len(created_ids), "failed:", len(failures))
json.dump({"created_ids": created_ids,
           "failures": [{"idx": i, "rec": r, "err": e} for i, r, e in failures]},
          open('/workspace/lark_daily/qa_write_result.json', 'w'), ensure_ascii=False, indent=1)
