import json
import re
import urllib.request

APP_ID = "cli_a9630741047a1cb1"
CHAT_ID = "oc_5c11ab5f3bd43008d8e58cdd2d62199b"
UUID = "daily-report-2026-10-12-bot"

with open(".bot_secret.tmp", "r") as f:
    app_secret = f.read().strip()


def post(url, payload, token=None):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode("utf-8"))


tok_resp = post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    {"app_id": APP_ID, "app_secret": app_secret},
)
if tok_resp.get("code") != 0:
    print("TOKEN_FAIL", json.dumps(tok_resp, ensure_ascii=False))
    raise SystemExit(1)
tat = tok_resp["tenant_access_token"]
print("token acquired, expire:", tok_resp.get("expire"))

with open("chat_message.md", "r") as f:
    md = f.read()

lines = md.split("\n")
title = "运维日报"
body_lines = []
for i, ln in enumerate(lines):
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
        "padding": "default",
    },
    "body": {
        "elements": [
            {"tag": "markdown", "content": body_md, "text_size": "normal"}
        ]
    },
}

send_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
resp = post(
    send_url,
    {
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False),
        "uuid": UUID,
    },
    token=tat,
)
ok = resp.get("code") == 0
print("SEND_OK" if ok else "SEND_FAIL")
print(json.dumps(resp, ensure_ascii=False)[:2000])

if not ok:
    md_no_table = "\n".join(
        ln for ln in body_lines if not ln.strip().startswith("|")
    ).strip()
    post_payload = {
        "zh_cn": {
            "title": title,
            "content": [[{"tag": "text", "text": md_no_table}]],
        }
    }
    resp2 = post(
        send_url,
        {
            "receive_id": CHAT_ID,
            "msg_type": "post",
            "content": json.dumps(post_payload, ensure_ascii=False),
            "uuid": UUID + "-post",
        },
        token=tat,
    )
    ok2 = resp2.get("code") == 0
    print("FALLBACK_POST_OK" if ok2 else "FALLBACK_POST_FAIL")
    print(json.dumps(resp2, ensure_ascii=False)[:2000])
