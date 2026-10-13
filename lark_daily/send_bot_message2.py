import json
import re
import urllib.request

APP_ID = "cli_a9630741047a1cb1"
CHAT_ID = "oc_5c11ab5f3bd43008d8e58cdd2d62199b"
UUID = "daily-report-2026-10-12-bot"

with open(".bot_secret.tmp", "r") as f:
    app_secret = f.read().strip()


def req(url, payload=None, token=None, method=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    r.add_header("Content-Type", "application/json; charset=utf-8")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode("utf-8"))


tok = req(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    {"app_id": APP_ID, "app_secret": app_secret},
)
assert tok.get("code") == 0, "token fail"
tat = tok["tenant_access_token"]

# 1) recall the previous plain post message
lst = req(
    "https://open.feishu.cn/open-apis/im/v1/messages?container_id_type=chat"
    "&container_id=" + CHAT_ID + "&sort_type=ByCreateTimeDesc&page_size=10",
    token=tat,
)
recalled = []
if lst.get("code") == 0:
    for it in lst.get("data", {}).get("items", []):
        if it.get("msg_type") == "post" and it.get("sender", {}).get("sender_type") == "app":
            did = it.get("message_id")
            d = req(
                "https://open.feishu.cn/open-apis/im/v1/messages/" + did,
                token=tat, method="DELETE")
            recalled.append((did, d.get("code")))
            break
else:
    print("LIST_FAIL code:", lst.get("code"), lst.get("msg"))
print("recalled:", recalled)

# 2) send fixed card (schema 2.0, no padding/text_size fields)
with open("chat_message.md", "r") as f:
    md = f.read()

lines = md.split("\n")
title = "运维日报"
body_lines = []
for ln in lines:
    m = re.match(r"^#\s+(.*)$", ln)
    if m and not body_lines:
        title = m.group(1).strip()
        continue
    body_lines.append(ln)
body_md = "\n".join(body_lines).strip()

card = {
    "schema": "2.0",
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": title},
        "template": "blue",
    },
    "body": {"elements": [{"tag": "markdown", "content": body_md}]},
}

resp = req(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    {
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False),
        "uuid": UUID,
    },
    token=tat,
)
if resp.get("code") == 0:
    print("CARD_SEND_OK message_id:", resp["data"]["message_id"])
else:
    print("CARD_SEND_FAIL", json.dumps(resp, ensure_ascii=False)[:1500])
