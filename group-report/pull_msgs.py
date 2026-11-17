import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

START = "2026-11-16 00:00:00"
END = "2026-11-16 23:59:59"
OUT = "./raw_msgs"
os.makedirs(OUT, exist_ok=True)

chats = json.load(open("./chats.json"))["data"]["chats"]
# skip chats already done
todo = [c for c in chats if not os.path.exists(os.path.join(OUT, c["chat_id"] + ".json"))]
print("todo", len(todo), "of", len(chats), flush=True)

def pull(chat):
    cid = chat["chat_id"]
    path = os.path.join(OUT, cid + ".json")
    cmd = ["timeout", "180", "lark-cli", "im", "+chat-messages-list",
           "--chat-id", cid, "--start", START, "--end", END,
           "--order", "asc", "--page-all", "--page-size", "50",
           "--no-reactions", "--as", "user"]
    for attempt in range(2):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
            if p.returncode == 0 and p.stdout.strip().startswith("{"):
                d = json.loads(p.stdout)
                if d.get("ok"):
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(d, f, ensure_ascii=False)
                    n = len(d.get("data", {}).get("messages") or [])
                    return (cid, "ok", n, "")
                err = json.dumps(d.get("error", {}), ensure_ascii=False)[:200]
            else:
                err = (p.stderr or p.stdout)[:200]
        except Exception as e:
            err = str(e)[:200]
        time.sleep(1.5)
    return (cid, "fail", 0, err)

ok = fail = msgs = 0
fails = []
with ThreadPoolExecutor(max_workers=5) as ex:
    for cid, status, n, err in ex.map(pull, todo):
        if status == "ok":
            ok += 1
            msgs += n
        else:
            fail += 1
            fails.append({"chat_id": cid, "error": err})
        if (ok + fail) % 50 == 0:
            print("progress", ok + fail, "ok", ok, "fail", fail, "msgs", msgs, flush=True)

json.dump(fails, open("./tmp/pull_fails.json", "w"), ensure_ascii=False, indent=1)
print("DONE ok", ok, "fail", fail, "msgs", msgs, flush=True)