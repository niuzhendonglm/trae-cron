import json, glob, os, collections

files = sorted(glob.glob('/workspace/lark_daily/msgs/*.json'))
CHATS = {c['chat_id']: c for c in json.load(open('/workspace/lark_daily/chats_all.json'))['data']['chats']}

flat = []
seen = set()

def add(m, parent_thread=None):
    mid = m.get('message_id')
    key = (m.get('chat_id') or m.get('_chat_id'), mid)
    if key in seen:
        return
    seen.add(key)
    mm = dict(m)
    mm['_chat_id'] = m.get('chat_id') or m.get('_chat_id')
    flat.append(mm)
    for r in (m.get('thread_replies') or []):
        r2 = dict(r)
        r2.setdefault('chat_id', mm['_chat_id'])
        r2['_is_thread_reply'] = True
        r2['_parent_message_id'] = mid
        add(r2)

for p in files:
    cid = os.path.basename(p)[:-5]
    try:
        d = json.load(open(p))
    except Exception:
        continue
    if not d.get('ok'):
        continue
    for m in (d.get('data', {}).get('messages') or []):
        m.setdefault('chat_id', cid)
        add(m)

flat.sort(key=lambda m: (m['_chat_id'], m.get('create_time') or '', m.get('message_id')))
print('flattened total', len(flat))
print('msg_type', collections.Counter(m.get('msg_type') for m in flat))
print('sender_type', collections.Counter((m.get('sender') or {}).get('sender_type') for m in flat))
print('deleted', sum(1 for m in flat if m.get('deleted')))
print('thread_reply', sum(1 for m in flat if m.get('_is_thread_reply')))

# per chat stats
per = collections.defaultdict(lambda: collections.Counter())
for m in flat:
    cid = m['_chat_id']
    per[cid]['all'] += 1
    if m.get('msg_type') == 'system':
        per[cid]['system'] += 1
    elif m.get('deleted'):
        per[cid]['deleted'] += 1
    elif (m.get('sender') or {}).get('sender_type') != 'user':
        per[cid]['bot'] += 1
    else:
        per[cid]['user'] += 1

rows = []
for cid, c in per.items():
    ch = CHATS.get(cid, {})
    rows.append((c['all'], c['user'], c['bot'], c['system'], c['deleted'], ch.get('chat_mode'), ch.get('name'), cid))
rows.sort(reverse=True)
print('%-4s %-4s %-4s %-4s %-4s %-6s %s' % ('all', 'usr', 'bot', 'sys', 'del', 'mode', 'name'))
for r in rows:
    print('%-4d %-4d %-4d %-4d %-4d %-6s %s | %s' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

json.dump(flat, open('/workspace/lark_daily/flat.json', 'w'), ensure_ascii=False)
