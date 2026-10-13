import json, collections

recs = json.load(open("raw_records.json"))

# 1) type check: every value must be str
bad_types = []
for i,r in enumerate(recs):
    for k,v in r.items():
        if not isinstance(v, str):
            bad_types.append((i,k,type(v).__name__, str(v)[:100]))
print("non-string values:", len(bad_types))
for b in bad_types[:20]: print(b)

# 2) compare batch0 (0-199, succeeded) vs batch1+ (200+, failed)
def scan(sub, label):
    print(f"\n=== {label} (n={len(sub)}) ===")
    print("msg_type:", collections.Counter(r["消息类型"] for r in sub))
    # sender id prefixes
    pref = collections.Counter((r["发送人ID"][:3] if r["发送人ID"] else "EMPTY") for r in sub)
    print("senderID prefix:", dict(pref))
    empty_sid = sum(1 for r in sub if not r["发送人ID"])
    empty_send = sum(1 for r in sub if not r["发送人"])
    print("empty 发送人ID:", empty_sid, " empty 发送人:", empty_send)

scan(recs[0:200], "batch0 OK")
scan(recs[200:400], "batch1 FAIL")
scan(recs[400:695], "batch2+3 FAIL")
