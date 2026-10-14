import json

rows = json.load(open('messages_clean.json', encoding='utf-8'))
TYPE_MAP = {'group': '群聊', 'p2p': '单聊', 'topic': '群聊'}

MAXLEN = 8000
recs = []
for r in rows:
    content = r['content'] or ''
    if len(content) > MAXLEN:
        content = content[:MAXLEN] + '…(内容过长已截断)'
    rec = {
        '会话ID': r['chat_id'],
        '会话名称': r['chat_name'],
        '会话类型': TYPE_MAP.get(r['chat_type'], r['chat_type']),
        '消息ID': r['message_id'],
        '消息类型': r['msg_type'],
        '发送人': r['sender_name'],
        '发送人ID': r['sender_id'],
        '消息内容': content,
        '发送时间': r['create_time'],
    }
    if r['thread_id']:
        rec['话题ID'] = r['thread_id']
    recs.append(rec)

print('total', len(recs))
B = 200
for i in range(0, len(recs), B):
    batch = recs[i:i + B]
    fn = 'msg_batch_%d.json' % (i // B)
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump({'create_records': batch}, f, ensure_ascii=False)
    print(fn, len(batch))
