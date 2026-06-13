"""Shared SQLite connection helper: WAL + busy_timeout for concurrency safety.

Sentinel's components (audit, kill switch, approvals, rate limiter) all open the same DB,
and the dashboard reads while agents write. WAL journaling plus a busy timeout prevent
"database is locked" errors under that concurrency.
"""
from __future__ import annotations

import os
import sqlite3


def connect(db_path: str, busy_timeout_ms: int = 5000) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    con = sqlite3.connect(db_path, timeout=busy_timeout_ms / 1000)
    con.row_factory = sqlite3.Row
    con.execute(f"PRAGMA busy_timeout={int(busy_timeout_ms)}")
    con.execute("PRAGMA journal_mode=WAL")
    return con
