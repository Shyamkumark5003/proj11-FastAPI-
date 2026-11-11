import re
import sqlite3

STOPWORDS = {
    "what", "the", "how", "does", "do", "did", "why", "when", "can", "are",
    "was", "were", "this", "that", "with", "for", "and", "from", "about",
    "tell", "me", "you", "your", "its", "his", "her", "our", "who", "which",
}

NO_ANSWER = "I could not find an answer in the documents."


def tokens(text: str) -> set[str]:
    out = set()
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word in STOPWORDS:
            continue
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]  # logs -> log, settings -> setting
        if len(word) > 2:
            out.add(word)
    return out


def ask(conn: sqlite3.Connection, question: str) -> dict:
    q_tokens = tokens(question)
    rows = conn.execute("SELECT id, title, content FROM documents").fetchall()

    scored = []
    for doc_id, title, content in rows:
        score = len(q_tokens & tokens(title + " " + content))
        if score > 0:
            scored.append((score, doc_id, title, content))

    if not scored:
        return {"answer": NO_ANSWER, "sources": []}

    # score athigam first; same score na id kuraiya first
    scored.sort(key=lambda s: (-s[0], s[1]))
    top = scored[:2]
    return {"answer": top[0][3], "sources": [t[2] for t in top]}
