import json, subprocess

BASE = "KezfbQ2fDaNBonskSTZcM3YVnWf"
TABLE = "tblrHaPTUI8x71ot"

ids = []
for line in open('/workspace/lark_daily/qa_written_check.ndjson'):
    line = line.strip()
    if not line:
        continue
    d = json.loads(line)
    if d.get('record_id'):
        ids.append(d['record_id'])
print('to delete:', len(ids))

deleted = 0
for i in range(0, len(ids), 200):
    chunk = ids[i:i+200]
    payload = json.dumps({"record_id_list": chunk})
    p = subprocess.run(
        ["lark-cli", "base", "+record-delete", "--as", "user",
         "--base-token", BASE, "--table-id", TABLE, "--json", payload, "--yes", "--format", "json"],
        capture_output=True, text=True)
    ok = False
    try:
        j = json.loads(p.stdout)
        ok = bool(j.get('ok')) or j.get('code') == 0
    except Exception:
        pass
    if ok:
        deleted += len(chunk)
        print(f'batch {i//200}: deleted {len(chunk)}')
    else:
        print(f'batch {i//200}: FAIL', (p.stdout + p.stderr)[:300])
print('total deleted:', deleted)
