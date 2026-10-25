import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

DAY = "2026-10-25"
START = DAY + "T00:00:00+08:00"
END = DAY + "T23:59:59+08:00"
OUT_DIR = "/workspace/lark_daily/msgs"
PROGRESS = "/workspace/lark_daily/pull_progress.log"

os.makedirs(OUT_DIR, exist_ok=True)

with open("/tmp/chatlist.json", encoding="utf-8") as f:
    chats = json.load(f)["data"]["chats"]

lock = threading.Lock()
counter = {"done": 0, "hit": 0, "fail": 0}


def log(line):
    with lock:
        with open(PROGRESS, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def pull(chat):
    cid = chat["chat_id"]
    dest = os.path.join(OUT_DIR, cid + ".json")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return cid, "cached"
    cmd = [
        "timeout", "180", "lark-cli", "im", "+chat-messages-list",
        "--chat-id", cid,
        "--start", START,
        "--end", END,
        "--order", "asc",
        "--page-size", "50",
        "--page-all", "--page-limit", "40",
        "--no-reactions",
        "--as", "user",
        "--format", "json",
    ]
    last_err = ""
    for attempt in range(2):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    payload = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    last_err = "bad json: " + proc.stdout[:200]
                    continue
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
                return cid, "ok"
            last_err = (proc.stderr or proc.stdout or "")[-300:]
        except subprocess.TimeoutExpired:
            last_err = "timeout"
        except Exception as exc:
            last_err = repr(exc)
    return cid, "fail: " + last_err.replace("\n", " ")


results = {}
total = len(chats)
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = {pool.submit(pull, c): c for c in chats}
    for fut in as_completed(futures):
        chat = futures[fut]
        cid, status = fut.result()
        results[cid] = status
        with lock:
            counter["done"] += 1
            n = counter["done"]
            if status.startswith("fail"):
                counter["fail"] += 1
        if n % 25 == 0 or status.startswith("fail"):
            log("progress %d/%d fails=%d last=%s %s" % (n, total, counter["fail"], cid, status[:120]))

with open("/workspace/lark_daily/pull_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

log("DONE total=%d fails=%d" % (total, counter["fail"]))
print("DONE total=%d fails=%d" % (total, counter["fail"]))
