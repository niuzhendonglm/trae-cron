import json, collections, re

flat = json.load(open('/workspace/lark_daily/flat.json'))
CHATS = {c['chat_id']: c for c in json.load(open('/workspace/lark_daily/chats_all.json'))['data']['chats']}

Q_MARKS = ['?', '？']
Q_WORDS = ['吗', '怎么', '怎样', '如何', '为什么', '为啥', '能否', '能不能', '是否', '有没有', '有木有',
           '什么时候', '啥时候', '谁知道', '请问', '请教', '求助', '帮忙看', '帮看', '麻烦看', '哪位',
           '有人知道', '谁知道', '求解', '咋办', '怎么办', '咋整', '是不是', '可不可以', '行不行',
           '谁知道', '谁有', '哪里', '哪个', '多少', '什么原因', '什么问题', '了解', '咨询']

def is_question(text):
    if not text:
        return False
    t = text.strip()
    if any(m in t for m in Q_MARKS):
        return True
    hits = sum(1 for w in Q_WORDS if w in t)
    return hits >= 1 and len(t) < 400

valid = []
for m in flat:
    if m.get('msg_type') == 'system':
        continue
    if m.get('deleted'):
        continue
    s = m.get('sender') or {}
    if s.get('sender_type') != 'user':
        continue
    valid.append(m)

valid.sort(key=lambda m: (m['_chat_id'], m.get('create_time') or '', m.get('message_id')))
print('valid user messages', len(valid))
print('types', collections.Counter(m.get('msg_type') for m in valid))

qs = [m for m in valid if is_question(m.get('content') or '')]
print('question-like', len(qs))
print('by chat:')
c = collections.Counter((CHATS.get(m['_chat_id'], {}).get('name'), m['_chat_id']) for m in qs)
for (name, cid), n in c.most_common():
    print('  ', n, name, cid)

json.dump(valid, open('/workspace/lark_daily/valid.json', 'w'), ensure_ascii=False)
