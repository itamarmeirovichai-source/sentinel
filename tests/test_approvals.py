"""Approval-flow contract (human-in-the-loop) — written before the implementation.

Model: a `require_approval` call is held; an operator approves it; the next identical
call is allowed exactly once. Persisted, so approval survives a restart.
"""
from sentinel.approvals import Approvals
from sentinel.models import ToolCall


def call(tool="place_order", **args):
    return ToolCall(tool=tool, args=args, agent_id="a1", session_id="s1")


def test_request_creates_a_pending_entry(tmp_path):
    ap = Approvals(str(tmp_path / "a.db"))
    aid = ap.request(call(amount=5000))
    pend = ap.pending()
    assert len(pend) == 1 and pend[0]["id"] == aid


def test_request_is_idempotent_for_same_call(tmp_path):
    ap = Approvals(str(tmp_path / "a.db"))
    a1 = ap.request(call(amount=5000))
    a2 = ap.request(call(amount=5000))
    assert a1 == a2
    assert len(ap.pending()) == 1


def test_consume_only_succeeds_after_approval_and_is_single_use(tmp_path):
    ap = Approvals(str(tmp_path / "a.db"))
    c = call(amount=5000)
    assert ap.consume(c) is False          # nothing requested/approved yet
    aid = ap.request(c)
    assert ap.consume(c) is False          # still pending
    assert ap.approve(aid, by="boss") is True
    assert ap.consume(c) is True           # approved -> allowed once
    assert ap.consume(c) is False          # single-use


def test_approval_persists_across_instances(tmp_path):
    db = str(tmp_path / "a.db")
    c = call(amount=5000)
    aid = Approvals(db).request(c)
    assert Approvals(db).approve(aid, by="x") is True
    assert Approvals(db).consume(c) is True   # survives "restart"


def test_different_args_need_separate_approval(tmp_path):
    ap = Approvals(str(tmp_path / "a.db"))
    aid = ap.request(call(amount=5000))
    ap.approve(aid, by="x")
    assert ap.consume(call(amount=9999)) is False  # different call, not covered
    assert ap.consume(call(amount=5000)) is True


def test_approval_expires_after_ttl(tmp_path):
    t = {"now": 1000.0}
    ap = Approvals(str(tmp_path / "a.db"), ttl_seconds=60, clock=lambda: t["now"])
    c = call(amount=5000)
    aid = ap.request(c)
    ap.approve(aid, by="x")
    t["now"] += 120  # past TTL -> stale approval can't authorize
    assert ap.consume(c) is False


def test_purge_removes_consumed_rows(tmp_path):
    t = {"now": 1000.0}
    ap = Approvals(str(tmp_path / "a.db"), clock=lambda: t["now"])
    c = call(amount=5000)
    aid = ap.request(c)
    ap.approve(aid, by="x")
    ap.consume(c)
    t["now"] += 10_000
    assert ap.purge(older_than_seconds=3600) >= 1
