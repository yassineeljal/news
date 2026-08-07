import sqlite3
from contextlib import contextmanager

import config


@contextmanager
def _connect():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_articles (
                url TEXT PRIMARY KEY,
                seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def is_seen(url: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_articles WHERE url = ?", (url,)
        ).fetchone()
        return row is not None


def mark_seen(url: str) -> None:
    with _connect() as conn:
        conn.execute("INSERT OR IGNORE INTO seen_articles (url) VALUES (?)", (url,))
