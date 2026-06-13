"""Audit-trail integrity contract — written before the implementation.

This is the heart of the wedge: the log must be append-only and tamper-evident.
"""
import sqlite3

from sentinel.audit import AuditLog
from sentinel.models import Decision, Status, ToolCall


def mk(tool="get_quote", **args):
    return ToolCall(tool=tool, args=args, agent_id="a1", session_id="s1")


def test_append_builds_hash_chain(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    r1 = log.append(mk(), Decision.ALLOW, "reads", "ok", [], Status.EXECUTED)
    r2 = log.append(mk("place_order", amount=10), Decision.BLOCK, "forbid", "no", [], Status.BLOCKED)
    assert (r1.seq, r2.seq) == (1, 2)
    assert r1.prev_hash == "0" * 64          # genesis
    assert r2.prev_hash == r1.hash           # chained
    assert log.verify().ok


def test_secrets_are_redacted_before_storage(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"), redact_keys=["api_key"])
    r = log.append(mk("login", api_key="SECRET123", user="bob"), Decision.ALLOW, None, "", [], Status.EXECUTED)
    assert r.args["api_key"] != "SECRET123"
    assert "SECRET123" not in str(r.args)
    assert r.args["user"] == "bob"


def test_tampering_with_a_row_is_detected(tmp_path):
    db = str(tmp_path / "a.db")
    log = AuditLog(db)
    log.append(mk(), Decision.ALLOW, "r", "", [], Status.EXECUTED)
    log.append(mk("place_order", amount=999), Decision.BLOCK, "f", "", [], Status.BLOCKED)
    log.append(mk("get_balance"), Decision.ALLOW, "r", "", [], Status.EXECUTED)
    assert log.verify().ok

    con = sqlite3.connect(db)
    con.execute("UPDATE audit SET args = ? WHERE seq = 2", ('{"amount": 1}',))
    con.commit()
    con.close()

    v = log.verify()
    assert not v.ok
    assert v.first_bad_seq == 2


def test_deleting_a_middle_row_is_detected(tmp_path):
    db = str(tmp_path / "a.db")
    log = AuditLog(db)
    for _ in range(3):
        log.append(mk(), Decision.ALLOW, "r", "", [], Status.EXECUTED)
    con = sqlite3.connect(db)
    con.execute("DELETE FROM audit WHERE seq = 2")
    con.commit()
    con.close()
    assert not log.verify().ok


def test_export_is_a_compliance_report(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.append(mk(), Decision.ALLOW, "r", "", [], Status.EXECUTED)
    rep = log.export()
    assert rep["integrity"]["ok"] is True
    assert rep["count"] == 1
    assert rep["records"][0]["compliance"]["eu_ai_act_art12"] is True
    assert "generated_at" in rep
