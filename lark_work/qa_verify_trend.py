#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, collections

def load(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def fld(rec, name):
    f = rec.get("fields") or rec
    v = f.get(name)
    if isinstance(v, list):
        v = "".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in v)
    return (v or "").strip() if isinstance(v, str) else ("" if v is None else str(v))

recs = load("verify_qa_records.ndjson")
print("yesterday records:", len(recs))
MAND = ["Question", "Answer", "提问人", "回复人", "问题类型", "问题日期"]
bad = 0
for r in recs:
    for m in MAND:
        if not fld(r, m):
            bad += 1
            print("EMPTY", m, r.get("record_id"))
print("empty mandatory fields:", bad)

ai = sum(1 for r in recs if fld(r, "回复人") == "AI助手")
print("AI answered:", ai)
tcount = collections.Counter(fld(r, "问题类型") for r in recs)
acount = collections.Counter(fld(r, "提问人") for r in recs)
rcount = collections.Counter(fld(r, "回复人") for r in recs)
print("type:", tcount.most_common())
print("asker:", acount.most_common())
print("replier:", rcount.most_common())

allr = load("qa_all_full.ndjson")
print("total all:", len(allr))
days = collections.Counter()
day_type = collections.defaultdict(collections.Counter)
day_asker = collections.defaultdict(collections.Counter)
for r in allr:
    d = fld(r, "问题日期")[:10]
    days[d] += 1
    day_type[d][fld(r, "问题类型")] += 1
    day_asker[d][fld(r, "提问人")] += 1
for d in sorted(days):
    print(d, days[d], "| top types:", day_type[d].most_common(3), "| top askers:", day_asker[d].most_common(3))
