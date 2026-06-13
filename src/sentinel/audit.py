"""Append-only, hash-chained audit log (SQLite) — the flight recorder.

Each record's hash = sha256(prev_hash + canonical_json(payload)), where payload is
every field except `hash`. verify() recomputes the whole chain and reports the first
record that fails (edit, reorder, or deletion). Tail-truncation is the one residual
gap (see ROADMAP.md: periodic external anchoring).
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Callable, Optional

from sentinel.models import ToolCall, Decision, Status, AuditRecord
from sentinel.redaction import redact, DEFAULT_REDACT_KEYS
from sentinel.compliance import map_compliance

GENESIS = "0" * 64

# Fields that participate in the hash, in a fixed list (order is irrelevant because
# canonicalization sorts keys, but we keep an explicit allow-list).
_FIELDS = [
    "seq", "ts", "agent_id", "session_id", "tool", "args", "decision",
    "policy_rule", "reason", "flags", "status", "error", "compliance", "prev_hash",
]


@dataclass
class VerifyResult:
    ok: bool
    first_bad_seq: Optional[int] = None
    message: str = "ok"


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash(prev_hash: str, payload: dict) -> str:
    return hashlib.sha256((prev_hash + _canonical(payload)).encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, db_path: str, redact_keys: Optional[list[str]] = None,
                 clock: Callable[[], float] = time.time):
        self.db_path = db_path
        self.redact_keys = redact_keys if redact_keys is not None else list(DEFAULT_REDACT_KEYS)
        self._clock = clock
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._conn() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS audit (
                    seq INTEGER PRIMARY KEY,
                    ts REAL, agent_id TEXT, session_id TEXT, tool TEXT,
                    args TEXT, decision TEXT, policy_rule TEXT, reason TEXT,
                    flags TEXT, status TEXT, error TEXT, compliance TEXT,
                    prev_hash TEXT, hash TEXT
                )
                """
            )

    def append(self, call: ToolCall, decision: Decision, policy_rule: Optional[str],
               reason: str, flags: list[str], status: Status,
               error: Optional[str] = None) -> AuditRecord:
        dec = decision if isinstance(decision, Decision) else Decision(str(decision))
        sval = status.value if isinstance(status, Status) else str(status)
        with self._conn() as con:
            row = con.execute("SELECT seq, hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
            prev_seq = row["seq"] if row else 0
            prev_hash = row["hash"] if row else GENESIS
            rec = AuditRecord(
                seq=prev_seq + 1,
                ts=self._clock(),
                agent_id=call.agent_id,
                session_id=call.session_id,
                tool=call.tool,
                args=redact(call.args, self.redact_keys),
                decision=dec.value,
                policy_rule=policy_rule,
                reason=reason,
                flags=list(flags),
                status=sval,
                error=error,
                compliance=map_compliance(dec, list(flags)),
                prev_hash=prev_hash,
            )
            payload = {f: getattr(rec, f) for f in _FIELDS}
            rec.hash = _hash(prev_hash, payload)
            con.execute(
                "INSERT INTO audit (seq,ts,agent_id,session_id,tool,args,decision,policy_rule,"
                "reason,flags,status,error,compliance,prev_hash,hash) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (rec.seq, rec.ts, rec.agent_id, rec.session_id, rec.tool,
                 json.dumps(rec.args, default=str), rec.decision, rec.policy_rule, rec.reason,
                 json.dumps(rec.flags), rec.status, rec.error, json.dumps(rec.compliance),
                 rec.prev_hash, rec.hash),
            )
        return rec

    def _row_to_record(self, row: sqlite3.Row) -> AuditRecord:
        return AuditRecord(
            seq=row["seq"], ts=row["ts"], agent_id=row["agent_id"], session_id=row["session_id"],
            tool=row["tool"], args=json.loads(row["args"]), decision=row["decision"],
            policy_rule=row["policy_rule"], reason=row["reason"], flags=json.loads(row["flags"]),
            status=row["status"], error=row["error"], compliance=json.loads(row["compliance"]),
            prev_hash=row["prev_hash"], hash=row["hash"],
        )

    def records(self) -> list[AuditRecord]:
        with self._conn() as con:
            rows = con.execute("SELECT * FROM audit ORDER BY seq ASC").fetchall()
        return [self._row_to_record(r) for r in rows]

    def verify(self) -> VerifyResult:
        expected_prev = GENESIS
        expected_seq = 1
        with self._conn() as con:
            rows = con.execute("SELECT * FROM audit ORDER BY seq ASC").fetchall()
        for row in rows:
            rec = self._row_to_record(row)
            if rec.seq != expected_seq:
                return VerifyResult(False, rec.seq, f"sequence gap at seq {rec.seq} (deletion?)")
            if rec.prev_hash != expected_prev:
                return VerifyResult(False, rec.seq, f"broken chain link at seq {rec.seq}")
            payload = {f: getattr(rec, f) for f in _FIELDS}
            if _hash(rec.prev_hash, payload) != rec.hash:
                return VerifyResult(False, rec.seq, f"hash mismatch at seq {rec.seq} (row edited?)")
            expected_prev = rec.hash
            expected_seq += 1
        return VerifyResult(True, None, "ok")

    def export(self, start: Optional[float] = None, end: Optional[float] = None) -> dict:
        recs = self.records()
        if start is not None:
            recs = [r for r in recs if r.ts >= start]
        if end is not None:
            recs = [r for r in recs if r.ts <= end]
        v = self.verify()
        return {
            "generated_at": self._clock(),
            "integrity": {"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message},
            "count": len(recs),
            "frameworks": ["EU AI Act Art. 12", "OWASP Agentic Top 10"],
            "records": [r.__dict__ for r in recs],
        }
