#!/bin/bash
TID="$1"
OUT="/workspace/lark_daily/threads/$TID.json"
if [ -s "$OUT" ]; then exit 0; fi
for attempt in 1 2; do
  timeout 180 lark-cli im +threads-messages-list --thread "$TID" --order asc --page-all --page-limit 10 \
    --no-reactions --format json --as user > "$OUT" 2>"/workspace/lark_daily/errs/thread_$TID.err"
  rc=$?
  if [ $rc -eq 0 ] && [ -s "$OUT" ]; then rm -f "/workspace/lark_daily/errs/thread_$TID.err"; exit 0; fi
  rm -f "$OUT"; sleep 2
done
echo "THREAD_FAILED rc=$rc thread=$TID $(tail -c 200 /workspace/lark_daily/errs/thread_$TID.err 2>/dev/null | tr '\n' ' ')" >> /workspace/lark_daily/failed_threads.log
exit 1
