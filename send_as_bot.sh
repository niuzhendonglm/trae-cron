#!/usr/bin/env bash
# 以机器人应用身份发送飞书消息
# 用法: ./send_as_bot.sh --chat-id oc_xxx --markdown @./msg.md
#       ./send_as_bot.sh --chat-id oc_xxx --text "hello"
set -euo pipefail

CRED_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.lark_bot"
APP_ID="$(cat "$CRED_DIR/app_id")"
APP_SECRET="$(cat "$CRED_DIR/app_secret")"

TOKEN_JSON="$(curl -sS -X POST \
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")"

TOKEN="$(printf '%s' "$TOKEN_JSON" | sed -n 's/.*"tenant_access_token":"\([^"]*\)".*/\1/p')"
if [ -z "$TOKEN" ]; then
  echo "tenant_access_token 获取失败: $TOKEN_JSON" >&2
  exit 1
fi

exec env -u LARKSUITE_CLI_USER_ACCESS_TOKEN \
  LARKSUITE_CLI_APP_ID="$APP_ID" \
  LARKSUITE_CLI_TENANT_ACCESS_TOKEN="$TOKEN" \
  LARKSUITE_CLI_DEFAULT_AS=bot \
  LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1 \
  LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1 \
  lark-cli im +messages-send --as bot "$@"