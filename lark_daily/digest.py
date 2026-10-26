import json, sys

conv = json.load(open('/tmp/conversations.json'))
items = sorted(conv.items(), key=lambda kv: -len(kv[1]['messages']))
start = int(sys.argv[1]); end = int(sys.argv[2])
maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 200
for idx, (cid, v) in enumerate(items):
    if idx < start or idx >= end:
        continue
    print(f"\n##### [{idx}] {v['name']} ({v['type']}, {len(v['messages'])} msgs) {cid}")
    cur_thread = None
    for m in v['messages']:
        th = m['thread']
        prefix = '   ↳' if th else ''
        if th and th != cur_thread:
            cur_thread = th
        txt = m['text']
        if len(txt) > maxlen:
            txt = txt[:maxlen] + '…'
        print(f"{m['t'][11:]} {m['who'][:12]:<12}{prefix} [{m['type']}] {txt}")
