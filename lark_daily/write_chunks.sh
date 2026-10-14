#!/bin/bash
# usage: ./write_chunks.sh <payload_prefix> <start_idx> <end_idx>
set -u
BASE=KezfbQ2fDaNBonskSTZcM3YVnWf
TABLE=tblmbeQPFVKFR2Tb
mkdir -p chunks
python3 - "$@" <<'PY'
import json,sys
src, s, e = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
recs = json.load(open(src))['create_records'][s:e]
size = 20
n = 0
for i in range(0, len(recs), size):
    part = recs[i:i+size]
    fn = f"chunks/{src.replace('.json','')}_{s+i:04d}.json"
    json.dump({"create_records": part}, open(fn,'w'), ensure_ascii=False)
    print(fn, len(part))
    n += 1
print("chunks", n)
PY
