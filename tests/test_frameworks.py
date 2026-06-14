"""Regulation catalog — structure, honest gaps, and per-framework reports."""
import pytest

from sentinel import frameworks
from sentinel.audit import AuditLog
from sentinel.models import Decision, Status, ToolCall


def test_catalog_has_multiple_frameworks_with_valid_coverage():
    assert len(frameworks.list_frameworks()) >= 6
    for f in frameworks._FRAMEWORKS:
        assert f["obligations"]
        for ob in f["obligations"]:
            assert {"id", "title", "requirement", "coverage", "how"} <= set(ob)
            assert ob["coverage"] in {"full", "partial", "none"}


def test_honest_gaps_are_present():
    totals = frameworks.coverage_summary()["totals"]
    assert totals["none"] > 0      # we do NOT claim to cover everything
    assert totals["partial"] > 0


def test_eu_ai_act_article_12_is_full_coverage():
    f = frameworks.get_framework("eu_ai_act")
    art12 = [o for o in f["obligations"] if o["id"].startswith("Art. 12")]
    assert art12 and art12[0]["coverage"] == "full"


def test_framework_report_has_evidence_and_disclaimer(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.append(ToolCall(tool="get_quote", agent_id="b1"), Decision.ALLOW, "r", "", [], Status.EXECUTED)
    rep = frameworks.framework_report("gdpr", records=log.records(), verify_ok=log.verify().ok,
                                      generated_at=1.0, system_name="X", provider="Y")
    assert rep["framework"]["key"] == "gdpr"
    assert rep["audit_evidence"]["event_count"] == 1
    assert rep["audit_evidence"]["integrity_intact"] is True
    assert "disclaimer" in rep


def test_unknown_framework_raises():
    with pytest.raises(KeyError):
        frameworks.framework_report("nope")


def test_coverage_summary_totals_are_consistent():
    s = frameworks.coverage_summary()
    per = sum(f["full"] + f["partial"] + f["none"] for f in s["frameworks"])
    assert sum(s["totals"].values()) == per
