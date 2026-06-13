"""Persisted kill switch (SQLite). Global ('*') or per-agent scope.

Persistence matters: a kill decision must survive a process restart (threat T5).
The core (sentinel.check) treats a read failure here as "active" — fail-closed.
"""
from __future__ import annotations

import os
import sqlite3
import time
from typing import Callable

from sentinel.db import connect


class KillSwitch:
    def __init__(self, db_path: str, clock: Callable[[], float] = time.time):
        self.db_path = db_path
        self._clock = clock
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS killswitch (
                    scope TEXT PRIMARY KEY, active INTEGER, reason TEXT, ts REAL
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        return connect(self.db_path)

    def arm(self, scope: str = "*", reason: str = "") -> None:
        with self._conn() as con:
            con.execute(
                "INSERT INTO killswitch (scope, active, reason, ts) VALUES (?,1,?,?) "
                "ON CONFLICT(scope) DO UPDATE SET active=1, reason=excluded.reason, ts=excluded.ts",
                (scope, reason, self._clock()),
            )

    def disarm(self, scope: str = "*") -> None:
        with self._conn() as con:
            con.execute("UPDATE killswitch SET active=0 WHERE scope=?", (scope,))

    def is_active(self, agent_id: str = "*") -> bool:
        with self._conn() as con:
            rows = con.execute(
                "SELECT active FROM killswitch WHERE scope IN ('*', ?)", (agent_id,)
            ).fetchall()
        return any(r["active"] == 1 for r in rows)

    def status(self) -> dict:
        with self._conn() as con:
            rows = con.execute("SELECT scope, active, reason, ts FROM killswitch").fetchall()
        return {
            r["scope"]: {"active": bool(r["active"]), "reason": r["reason"], "ts": r["ts"]}
            for r in rows
        }
