#!/bin/bash
cd /workspace/lark_work || exit 1
BASE=KezfbQ2fDaNBonskSTZcM3YVnWf
TABLE=tblmbeQPFVKFR2Tb
run_one() {
  local f="$1"; local kind="$2"
  local cmd
  if [ "$kind" = "upd" ]; then
    cmd="timeout 180 lark-cli base +record-batch-update --base-token $BASE --table-id $TABLE --json @$f --as user"
  else
    cmd="timeout 180 lark-cli base +record-batch-create --base-token $BASE --table-id $TABLE --json @$f --as user"
  fi
  echo ">>> $f ($kind)"
  out=$(eval $cmd 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    echo "RETRY $f rc=$rc: $(echo "$out" | head -c 300)"
    sleep 3
    out=$(eval $cmd 2>&1); rc=$?
  fi
  if [ $rc -ne 0 ]; then
    echo "FAIL $f rc=$rc: $(echo "$out" | head -c 500)"
    return 1
  fi
  echo "OK $f: $(echo "$out" | head -c 120)"
  return 0
}
fails=0
for f in batches_fix/upd_*.json; do
  run_one "$f" upd || fails=$((fails+1))
  sleep 1
done
run_one batches_fix/new_01.json create || fails=$((fails+1))
echo "FIX_WRITE_DONE fails=$fails"
touch FIX_WRITE_COMPLETE
