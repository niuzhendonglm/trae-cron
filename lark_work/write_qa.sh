#!/usr/bin/env bash
set -u
cd /workspace/lark_work
LOG=write_qa.log
: > "$LOG"
fails=0
for f in batches_qa/qa_batch_01.json batches_qa/qa_batch_02.json; do
  ok=0
  for attempt in 1 2; do
    echo "[$(TZ=Asia/Shanghai date '+%H:%M:%S')] writing $f attempt=$attempt" >> "$LOG"
    out=$(timeout 180 lark-cli base +record-batch-create \
      --base-token KezfbQ2fDaNBonskSTZcM3YVnWf \
      --table-id tblrHaPTUI8x71ot \
      --json @"$f" --as user 2>&1)
    rc=$?
    echo "$out" | head -c 600 >> "$LOG"
    echo "" >> "$LOG"
    if [ $rc -eq 0 ]; then ok=1; break; fi
    echo "[$(TZ=Asia/Shanghai date '+%H:%M:%S')] $f attempt=$attempt FAILED rc=$rc" >> "$LOG"
    sleep 3
  done
  if [ $ok -ne 1 ]; then fails=$((fails+1)); fi
  sleep 2
done
echo "QA_WRITE_DONE fails=$fails" >> "$LOG"
