import json, os, re, collections, html

DAY = '2026-10-26'
rows_meta = {r['chat_id']: r for r in json.load(open('/tmp/chats_flat.json'))}
TYPE_CN = {'group': '群聊', 'p2p': '单聊', 'topic': '话题群'}

def clean(text):
    if text is None:
        return ''
    t = text
    t = re.sub(r'</?p>', '', t)
    t = re.sub(r'<at[^>]*>', '', t)
    t = t.replace('</at>', '')
    t = html.unescape(t)
    t = re.sub(r'\s*\n\s*', ' ', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return t

def to_iso(ct):
    ct = (ct or '').strip()
    if len(ct) == 16:
        ct += ':00'
    return ct.replace(' ', 'T') + '+08:00'

pool = {}   # message_id -> dict
src_count = collections.Counter()

def add(m, chat_id, chat_name, chat_type, thread_id, origin):
    s = m.get('sender') or {}
    if m.get('msg_type') == 'system' or m.get('deleted'):
        return
    if s.get('sender_type') not in ('user', 'anonymous'):
        return
    text = clean(m.get('content'))
    if not text:
        return
    ct = (m.get('create_time') or '').strip()
    if not ct.startswith(DAY):
        return
    mid = m.get('message_id')
    if not mid:
        return
    src_count[origin] += 1
    if mid in pool:
        rec = pool[mid]
        for k, v in (('chat_name', chat_name), ('thread_id', thread_id), ('chat_type', chat_type), ('chat_id', chat_id)):
            if not rec.get(k) and v:
                rec[k] = v
        rec['origin'] = rec['origin'] + '+' + origin if origin not in rec['origin'] else rec['origin']
        return
    pool[mid] = {
        'message_id': mid, 'chat_id': chat_id or m.get('chat_id') or '',
        'chat_name': chat_name or m.get('chat_name') or '',
        'chat_type': chat_type or m.get('chat_type') or '',
        'msg_type': m.get('msg_type') or '', 'thread_id': thread_id or m.get('thread_id') or '',
        'sender_name': s.get('name') or '', 'sender_id': s.get('id') or '',
        'sender_type': s.get('sender_type') or '', 'create_time': ct,
        'text': text, 'mentions': m.get('mentions') or [], 'origin': origin,
    }

# source 1: per-chat message list
for fn in sorted(os.listdir('/workspace/lark_daily/msgs')):
    cid = fn[:-5]
    meta = rows_meta.get(cid, {})
    d = json.load(open('/workspace/lark_daily/msgs/' + fn)); dd = d.get('data', d)
    for m in dd.get('messages', []) or []:
        add(m, cid, meta.get('name'), TYPE_CN.get(meta.get('mode'), meta.get('mode')), m.get('thread_id'), 'chat')

# source 2: expanded threads
for fn in sorted(os.listdir('/workspace/lark_daily/threads')):
    tid = fn[:-5]
    d = json.load(open('/workspace/lark_daily/threads/' + fn)); dd = d.get('data', d)
    cid = dd.get('chat_id') or ''
    for m in dd.get('messages', []) or []:
        cid2 = m.get('chat_id') or cid
        meta = rows_meta.get(cid2, {})
        add(m, cid2, m.get('chat_name') or meta.get('name'), TYPE_CN.get(meta.get('mode'), meta.get('mode')), m.get('thread_id') or tid, 'thread')

# source 3: global search
d = json.load(open('/tmp/search_all.json')); dd = d.get('data', d)
for m in dd.get('messages', []) or []:
    cid = m.get('chat_id') or ''
    meta = rows_meta.get(cid, {})
    cname = m.get('chat_name') or meta.get('name') or ''
    ctype = TYPE_CN.get(m.get('chat_type') or meta.get('mode'), m.get('chat_type') or meta.get('mode') or '')
    add(m, cid, cname, ctype, m.get('thread_id'), 'search')

recs = sorted(pool.values(), key=lambda r: (r['chat_id'], r['create_time'], r['message_id']))
print('source contributions:', dict(src_count))
print('unique merged:', len(recs), 'chats:', len(set(r['chat_id'] for r in recs)))
print('missing chat_name:', sum(1 for r in recs if not r['chat_name']))
print('missing sender:', sum(1 for r in recs if not r['sender_name']))
print('by chat type:', collections.Counter(r['chat_type'] for r in recs))
print('by msg type:', collections.Counter(r['msg_type'] for r in recs).most_common())
print('origin mix:', collections.Counter(r['origin'] for r in recs).most_common())

json.dump(recs, open('/tmp/merged_msgs.json', 'w'), ensure_ascii=False)

raw_rows = [{'fields': {
    '会话ID': r['chat_id'], '会话名称': r['chat_name'], '会话类型': r['chat_type'],
    '消息ID': r['message_id'], '消息类型': r['msg_type'], '话题ID': r['thread_id'],
    '发送人': r['sender_name'], '发送人ID': r['sender_id'],
    '消息内容': (r['text'][:1500] + '…') if len(r['text']) > 1500 else r['text'],
    '发送时间': to_iso(r['create_time']),
}} for r in recs]
json.dump(raw_rows, open('/tmp/raw_rows.json', 'w'), ensure_ascii=False)
print('raw rows:', len(raw_rows))

# per-chat conversation dump for QA building
conv = collections.defaultdict(list)
for r in recs:
    conv[r['chat_id']].append(r)
out = {}
for cid, ms in conv.items():
    out[cid] = {'name': ms[0]['chat_name'], 'type': ms[0]['chat_type'],
                'messages': [{'t': m['create_time'], 'who': m['sender_name'], 'id': m['message_id'],
                              'type': m['msg_type'], 'thread': m['thread_id'], 'text': m['text']} for m in ms]}
json.dump(out, open('/tmp/conversations.json', 'w'), ensure_ascii=False, indent=1)
print('conversations:', len(out))
for cid, v in sorted(out.items(), key=lambda kv: -len(kv[1]['messages']))[:12]:
    print(f"  {len(v['messages']):4d} {v['type']:4s} {v['name'][:50]}")
