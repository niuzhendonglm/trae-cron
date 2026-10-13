import json, collections, re

valid = json.load(open('/workspace/lark_daily/valid.json'))
CHATS = {c['chat_id']: c for c in json.load(open('/workspace/lark_daily/chats_all.json'))['data']['chats']}
by_id = {m['message_id']: m for m in valid}

def clean(t):
    if not t:
        return ''
    t = t.replace('\r', ' ')
    t = re.sub(r'\n+', ' ⏎ ', t)
    t = re.sub(r'<card>.*?</card>', lambda m: '[CARD]' + m.group(0)[6:-7][:600], t, flags=re.S)
    return t.strip()

order = collections.defaultdict(list)
for m in valid:
    order[m['_chat_id']].append(m)

# sort chats by message count desc
chats_sorted = sorted(order.items(), key=lambda kv: -len(kv[1]))

lines = []
for cid, msgs in chats_sorted:
    name = CHATS.get(cid, {}).get('name') or cid
    mode = CHATS.get(cid, {}).get('chat_mode')
    lines.append('===== CHAT: %s | %s | %s | msgs=%d =====' % (name, mode, cid, len(msgs)))
    msgs.sort(key=lambda m: (m.get('create_time') or '', m.get('message_id')))
    for i, m in enumerate(msgs):
        s = (m.get('sender') or {}).get('name') or (m.get('sender') or {}).get('id')
        t = m.get('create_time')
        mt = m.get('msg_type')
        c = clean(m.get('content'))
        if len(c) > 400:
            c = c[:400] + '…[TRUNC]'
        extra = []
        if m.get('thread_id'):
            extra.append('thread=' + m['thread_id'])
        if m.get('_is_thread_reply'):
            extra.append('reply_in_thread->' + str(m.get('_parent_message_id')))
        if m.get('reply_to'):
            p = by_id.get(m['reply_to'])
            extra.append('quote->' + (('%s:%s' % (((p.get('sender') or {}).get('name')), clean(p.get('content'))[:60])) if p else m['reply_to']))
        lines.append('[%s|%s] %s <%s> %s%s' % (t[11:] if t and len(t) > 11 else t, i, s, mt, c, ('  {' + ', '.join(extra) + '}') if extra else ''))
    lines.append('')

open('/workspace/lark_daily/transcript.txt', 'w').write('\n'.join(lines))
print('lines', len(lines))
print('chars', sum(len(x) for x in lines))
