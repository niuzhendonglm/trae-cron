#!/bin/bash
cd /workspace/lark_daily
mkdir -p done_qa
for f in /tmp/batches/qa_*.json; do
  b=$(basename "$f" .json)
  [ -f "done_qa/$b" ] && continue
  ok=0
  for try in 1 2; do
    out=$(timeout 180 lark-cli base +record-batch-create --base-token KezfbQ2fDaNBonskSTZcM3YVnWf --table-id tblrHaPTUI8x71ot --json @"$f" --as user 2>&1)
    if echo "$out" | grep -q '"ok": true' && echo "$out" | grep -qo 'rec[A-Za-z0-9]\{8,\}'; then
      n=$(echo "$out" | grep -o 'rec[A-Za-z0-9]\{8,\}' | wc -l)
      echo "$b OK records=$n"
      touch "done_qa/$b"
      ok=1
      break
    else
      echo "$b try$try FAIL: $(echo "$out" | head -c 300)"
      sleep 5
    fi
  done
  [ $ok -eq 0 ] && echo "$b GIVEUP" && exit 1
done
echo ALL_QA_DONE
