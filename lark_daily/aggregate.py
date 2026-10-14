import json, glob, os
from datetime import datetime, timedelta, timezone

CN = timezone(timedelta(hours=8))
DAY_START = datetime(2026, 10, 13, 0, 0, 0, tzinfo=CN)
DAY_END = datetime(2026, 10, 13, 23, 59, 59, tzinfo=CN)

chats = {c['chat_id']: c for c in json.load(open('chats_list.json', encoding='utf-8'))}


def parse_ct(s):
    s = (s or '').strip()
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).astimezone(CN)
        except ValueError:
            continue
    raise ValueError(s)


rows = []
stats = {'files': 0, 'bad': 0, 'raw': 0, 'system': 0, 'app': 0, 'deleted': 0, 'out_of_range': 0, 'kept': 0}

for fp in sorted(glob.glob('msgs/*.json')):
    stats['files'] += 1
    cid = os.path.basename(fp)[:-5]
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        stats['bad'] += 1
        continue
    if not d.get('ok'):
        stats['bad'] += 1
        continue
    chat = chats.get(cid, {})
    chat_name = chat.get('name') or cid
    chat_mode = chat.get('chat_mode') or 'group'

    def handle(m, is_reply, root_thread):
        stats['raw'] += 1
        mt = m.get('msg_type')
        s = m.get('sender') or {}
        st = s.get('sender_type') or ''
        if m.get('deleted'):
            stats['deleted'] += 1
            return
        if mt == 'system' or not st:
            stats['system'] += 1
            return
        if st != 'user':
            stats['app'] += 1
            return
        try:
            dt = parse_ct(m['create_time'])
        except Exception:
            return
        if dt < DAY_START or dt > DAY_END:
            stats['out_of_range'] += 1
            return
        stats['kept'] += 1
        rows.append({
            'chat_id': cid,
            'chat_name': chat_name,
            'chat_type': chat_mode,
            'message_id': m.get('message_id'),
            'msg_type': mt,
            'thread_id': m.get('thread_id') or root_thread or '',
            'sender_name': s.get('name') or s.get('id') or '',
            'sender_id': s.get('id') or '',
            'content': m.get('content') or '',
            'create_time': dt,
            'is_reply': is_reply,
            'reply_to': (m.get('reply_to') or {}).get('message_id', '') if isinstance(m.get('reply_to'), dict) else '',
            'mentions': [{'id': x.get('id'), 'name': x.get('name')} for x in (m.get('mentions') or [])],
        })

    for m in d.get('data', {}).get('messages', []):
        handle(m, False, m.get('thread_id') or '')
        tid = m.get('thread_id') or ''
        for r in (m.get('thread_replies') or []):
            handle(r, True, tid)

rows.sort(key=lambda r: (r['chat_id'], r['create_time'], r['message_id'] or ''))
seen = set()
dedup = []
for r in rows:
    if r['message_id'] in seen:
        continue
    seen.add(r['message_id'])
    dedup.append(r)

print('stats', stats)
print('kept_after_dedup', len(dedup))
by_chat = {}
for r in dedup:
    by_chat.setdefault((r['chat_id'], r['chat_name'], r['chat_type']), 0)
    by_chat[(r['chat_id'], r['chat_name'], r['chat_type'])] += 1
print('active_chats', len(by_chat))
for k, v in sorted(by_chat.items(), key=lambda x: -x[1]):
    print(v, '|', k[2], '|', k[1], '|', k[0])

with open('messages_clean.json', 'w', encoding='utf-8') as f:
    json.dump([{**r, 'create_time': r['create_time'].isoformat()} for r in dedup], f, ensure_ascii=False, indent=1)
