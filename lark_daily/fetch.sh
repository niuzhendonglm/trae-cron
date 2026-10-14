#!/bin/bash
cd /workspace/lark_daily
fetch_one() {
  cid="$1"
  [ -s "msgs/$cid.json" ] && return 0
  lark-cli im +chat-messages-list --as user --chat-id "$cid" \
    --start "2026-10-13T00:00:00+08:00" --end "2026-10-13T23:59:59+08:00" \
    --order asc --page-all --page-limit 20 --no-reactions --format json \
    > "msgs/$cid.json" 2> "msgs/$cid.err"
}
export -f fetch_one
cat chat_ids.txt | xargs -P 10 -I{} bash -c 'fetch_one "$@"' _ {}
echo DONE_ALL > fetch.done
