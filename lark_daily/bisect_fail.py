import json, subprocess, sys

recs = json.load(open("raw_records.json"))

def try_create(chunk):
    payload = json.dumps({"create_records": chunk}, ensure_ascii=False)
    p = subprocess.run(
        ["lark-cli","base","+record-batch-create","--as","user",
         "--base-token","KezfbQ2fDaNBonskSTZcM3YVnWf",
         "--table-id","tblmbeQPFVKFR2Tb","--json",payload,"--format","json"],
        capture_output=True, text=True)
    out = p.stdout.strip()
    ok = False
    try:
        d = json.loads(out)
        ok = d.get("ok") is True
        err = d.get("error",{}).get("message","")
    except Exception:
        err = (p.stderr or out)[:200]
    return ok, err

# batch1 = indices 200..399
lo, hi = 200, 400
# find a failing single record by bisecting the range
def find_fail(a, b):
    # returns index of a failing record within [a,b)
    chunk = recs[a:b]
    ok, err = try_create(chunk)
    if ok:
        return None, err
    if b - a == 1:
        return a, err
    mid = (a+b)//2
    idx, e = find_fail(a, mid)
    if idx is not None:
        return idx, e
    return find_fail(mid, b)

idx, err = find_fail(lo, hi)
print("failing index:", idx, "err:", err)
if idx is not None:
    r = recs[idx]
    print(json.dumps(r, ensure_ascii=False, indent=1)[:1500])
    for k,v in r.items():
        print(k, type(v).__name__, (str(v)[:80]))
