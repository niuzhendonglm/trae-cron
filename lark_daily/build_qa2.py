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
    s = re.sub(r'\[Image:[^\]]*\]', '[图片]', s)
    s = s.replace('<card>', '').replace('</card>', '')
    s = re.sub(r'<file[^>]*name="([^"]*)"[^>]*>', r'[文件:\1]', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def strip_media(t):
    t = t.replace("[图片]", "")
    t = re.sub(r'\[文件:[^\]]*\]', '', t)
    t = re.sub(r'\[Image:[^\]]*\]', '', t)
    return t.strip()

def core_len(t):
    c = re.sub(r'[？?。.！!，,、~～\s:：;；"\'""]', '', t)
    c = strip_media(c)
    return len(c)

FILLER = {"好的","好","嗯","收到","ok","OK","Ok","1","赞","行","可以","对","是的","嗯嗯",
          "哈哈","哈哈哈","？","?","。。。","...","在","在的","早","早上好","谢谢","感谢","👍"}
REF_WORDS = ["你指","上面","下面","刚才","如上","如图","这个意思","那个意思"]
BOT_MARK = ["（由豆包发送）","叮咚～","别忘了顺手签","签到提醒","由豆包发送"]

def q_ok(text):
    t = text.strip()
    if any(b in t for b in BOT_MARK): return False
    if core_len(t) < 3: return False
    if strip_media(t) == "" : return False
    return True

def a_ok(text, src):
    t = text.strip()
    if not t: return False
    if strip_media(t) == "": return False           # pure image/file
    if t in FILLER: return False
    if core_len(t) < (5 if src == "lookahead" else 2): return False
    if src == "lookahead" and re.fullmatch(r'[？?。.！!~～\s]+', t): return False
    return True

Q_WORDS = ["吗","怎么","如何","为什么","为何","请问","请教","求助","能不能","可不可以","是不是",
           "哪个","哪里","什么原因","有没有","怎样","咋","求教","问下","问一下","咨询","是否",
           "行不行","要不要","多少","什么时候","为啥","能否","可否","谁知道","啥"]

def self_contained(text):
    t = text.strip()
    if len(t) < 8: return False
    if any(w in t for w in REF_WORDS): return False
    has_q = ("？" in t or "?" in t or any(w in t for w in Q_WORDS))
    return has_q

def to_iso(ct):
    d, t = ct.split(" ")
    if len(t) == 5: t += ":00"
    return f"{d}T{t}+08:00"

by_id = {m.get("message_id"): m for m in v}
chats = collections.defaultdict(list)
for m in v: chats[m.get("chat_id")].append(m)
for c in chats: chats[c].sort(key=lambda m: m.get("create_time") or "")

thread_children = collections.defaultdict(list)
reply_children = collections.defaultdict(list)
for m in v:
    if m.get("_parent_message_id"): thread_children[m["_parent_message_id"]].append(m)
    if m.get("reply_to"): reply_children[m["reply_to"]].append(m)

def is_question(m):
    c = m.get("content") or ""
    mid = m.get("message_id")
    if mid in thread_children or mid in reply_children: return True
    if "？" in c or "?" in c: return True
    if any(w in c for w in Q_WORDS): return True
    return False

def sname(m): return (m.get("sender") or {}).get("name") or ""
def sid(m): return (m.get("sender") or {}).get("id") or ""

kept_human, kept_ai, dropped = [], [], []
used = set()

for cid, msgs in chats.items():
    for idx, m in enumerate(msgs):
        if not is_question(m): continue
        mid = m.get("message_id")
        asker, asker_id, qtime = sname(m), sid(m), m.get("create_time")
        qtext = clean(m.get("content"))
        if not q_ok(qtext):
            dropped.append((cid, qtext[:40], "q_low")); continue
        ans, src = [], "none"
        for ch in thread_children.get(mid, []):
            if sid(ch) != asker_id and ch.get("message_id") not in used: ans.append(ch)
        if ans: src = "thread"
        for ch in reply_children.get(mid, []):
            if sid(ch) != asker_id and ch.get("message_id") not in used and ch not in ans: ans.append(ch)
        if ans and src == "none": src = "reply"
        if not ans:
            for j in range(idx+1, min(idx+6, len(msgs))):
                nm = msgs[j]
                if sid(nm) == asker_id or nm.get("message_id") in used: continue
                try:
                    t1 = datetime.strptime(qtime, "%Y-%m-%d %H:%M")
                    t2 = datetime.strptime(nm.get("create_time"), "%Y-%m-%d %H:%M")
                    if (t2-t1).total_seconds() > 2400: break
                except: pass
                if not clean(nm.get("content")): continue
                ans.append(nm); src = "lookahead"; break
        # filter answers by quality
        good = [a for a in ans if a_ok(clean(a.get("content")), src)]
        rec_base = {"chat_id": cid, "chat_name": cname.get(cid,""), "chat_mode": cmode.get(cid,""),
                    "q_msg_id": mid, "question": qtext, "asker": asker, "asker_id": asker_id,
                    "qtime": qtime, "q_iso": to_iso(qtime), "msg_type": m.get("msg_type"),
                    "answer_source": src}
        if good:
            good = good[:3]
            answer = "\n".join(clean(a.get("content")) for a in good)
            answerer = "、".join(dict.fromkeys(sname(a) for a in good if sname(a)))
            for a in good: used.add(a.get("message_id"))
            rec = dict(rec_base, answer=answer, answerer=answerer, human_answered=True)
            kept_human.append(rec)
        else:
            if self_contained(qtext):
                rec = dict(rec_base, answer="", answerer="", human_answered=False)
                kept_ai.append(rec)
            else:
                dropped.append((cid, qtext[:40], "no_ans_not_selfcontained"))

print("kept_human:", len(kept_human))
print("kept_ai (need AI answer):", len(kept_ai))
print("dropped:", len(dropped), collections.Counter(d[2] for d in dropped))
print("kept_human by source:", collections.Counter(r["answer_source"] for r in kept_human))
json.dump({"kept_human": kept_human, "kept_ai": kept_ai,
           "dropped": [{"chat_id":d[0],"q":d[1],"reason":d[2]} for d in dropped]},
          open("qa_curated.json","w"), ensure_ascii=False, indent=1)
print("\n--- kept_ai questions (to answer) ---")
for i,r in enumerate(kept_ai):
    print(f"{i}. [{r['chat_name'][:16]}] {r['asker']}: {r['question'][:120]}")
