import json, subprocess, sys

BASE="KezfbQ2fDaNBonskSTZcM3YVnWf"; TABLE="tblmbeQPFVKFR2Tb"
recs = json.load(open("raw_records.json"))
START = 200  # 0-199 already written
END = len(recs)

created_ids = []
failures = []  # (index, record, err)

def try_create(chunk):
    payload = json.dumps({"create_records": chunk}, ensure_ascii=False)
    p = subprocess.run(
        ["lark-cli","base","+record-batch-create","--as","user",
         "--base-token",BASE,"--table-id",TABLE,"--json",payload,"--format","json"],
        capture_output=True, text=True)
    out = (p.stdout or "").strip()
    try:
        d = json.loads(out)
        if d.get("ok") is True:
            return True, d.get("data",{}).get("record_id_list",[]), ""
        return False, [], d.get("error",{}).get("message","") or json.dumps(d.get("error",{}),ensure_ascii=False)[:200]
    except Exception:
        return False, [], ((p.stderr or out)[:200])

MAX_ARG_BYTES = 120000  # keep single argv under Linux MAX_ARG_STRLEN (128KB)

def process(a, b):
    """write recs[a:b]; adaptive split on failure; isolate single bad records."""
    chunk = recs[a:b]
    payload_bytes = len(json.dumps({"create_records": chunk}, ensure_ascii=False).encode("utf-8"))
    if payload_bytes > MAX_ARG_BYTES and b - a > 1:
        mid = (a+b)//2
        process(a, mid)
        process(mid, b)
        return
    ok, ids, err = try_create(chunk)
    if ok:
        created_ids.extend(ids)
        print(f"[{a}:{b}] OK +{len(ids)} (total {len(created_ids)})")
        return
    if b - a == 1:
        failures.append((a, recs[a], err))
        print(f"[{a}] FAIL isolated: {err}")
        return
    mid = (a+b)//2
    process(a, mid)
    process(mid, b)

process(START, END)

print("\n=== SUMMARY ===")
print("created:", len(created_ids), " failures:", len(failures))
for idx, r, err in failures:
    print(idx, r.get("消息类型"), r.get("会话名称"), "|", r.get("发送人"), "|", err)

json.dump({"created_ids": created_ids,
           "failures": [{"index":i,"record":r,"err":e} for i,r,e in failures]},
          open("raw_write_result.json","w"), ensure_ascii=False, indent=1)
