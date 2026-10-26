#!/bin/bash
# Serial batch write of raw messages into 消息记录 table (R5: max 50 per batch, strictly serial)
BASE=KezfbQ2fDaNBonskSTZcM3YVnWf
TABLE=tblmbeQPFVKFR2Tb
LOG=/workspace/lark_daily/raw_write.log
DONE=/workspace/lark_daily/raw_done
mkdir -p "$DONE"
touch "$DONE/raw_00.json"
for f in $(ls /tmp/batches/raw_*.json | sort); do
  bn=$(basename "$f")
  if [ -f "$DONE/$bn" ]; then echo "SKIP $bn already done" >> "$LOG"; continue; fi
  ok=0
  for attempt in 1 2; do
    timeout 180 lark-cli base +record-batch-create --base-token "$BASE" --table-id "$TABLE" \
      --json @"$f" --as user > "/tmp/batches/$bn.out" 2>&1
    rc=$?
    if [ $rc -eq 0 ] && grep -q '"ok": true' "/tmp/batches/$bn.out"; then
      n=$(grep -o 'rec[A-Za-z0-9]\{8,\}' "/tmp/batches/$bn.out" | sort -u | wc -l)
      echo "OK $bn rc=0 created=$n" >> "$LOG"
      touch "$DONE/$bn"
      ok=1
      break
    fi
    echo "RETRY $bn rc=$rc attempt=$attempt $(tail -c 200 /tmp/batches/$bn.out | tr '\n' ' ')" >> "$LOG"
    sleep 3
  done
  if [ $ok -ne 1 ]; then echo "FAILED_BATCH $bn" >> "$LOG"; fi
  sleep 1
done
echo "RAW_WRITE_DONE ok=$(ls $DONE | wc -l) failed=$(grep -c '^FAILED_BATCH' $LOG)" >> "$LOG"
