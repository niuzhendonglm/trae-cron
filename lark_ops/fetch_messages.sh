#!/usr/bin/env bash
# Fetch yesterday's messages for every chat in chats.json (parallel, resumable)
set -u
cd /workspace/lark_ops
START="2026-10-14T00:00:00+08:00"
END="2026-10-14T23:59:59+08:00"
OUTDIR=raw
mkdir -p "$OUTDIR"

CONCURRENCY="${CONCURRENCY:-5}"

python3 -c "
import json
d=json.load(open('chats.json'))
for c in d['data']['chats']:
    print(c['chat_id'])
" > chat_ids.txt

fetch_one() {
  local cid="$1"
  local out="$OUTDIR/$cid.json"
  if [ -s "$out" ]; then
    if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$out" >/dev/null 2>&1; then
      return 0
    fi
  fi
  for attempt in 1 2 3; do
    lark-cli im +chat-messages-list --as user --chat-id "$cid" \
      --start "$START" --end "$END" --order asc --page-size 50 \
      --page-all --page-limit 60 --no-reactions --format json > "$out.tmp" 2>"$out.err"
    if [ $? -eq 0 ] && python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$out.tmp" >/dev/null 2>&1; then
      mv "$out.tmp" "$out"
      rm -f "$out.err"
      return 0
    fi
    sleep $((attempt*2))
  done
  mv "$out.tmp" "$out" 2>/dev/null || true
  echo "FAILED $cid" >> fetch_failures.txt
}
export -f fetch_one
export OUTDIR START END

cat chat_ids.txt | xargs -P "$CONCURRENCY" -I{} bash -c 'fetch_one "$@"' _ {}
echo "DONE: $(ls -1 $OUTDIR | wc -l) files"
