from __future__ import annotations
from pathlib import Path
from platformdirs import user_data_dir
import sqlite3
import time

APP_NAME = "caas"

def db_path() -> Path:
    d = Path(user_data_dir(APP_NAME))
    d.mkdir(parents=True, exist_ok=True)
    return d / "memory.sqlite3"

def init_db() -> None:
    con = sqlite3.connect(db_path())
    try:
        con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          created_at REAL NOT NULL
        )
        """)
        con.commit()
    finally:
        con.close()

def add_message(session_id: str, role: str, content: str) -> None:
    con = sqlite3.connect(db_path())
    try:
        con.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES(?,?,?,?)",
            (session_id, role, content, time.time())
        )
        con.commit()
    finally:
        con.close()

def get_recent(session_id: str, limit: int = 30) -> list[tuple[str, str]]:
    con = sqlite3.connect(db_path())
    try:
        cur = con.execute(
            "SELECT role, content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cur.fetchall()
        rows.reverse()
        return [(r[0], r[1]) for r in rows]
    finally:
        con.close()
