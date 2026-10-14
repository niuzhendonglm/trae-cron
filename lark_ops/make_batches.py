import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
prefix = sys.argv[2]
SIZE = 200

recs = [json.loads(l) for l in open(os.path.join(BASE, src), encoding="utf-8") if l.strip()]
rows = []
for r in recs:
    rows.append(r["fields"] if "fields" in r else r)

n = 0
for i in range(0, len(rows), SIZE):
    chunk = rows[i:i + SIZE]
    n += 1
    out = os.path.join(BASE, f"{prefix}_batch{n}.json")
    json.dump({"create_records": chunk}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(out, len(chunk))
print("total", len(rows), "batches", n)
