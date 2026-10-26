import json, os, collections

rows = json.load(open('/tmp/chats_flat.json'))
meta = {r['chat_id']: r for r in rows}
msg_dir = '/workspace/lark_daily/msgs'

all_msgs = []
stats = collections.Counter()
chat_with_msg = 0
for fn in sorted(os.listdir(msg_dir)):
    cid = fn[:-5]
    try:
        d = json.load(open(os.path.join(msg_dir, fn)))
    except Exception as e:
        stats['parse_error'] += 1
        continue
    dd = d.get('data', d)
    ms = dd.get('messages', []) or []
    if ms:
        chat_with_msg += 1
    for m in ms:
        m['_chat_id'] = cid
        all_msgs.append(m)
        stats['total'] += 1
        stats['type:' + str(m.get('msg_type'))] += 1
        s = m.get('sender') or {}
        stats['sender_type:' + str(s.get('sender_type'))] += 1
        if m.get('deleted'):
            stats['deleted'] += 1
        if dd.get('has_more'):
            pass

print('chats scanned:', len(os.listdir(msg_dir)), 'chats with msgs:', chat_with_msg)
for k, v in stats.most_common(40):
    print(' ', k, v)

kept = []
dropped = collections.Counter()
for m in all_msgs:
    s = m.get('sender') or {}
    if m.get('msg_type') == 'system':
        dropped['system'] += 1
        continue
    if m.get('deleted'):
        dropped['deleted'] += 1
        continue
    if s.get('sender_type') != 'user':
        dropped['bot_sender:' + str(s.get('name'))] += 1
        continue
    content = (m.get('content') or '').strip()
    if not content:
        dropped['empty_content'] += 1
        continue
    kept.append(m)

print('\nkept:', len(kept))
print('dropped:')
for k, v in dropped.most_common(20):
    print(' ', k, v)

kc = collections.Counter((meta.get(m['_chat_id'], {}).get('name'), meta.get(m['_chat_id'], {}).get('mode')) for m in kept)
print('\ntop chats by kept msgs:')
for (name, mode), c in kc.most_common(25):
    print(f'  {c:5d}  {mode:5s}  {name}')
print('\ndistinct chats with kept msgs:', len(kc))
senders = collections.Counter((m.get('sender') or {}).get('name') for m in kept)
print('distinct senders:', len(senders))
print(senders.most_common(20))

json.dump(kept, open('/tmp/kept_msgs.json', 'w'), ensure_ascii=False)
