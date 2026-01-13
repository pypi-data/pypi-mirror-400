# src/caas/memory.py
from __future__ import annotations
from pathlib import Path
from platformdirs import user_data_dir
import sqlite3
import time
from typing import Optional, Any

APP_NAME = "caas"

def db_path() -> Path:
    d = Path(user_data_dir(APP_NAME))
    d.mkdir(parents=True, exist_ok=True)
    return d / "memory.sqlite3"

def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(db_path())
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

def init_db() -> None:
    con = _connect()
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

        # --- Trades captured from signatures ---
        con.execute("""
        CREATE TABLE IF NOT EXISTS trades (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          wallet_pubkey TEXT NOT NULL,
          mint TEXT NOT NULL,
          side TEXT NOT NULL,                 -- "buy" | "sell"
          signature TEXT NOT NULL UNIQUE,
          status TEXT NOT NULL,               -- "pending" | "confirmed" | "failed"
          slot INTEGER,
          block_time INTEGER,
          sol_delta REAL,                     -- signed SOL change for wallet (post - pre) in SOL
          fee_lamports INTEGER,
          token_delta REAL,                   -- signed token change for wallet (post - pre) in UI units
          usd_value REAL,                     -- buy: cost (positive), sell: proceeds (positive)
          error TEXT,
          created_at REAL NOT NULL,
          updated_at REAL NOT NULL
        )
        """)

        # --- Simple position tracking (avg-cost) ---
        con.execute("""
        CREATE TABLE IF NOT EXISTS positions (
          wallet_pubkey TEXT NOT NULL,
          mint TEXT NOT NULL,
          qty REAL NOT NULL,                  -- UI units
          cost_usd REAL NOT NULL,             -- remaining cost basis for open qty (avg-cost method)
          realized_pnl_usd REAL NOT NULL,
          updated_at REAL NOT NULL,
          PRIMARY KEY (wallet_pubkey, mint)
        )
        """)

        con.commit()
    finally:
        con.close()

def add_message(session_id: str, role: str, content: str) -> None:
    con = _connect()
    try:
        con.execute(
            "INSERT INTO messages(session_id, role, content, created_at) VALUES(?,?,?,?)",
            (session_id, role, content, time.time())
        )
        con.commit()
    finally:
        con.close()

def get_recent(session_id: str, limit: int = 30) -> list[tuple[str, str]]:
    con = _connect()
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

# -------------------------------
# Trades / Positions helpers
# -------------------------------

def insert_pending_trade(wallet_pubkey: str, mint: str, side: str, signature: str) -> None:
    now = time.time()
    con = _connect()
    try:
        con.execute(
            """
            INSERT OR IGNORE INTO trades(wallet_pubkey,mint,side,signature,status,created_at,updated_at)
            VALUES(?,?,?,?, "pending", ?, ?)
            """,
            (wallet_pubkey, mint, side, signature, now, now),
        )
        con.commit()
    finally:
        con.close()

def update_trade(signature: str, **fields: Any) -> None:
    if not fields:
        return
    fields["updated_at"] = time.time()
    cols = ", ".join([f"{k}=?" for k in fields.keys()])
    vals = list(fields.values())

    con = _connect()
    try:
        con.execute(f"UPDATE trades SET {cols} WHERE signature=?", (*vals, signature))
        con.commit()
    finally:
        con.close()

def get_pending_trades(wallet_pubkey: str, max_age_seconds: int = 3600, limit: int = 10) -> list[dict]:
    cutoff = time.time() - max_age_seconds
    con = _connect()
    try:
        cur = con.execute(
            """
            SELECT wallet_pubkey, mint, side, signature, created_at
            FROM trades
            WHERE wallet_pubkey=? AND status="pending" AND created_at >= ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (wallet_pubkey, cutoff, limit),
        )
        out = []
        for row in cur.fetchall():
            out.append(
                {
                    "wallet_pubkey": row[0],
                    "mint": row[1],
                    "side": row[2],
                    "signature": row[3],
                    "created_at": row[4],
                }
            )
        return out
    finally:
        con.close()

def get_position(wallet_pubkey: str, mint: str) -> Optional[dict]:
    con = _connect()
    try:
        cur = con.execute(
            "SELECT qty, cost_usd, realized_pnl_usd, updated_at FROM positions WHERE wallet_pubkey=? AND mint=?",
            (wallet_pubkey, mint),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"qty": float(row[0]), "cost_usd": float(row[1]), "realized_pnl_usd": float(row[2]), "updated_at": float(row[3])}
    finally:
        con.close()

def upsert_position(wallet_pubkey: str, mint: str, qty: float, cost_usd: float, realized_pnl_usd: float) -> None:
    now = time.time()
    con = _connect()
    try:
        con.execute(
            """
            INSERT INTO positions(wallet_pubkey,mint,qty,cost_usd,realized_pnl_usd,updated_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(wallet_pubkey,mint)
            DO UPDATE SET qty=excluded.qty, cost_usd=excluded.cost_usd,
                         realized_pnl_usd=excluded.realized_pnl_usd, updated_at=excluded.updated_at
            """,
            (wallet_pubkey, mint, float(qty), float(cost_usd), float(realized_pnl_usd), now),
        )
        con.commit()
    finally:
        con.close()

def list_positions(wallet_pubkey: str) -> list[dict]:
    con = _connect()
    try:
        cur = con.execute(
            "SELECT mint, qty, cost_usd, realized_pnl_usd, updated_at FROM positions WHERE wallet_pubkey=? ORDER BY cost_usd DESC",
            (wallet_pubkey,),
        )
        out = []
        for row in cur.fetchall():
            out.append(
                {
                    "mint": row[0],
                    "qty": float(row[1]),
                    "cost_usd": float(row[2]),
                    "realized_pnl_usd": float(row[3]),
                    "updated_at": float(row[4]),
                }
            )
        return out
    finally:
        con.close()

