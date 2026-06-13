"""Persisted sliding-window rate limiter (SQLite).

The in-memory limiter inside Policy is fine for unit tests, but a real long-running
agent needs the throttle to survive restarts and hold across processes — that's this.
"""
from __future__ import annotations

import os
import sqlite3
import time
from typing import Callable, Union


class SqliteRateLimiter:
    def __init__(self, db_path: str, clock: Callable[[], float] = time.time):
        self.db_path = db_path
        self._clock = clock
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        with self._conn() as con:
            con.execute("CREATE TABLE IF NOT EXISTS rate_hits (k TEXT, ts REAL)")
            con.execute("CREATE INDEX IF NOT EXISTS idx_rate_k ON rate_hits(k)")

    def _conn(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def allow(self, key: Union[str, tuple], max_n: int, per_seconds: float) -> bool:
        now = self._clock()
        cutoff = now - float(per_seconds)
        k = key if isinstance(key, str) else "|".join(map(str, key))
        with self._conn() as con:
            con.execute("DELETE FROM rate_hits WHERE k=? AND ts < ?", (k, cutoff))
            n = con.execute("SELECT COUNT(*) AS c FROM rate_hits WHERE k=?", (k,)).fetchone()["c"]
            if n >= int(max_n):
                return False
            con.execute("INSERT INTO rate_hits (k, ts) VALUES (?,?)", (k, now))
            return True
