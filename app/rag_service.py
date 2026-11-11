from contextlib import closing

from app.config import get_settings
from app.db import connect, init_db
from app.rag.core import ask


def answer_question(question: str) -> dict:
    # Ovvoru request ku thani DB connection. Mudinjadhum close aagum.
    with closing(connect(get_settings().database_url)) as conn:
        init_db(conn)
        return ask(conn, question)
