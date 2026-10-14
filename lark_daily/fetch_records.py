import json
import subprocess
import sys


def fetch(base_token, table_id, field_ids=None, filter_json=None, out_path=None):
    rows = []
    fields = None
    offset = 0
    while True:
        cmd = [
            "lark-cli", "base", "+record-list",
            "--base-token", base_token,
            "--table-id", table_id,
            "--as", "user",
            "--limit", "200",
            "--offset", str(offset),
            "--format", "json",
        ]
        for f in (field_ids or []):
            cmd += ["--field-id", f]
        if filter_json:
            cmd += ["--filter-json", filter_json]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        payload = json.loads(proc.stdout)
        if not payload.get("ok"):
            raise RuntimeError(json.dumps(payload, ensure_ascii=False)[:800])
        data = payload["data"]
        fields = data.get("fields") or fields
        batch = data.get("data") or []
        rows.extend(batch)
        if not data.get("has_more") or not batch:
            break
        offset += len(batch)
    result = {"fields": fields, "rows": rows}
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False)
    return result


if __name__ == "__main__":
    base_token = sys.argv[1]
    table_id = sys.argv[2]
    out_path = sys.argv[3]
    field_ids = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None
    filter_json = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else None
    res = fetch(base_token, table_id, field_ids, filter_json, out_path)
    print("fields:", res["fields"])
    print("rows:", len(res["rows"]))
