#!/bin/bash
# Fetch yesterday's messages for one chat, write to per-chat json file. 1 retry on failure.
CHAT_ID="$1"
CHAT_NAME="$2"
OUT_DIR="/workspace/lark_daily/msgs"
ERR_DIR="/workspace/lark_daily/errs"
mkdir -p "$OUT_DIR" "$ERR_DIR"
OUT="$OUT_DIR/$CHAT_ID.json"
if [ -s "$OUT" ]; then exit 0; fi
START="2026-10-26T00:00:00+08:00"
END="2026-10-26T23:59:59+08:00"
for attempt in 1 2; do
  timeout 180 lark-cli im +chat-messages-list --chat-id "$CHAT_ID" --start "$START" --end "$END" \
    --order asc --page-all --page-limit 20 --no-reactions --format json --as user > "$OUT" 2>"$ERR_DIR/$CHAT_ID.err"
  rc=$?
  if [ $rc -eq 0 ] && [ -s "$OUT" ]; then
    rm -f "$ERR_DIR/$CHAT_ID.err"
    exit 0
  fi
  rm -f "$OUT"
  sleep 2
done
echo "FAILED rc=$rc chat=$CHAT_ID name=$CHAT_NAME err=$(tail -c 300 "$ERR_DIR/$CHAT_ID.err" 2>/dev/null | tr '\n' ' ')" >> /workspace/lark_daily/failed_chats.log
exit 1
