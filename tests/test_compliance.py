"""Compliance mapping + EU AI Act Article 12 report."""
from sentinel.audit import AuditLog
from sentinel.compliance import art12_report, map_compliance
from sentinel.models import Decision, Status, ToolCall


def test_map_compliance_tags_block_and_art12():
    c = map_compliance(Decision.BLOCK, [])
    assert c["eu_ai_act_art12"] is True
    assert any("Policy Violation" in t for t in c["owasp_agentic"])


def test_art12_report_shape(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.append(ToolCall(tool="get_quote", args={}, agent_id="bot1"),
               Decision.ALLOW, "reads", "ok", [], Status.EXECUTED)
    rep = art12_report(log.records(), verify_ok=log.verify().ok, generated_at=123.0,
                       system_name="TradingBot", provider="Itamar")
    assert rep["framework"].startswith("EU AI Act")
    assert rep["system"]["name"] == "TradingBot"
    assert rep["automatic_logging"] is True
    assert rep["tamper_evidence"]["intact"] is True
    assert rep["event_count"] == 1
    assert rep["events"][0]["tool"] == "get_quote"
    assert "retention" in rep
