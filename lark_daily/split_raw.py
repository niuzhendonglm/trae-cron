import json

recs = json.load(open("raw_records.json"))
print("total", len(recs))
# truncate very long content to keep payloads safe
maxlen = 0
for r in recs:
    c = r.get("消息内容") or ""
    maxlen = max(maxlen, len(c))
    if len(c) > 4000:
        r["消息内容"] = c[:4000] + "…(truncated)"
print("max content len", maxlen)

BATCH = 200
n = 0
for i in range(0, len(recs), BATCH):
    chunk = recs[i:i+BATCH]
    payload = {"create_records": chunk}
    fn = f"raw_batch_{n}.json"
    json.dump(payload, open(fn, "w"), ensure_ascii=False)
    print(fn, len(chunk))
    n += 1
print("batches", n)
