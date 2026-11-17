import json, subprocess, time, sys

BASE = "KezfbQ2fDaNBonskSTZcM3YVnWf"
MSG_TABLE = "tblmbeQPFVKFR2Tb"
QA_TABLE = "tblrHaPTUI8x71ot"


def batch_create(table, records, label):
    results = []
    for i in range(0, len(records), 50):
        chunk = records[i:i + 50]
        path = "./tmp/payload_%s_%d.json" % (label, i // 50)
        json.dump({"create_records": chunk}, open(path, "w"), ensure_ascii=False)
        cmd = ["timeout", "180", "lark-cli", "base", "+record-batch-create",
               "--base-token", BASE, "--table-id", table,
               "--json", "@" + path, "--as", "user"]
        ok = False
        for attempt in range(2):
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
            try:
                d = json.loads(p.stdout)
            except Exception:
                d = {}
            if p.returncode == 0 and d.get("ok"):
                n = len(d.get("data", {}).get("record_id_list") or [])
                print("batch", label, i // 50, "ok", n, flush=True)
                ok = True
                break
            print("batch", label, i // 50, "FAIL attempt", attempt, (p.stdout or p.stderr)[:300], flush=True)
            time.sleep(2)
        if not ok:
            results.append({"chunk": i // 50, "error": (p.stdout or p.stderr)[:500]})
    return results


msgs = json.load(open("./tmp/msg_records.json"))
qa = json.load(open("./tmp/qa_records.json"))
print("writing messages", len(msgs), flush=True)
fails = batch_create(MSG_TABLE, msgs, "msg")
print("writing qa", len(qa), flush=True)
fails += batch_create(QA_TABLE, qa, "qa")
json.dump(fails, open("./tmp/write_fails.json", "w"), ensure_ascii=False, indent=1)
print("FAILS", len(fails), flush=True)