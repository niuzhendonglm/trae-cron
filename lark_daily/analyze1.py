import json, glob, os, collections, datetime, sys

CHATS = {c['chat_id']: c for c in json.load(open('/workspace/lark_daily/chats_all.json'))['data']['chats']}

files = sorted(glob.glob('/workspace/lark_daily/msgs/*.json'))
errs = []
all_msgs = []
for p in files:
    cid = os.path.basename(p)[:-5]
    try:
        d = json.load(open(p))
    except Exception as e:
        errs.append((cid, 'parse:' + str(e)))
        continue
    if not d.get('ok'):
        errs.append((cid, json.dumps(d.get('error', {}), ensure_ascii=False)[:300]))
        continue
    for m in (d.get('data', {}).get('messages') or []):
        m['_chat_id'] = cid
        all_msgs.append(m)

print('files', len(files), 'errors', len(errs))
for e in errs[:20]:
    print('ERR', e)
print('raw messages', len(all_msgs))
print('msg_type dist', collections.Counter(m.get('msg_type') for m in all_msgs))
print('chats with msgs', len(set(m['_chat_id'] for m in all_msgs)))
print('deleted', sum(1 for m in all_msgs if m.get('deleted')))

# sender name dist
print('--- senders ---')
for name, cnt in collections.Counter((m.get('sender') or {}).get('name') or (m.get('sender') or {}).get('id') for m in all_msgs).most_common(40):
    print(cnt, name)

print('--- sample message keys ---')
if all_msgs:
    print(json.dumps(all_msgs[0], ensure_ascii=False, indent=1)[:2000])

json.dump(all_msgs, open('/workspace/lark_daily/all_msgs_raw.json', 'w'), ensure_ascii=False)
