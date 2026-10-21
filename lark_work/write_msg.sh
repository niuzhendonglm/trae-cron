#!/bin/bash
set -u
cd /workspace/lark_work
BASE=KezfbQ2fDaNBonskSTZcM3YVnWf
TABLE=tblmbeQPFVKFR2Tb
: > write_msg_result.log
ok_batches=0
fail_batches=0
for f in batches_msg/msg_batch_*.json; do
  rel="./$f"
  success=0
  for attempt in 1 2; do
    out=$(timeout 180 lark-cli base +record-batch-create --base-token "$BASE" --table-id "$TABLE" --json "@$rel" --as user 2>&1)
    rc=$?
    if [ $rc -eq 0 ] && echo "$out" | grep -q '"ok": true'; then
      n=$(echo "$out" | python3 -c "import sys,json;d=json.load(sys.stdin);print(len(((d.get('data') or {}).get('records') or (d.get('data') or {}).get('record_id_list') or [])))" 2>/dev/null || echo "?")
      echo "OK $f created=$n" >> write_msg_result.log
      ok_batches=$((ok_batches+1))
      success=1
      break
    fi
    echo "RETRY($attempt) rc=$rc $f :: $(echo "$out" | tr -d '\n' | head -c 400)" >> write_msg_result.log
    sleep 3
  done
  if [ $success -eq 0 ]; then
    echo "FAIL $f" >> write_msg_result.log
    fail_batches=$((fail_batches+1))
  fi
  sleep 1
done
echo "SUMMARY ok=$ok_batches fail=$fail_batches" >> write_msg_result.log
touch WRITE_MSG_COMPLETE
