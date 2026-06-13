"""Control-plane API contract."""
from fastapi.testclient import TestClient

from sentinel.api import create_app
from sentinel.audit import AuditLog
from sentinel.config import Config
from sentinel.killswitch import KillSwitch
from sentinel.models import ToolCall, Decision, Status


def make_client(tmp_path):
    db = str(tmp_path / "api.db")
    pol = str(tmp_path / "p.yaml")
    with open(pol, "w", encoding="utf-8") as fh:
        fh.write("version: 1\ndefault: deny\nrules: []\n")
    AuditLog(db).append(
        ToolCall(tool="get_quote", args={"symbol": "AAPL"}),
        Decision.ALLOW, "reads", "ok", [], Status.EXECUTED,
    )
    return TestClient(create_app(Config(db_path=db, policy_path=pol))), db


def test_status_reports_counts_and_integrity(tmp_path):
    client, _ = make_client(tmp_path)
    body = client.get("/api/status").json()
    assert body["total_actions"] == 1
    assert body["integrity"]["ok"] is True


def test_actions_endpoint_returns_records(tmp_path):
    client, _ = make_client(tmp_path)
    actions = client.get("/api/actions").json()
    assert actions[0]["tool"] == "get_quote"


def test_dashboard_is_served(tmp_path):
    client, _ = make_client(tmp_path)
    r = client.get("/")
    assert r.status_code == 200
    assert "SENTINEL" in r.text


def test_kill_and_unkill_via_api(tmp_path):
    client, db = make_client(tmp_path)
    client.post("/api/kill", json={"scope": "*", "reason": "test"})
    assert KillSwitch(db).is_active("any-agent") is True  # shared via SQLite
    client.post("/api/unkill", json={"scope": "*"})
    assert KillSwitch(db).is_active("any-agent") is False


def test_verify_endpoint(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/verify").json()["ok"] is True


def test_policy_get_update_and_reject_invalid(tmp_path):
    client, _ = make_client(tmp_path)
    assert "default: deny" in client.get("/api/policy").json()["yaml"]

    ok = client.put("/api/policy", json={"yaml": "version: 1\ndefault: allow\nrules: []\n"})
    assert ok.status_code == 200
    assert "default: allow" in client.get("/api/policy").json()["yaml"]

    bad = client.put("/api/policy", json={"yaml": "rules: [unclosed"})
    assert bad.status_code == 400


def test_mutations_require_token_when_configured(tmp_path):
    db = str(tmp_path / "api.db")
    pol = str(tmp_path / "p.yaml")
    with open(pol, "w", encoding="utf-8") as fh:
        fh.write("version: 1\ndefault: deny\nrules: []\n")
    client = TestClient(create_app(Config(db_path=db, policy_path=pol, api_token="s3cret")))

    assert client.post("/api/kill", json={"scope": "*"}).status_code == 401
    assert client.post("/api/kill", json={"scope": "*"},
                       headers={"Authorization": "Bearer nope"}).status_code == 401
    ok = client.post("/api/kill", json={"scope": "*"},
                     headers={"Authorization": "Bearer s3cret"})
    assert ok.status_code == 200
    assert client.get("/api/status").json()["auth_required"] is True  # reads stay open


def test_pending_approvals_listed_and_approvable(tmp_path):
    from sentinel.approvals import Approvals
    from sentinel.models import ToolCall

    db = str(tmp_path / "api.db")
    pol = str(tmp_path / "p.yaml")
    with open(pol, "w", encoding="utf-8") as fh:
        fh.write("version: 1\ndefault: deny\nrules: []\n")
    ap = Approvals(db)
    aid = ap.request(ToolCall(tool="place_order", args={"amount": 5000}, agent_id="a1"))

    client = TestClient(create_app(Config(db_path=db, policy_path=pol)))
    listed = client.get("/api/approvals").json()
    assert len(listed) == 1 and listed[0]["id"] == aid
    assert client.post("/api/approve", json={"id": aid, "by": "tester"}).status_code == 200
    assert ap.consume(ToolCall(tool="place_order", args={"amount": 5000}, agent_id="a1")) is True
