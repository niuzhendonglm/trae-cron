#!/bin/bash
# Resumable pull of 2026-10-21 (Beijing) messages for every chat.
set -u
WORK=/workspace/lark_work
RAW="$WORK/msgs_raw"
mkdir -p "$RAW"
START="2026-10-21T00:00:00+08:00"
END="2026-10-22T00:00:00+08:00"

fetch_one() {
  cid="$1"
  out="$RAW/$cid.json"
  err="$RAW/$cid.err"
  # resume: already have a successful dump
  if [ -s "$out" ] && head -c 200 "$out" | grep -q '"ok": true'; then
    echo "SKIP $cid"
    return 0
  fi
  for attempt in 1 2; do
    timeout 120 lark-cli im +chat-messages-list \
      --chat-id "$cid" --start "$START" --end "$END" \
      --order asc --page-all --page-limit 60 --no-reactions --as user \
      > "$out" 2> "$err"
    rc=$?
    if [ $rc -eq 0 ] && head -c 200 "$out" | grep -q '"ok": true'; then
      rm -f "$err"
      echo "OK $cid"
      return 0
    fi
    # permanent api error (e.g. restricted chat) -> record and stop retrying
    if [ $rc -eq 0 ] && grep -q '"ok": false' "$out" 2>/dev/null; then
      if grep -qE '"code": (231203|230002|230001|230013|234001|231202)' "$out" 2>/dev/null; then
        echo "PERMFAIL $cid"
        echo "PERMFAIL $cid" >> "$WORK/pull_fail.log"
        return 0
      fi
    fi
    echo "RETRY($attempt) rc=$rc $cid" >> "$WORK/pull_fail.log"
    sleep 1
  done
  echo "FAIL $cid"
  echo "FAIL $cid" >> "$WORK/pull_fail.log"
  return 0
}
export -f fetch_one
export RAW START END WORK

: > "$WORK/pull_fail.log"
xargs -a "$WORK/chat_ids.txt" -d '\n' -n 1 -P 8 -I{} bash -c 'fetch_one "$@"' _ {} >> "$WORK/pull_progress.log" 2>&1
echo "ALLDONE $(date '+%Y-%m-%d %H:%M:%S')" >> "$WORK/pull_progress.log"
touch "$WORK/PULL_COMPLETE"
