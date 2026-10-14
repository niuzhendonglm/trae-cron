import json, os, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
BASE_TOKEN = "KezfbQ2fDaNBonskSTZcM3YVnWf"


def call_create(table_id, rows, attempt=0):
    payload = json.dumps({"create_records": rows}, ensure_ascii=False)
    p = subprocess.run(
        ["lark-cli", "base", "+record-batch-create", "--as", "user",
         "--base-token", BASE_TOKEN, "--table-id", table_id,
         "--json", payload, "--format", "json"],
        capture_output=True, text=True, cwd=BASE)
    out = p.stdout.strip()
    try:
        d = json.loads(out)
    except Exception:
        d = {"ok": False, "error": {"message": (out or p.stderr)[:300]}}
    if d.get("ok"):
        return True, (d.get("data") or {}).get("record_id_list") or [], None
    err = d.get("error") or {}
    if attempt < 3 and (err.get("code") in (None,) or "rate" in str(err.get("message", "")).lower()):
        time.sleep(2 + attempt * 3)
        return call_create(table_id, rows, attempt + 1)
    return False, [], f"{err.get('code')} {err.get('message')}"


def write_chunk(table_id, rows, depth=0, results=None, failures=None):
    ok, ids, err = call_create(table_id, rows)
    if ok:
        results.extend(ids)
        print(f"{'  '*depth}OK n={len(rows)} -> {len(ids)} ids", flush=True)
        return
    print(f"{'  '*depth}FAIL n={len(rows)} err={err}", flush=True)
    if len(rows) == 1:
        failures.append({"row": rows[0], "error": err})
        return
    mid = len(rows) // 2
    write_chunk(table_id, rows[:mid], depth + 1, results, failures)
    write_chunk(table_id, rows[mid:], depth + 1, results, failures)


def main():
    src, table_id, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    chunk_size = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    recs = [json.loads(l) for l in open(os.path.join(BASE, src), encoding="utf-8") if l.strip()]
    rows = [r["fields"] if "fields" in r else r for r in recs]
    results, failures = [], []
    total = len(rows)
    for i in range(0, total, chunk_size):
        chunk = rows[i:i + chunk_size]
        print(f"[batch {i//chunk_size+1}] rows {i+1}-{i+len(chunk)} / {total}", flush=True)
        write_chunk(table_id, chunk, 0, results, failures)
        time.sleep(0.4)
    json.dump({"created": len(results), "record_ids": results,
               "failures": failures},
              open(os.path.join(BASE, f"{out_prefix}_result.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"DONE created={len(results)} failures={len(failures)} total={total}")


if __name__ == "__main__":
    main()
