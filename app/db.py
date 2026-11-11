import sqlite3

from app.rag.seed import SEED_DOCS

PREFIX = "sqlite:///"


def db_path(database_url: str) -> str:
    if not database_url.startswith(PREFIX):
        raise ValueError("Only sqlite:/// database URLs are supported")
    return database_url[len(PREFIX):]


def connect(database_url: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path(database_url))


def init_db(conn: sqlite3.Connection) -> None:
    """Table illaati create pannum. Table empty ah irundha sample docs serkkum."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS documents ("
        "id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL)"
    )
    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO documents (title, content) VALUES (?, ?)", SEED_DOCS
        )
    conn.commit()
