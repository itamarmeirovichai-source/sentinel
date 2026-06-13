"""Human-in-the-loop approval store (SQLite).

A `require_approval` decision parks the action here as *pending*. An operator approves
it (dashboard / CLI / API). The next identical call `consume()`s the approval exactly
once and is allowed. A call's identity is the hash of (agent_id, tool, args), so
approving one big order does not silently approve a different one.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import uuid
from typing import Callable

from sentinel.models import ToolCall


def signature(call: ToolCall) -> str:
    payload = json.dumps(
        {"agent": call.agent_id, "tool": call.tool, "args": call.args},
        sort_keys=True, separators=(",", ":"), default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Approvals:
    def __init__(self, db_path: str, clock: Callable[[], float] = time.time):
        self.db_path = db_path
        self._clock = clock
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY, ts REAL, agent_id TEXT, tool TEXT,
                    signature TEXT, args TEXT, status TEXT,
                    approved_by TEXT, approved_ts REAL
                )
                """
            )

    def _conn(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def request(self, call: ToolCall) -> str:
        sig = signature(call)
        with self._conn() as con:
            row = con.execute(
                "SELECT id FROM approvals WHERE signature=? AND status IN ('pending','approved') "
                "ORDER BY ts DESC LIMIT 1",
                (sig,),
            ).fetchone()
            if row:
                return row["id"]
            approval_id = uuid.uuid4().hex
            con.execute(
                "INSERT INTO approvals (id, ts, agent_id, tool, signature, args, status, approved_by, approved_ts) "
                "VALUES (?,?,?,?,?,?, 'pending', NULL, NULL)",
                (approval_id, self._clock(), call.agent_id, call.tool, sig,
                 json.dumps(call.args, default=str)),
            )
            return approval_id

    def pending(self) -> list[dict]:
        with self._conn() as con:
            rows = con.execute(
                "SELECT id, ts, agent_id, tool, args, status FROM approvals "
                "WHERE status='pending' ORDER BY ts ASC"
            ).fetchall()
        return [
            {"id": r["id"], "ts": r["ts"], "agent_id": r["agent_id"], "tool": r["tool"],
             "args": json.loads(r["args"]), "status": r["status"]}
            for r in rows
        ]

    def approve(self, approval_id: str, by: str = "operator") -> bool:
        with self._conn() as con:
            cur = con.execute(
                "UPDATE approvals SET status='approved', approved_by=?, approved_ts=? "
                "WHERE id=? AND status='pending'",
                (by, self._clock(), approval_id),
            )
            return cur.rowcount > 0

    def consume(self, call: ToolCall) -> bool:
        sig = signature(call)
        with self._conn() as con:
            row = con.execute(
                "SELECT id FROM approvals WHERE signature=? AND status='approved' "
                "ORDER BY approved_ts ASC LIMIT 1",
                (sig,),
            ).fetchone()
            if not row:
                return False
            con.execute("UPDATE approvals SET status='consumed' WHERE id=?", (row["id"],))
            return True
