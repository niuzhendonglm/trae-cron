import json, re, collections
from datetime import datetime

v = json.load(open("valid_strict.json"))
chats_meta = json.load(open("chats_all.json"))["data"]["chats"]
cname = {c["chat_id"]: (c.get("name") or "") for c in chats_meta}
cmode = {c["chat_id"]: (c.get("chat_mode") or "") for c in chats_meta}

def clean(s):
    if not s: return ""
    s = re.sub(r'<at user_id="all"\s*>(.*?)</at>', '@所有人', s)
    s = re.sub(r'<at user_id="all"\s*/>', '@所有人', s)
    s = re.sub(r'<at user_id="([^"]*)"\s*>(.*?)</at>', lambda m: '@'+(m.group(2) or ''), s)
    s = re.sub(r'<at user_id="([^"]*)"\s*/>', '', s)
    s = re.sub(r'!\[Image\]\([^)]*\)', '[图片]', s)
    s = s.replace('<card>', '').replace('</card>', '')
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def to_iso(ct):
    d, t = ct.split(" ")
    if len(t) == 5: t += ":00"
    return f"{d}T{t}+08:00"

# index
by_id = {}
for m in v:
    by_id[m.get("message_id")] = m

# per-chat ordered
chats = collections.defaultdict(list)
for m in v:
    chats[m.get("chat_id")].append(m)
for c in chats: chats[c].sort(key=lambda m: m.get("create_time") or "")

# children maps
thread_children = collections.defaultdict(list)  # parent_id -> [msgs]
reply_children = collections.defaultdict(list)   # reply_to id -> [msgs]
for m in v:
    p = m.get("_parent_message_id")
    if p: thread_children[p].append(m)
    r = m.get("reply_to")
    if r: reply_children[r].append(m)

Q_WORDS = ["吗","怎么","如何","为什么","为何","请问","请教","求助","能不能","可不可以","是不是",
           "哪个","哪里","什么原因","有没有","怎样","咋","求教","问下","问一下","咨询","是否",
           "行不行","要不要","多少","几个","什么时候","为啥","能否","可否","有谁知道","谁知道"]

def is_question(m):
    c = m.get("content") or ""
    mid = m.get("message_id")
    if mid in thread_children or mid in reply_children:
        return True
    if "？" in c or "?" in c:
        return True
    if any(w in c for w in Q_WORDS):
        return True
    return False

def sender_name(m):
    return (m.get("sender") or {}).get("name") or ""

def sender_id(m):
    return (m.get("sender") or {}).get("id") or ""

# Build candidate QA pairs
candidates = []
used_as_answer = set()

for cid, msgs in chats.items():
    for idx, m in enumerate(msgs):
        if not is_question(m):
            continue
        mid = m.get("message_id")
        asker = sender_name(m)
        asker_id = sender_id(m)
        qtime = m.get("create_time")
        qtext = clean(m.get("content"))
        # gather answers
        ans_msgs = []
        src = "none"
        # 1 thread children
        for ch in thread_children.get(mid, []):
            if sender_id(ch) != asker_id and ch.get("message_id") not in used_as_answer:
                ans_msgs.append(ch)
        if ans_msgs: src = "thread"
        # 2 reply children
        for ch in reply_children.get(mid, []):
            if sender_id(ch) != asker_id and ch.get("message_id") not in used_as_answer and ch not in ans_msgs:
                ans_msgs.append(ch)
        if ans_msgs and src == "none": src = "reply"
        # 3 lookahead: next msgs by different sender within 5 msgs / 40 min, not a question itself
        if not ans_msgs:
            for j in range(idx+1, min(idx+6, len(msgs))):
                nm = msgs[j]
                if sender_id(nm) == asker_id: continue
                if nm.get("message_id") in used_as_answer: continue
                # time window
                try:
                    t1 = datetime.strptime(qtime, "%Y-%m-%d %H:%M")
                    t2 = datetime.strptime(nm.get("create_time"), "%Y-%m-%d %H:%M")
                    if (t2-t1).total_seconds() > 2400: break
                except: pass
                ntext = clean(nm.get("content"))
                if not ntext: continue
                ans_msgs.append(nm)
                src = "lookahead"
                break
        ans_msgs = ans_msgs[:3]
        if ans_msgs:
            answer = "\n".join(clean(a.get("content")) for a in ans_msgs if clean(a.get("content")))
            answerer = "、".join(dict.fromkeys(sender_name(a) for a in ans_msgs if sender_name(a)))
            for a in ans_msgs: used_as_answer.add(a.get("message_id"))
            human = True
        else:
            answer = ""
            answerer = ""
            human = False
        candidates.append({
            "chat_id": cid, "chat_name": cname.get(cid,""), "chat_mode": cmode.get(cid,""),
            "q_msg_id": mid,
            "question": qtext, "asker": asker, "asker_id": asker_id,
            "qtime": qtime, "q_iso": to_iso(qtime),
            "answer": answer, "answerer": answerer, "human_answered": human,
            "answer_source": src, "msg_type": m.get("msg_type"),
        })

print("candidate questions:", len(candidates))
print("human answered:", sum(1 for c in candidates if c["human_answered"]))
print("unanswered:", sum(1 for c in candidates if not c["human_answered"]))
print("answer_source:", collections.Counter(c["answer_source"] for c in candidates))
print("by chat_mode:", collections.Counter(c["chat_mode"] for c in candidates))
print("by chat:", collections.Counter(c["chat_name"] for c in candidates).most_common(15))
json.dump(candidates, open("qa_candidates.json","w"), ensure_ascii=False, indent=1)
