#!/usr/bin/env bash
set -u
cd /workspace/lark_daily
mkdir -p msgs logs
START="2026-10-12T00:00:00+08:00"
END="2026-10-12T23:59:59+08:00"

fetch_one() {
  cid="$1"
  out="msgs/${cid}.json"
  if [ -s "$out" ]; then return 0; fi
  lark-cli im +chat-messages-list --as user --chat-id "$cid" \
    --start "$START" --end "$END" --order asc --page-all --page-limit 20 \
    --no-reactions --format json > "$out" 2>"logs/${cid}.err"
  rc=$?
  if [ $rc -ne 0 ]; then echo "FAIL $cid rc=$rc" >> logs/failures.txt; fi
}
export -f fetch_one
export START END

python3 -c "
import json
d=json.load(open('chats_all.json'))
for c in d['data']['chats']:
    print(c['chat_id'])
" > logs/chat_ids.txt

total=$(wc -l < logs/chat_ids.txt)
echo "total chats: $total"
cat logs/chat_ids.txt | xargs -P 6 -I{} bash -c 'fetch_one "$@"' _ {}
echo "DONE"
ls msgs | wc -l
