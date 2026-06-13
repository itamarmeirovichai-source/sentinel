"""OpenTelemetry GenAI export contract."""
import pytest

from sentinel.models import ToolCall, Decision, Status
from sentinel.audit import AuditLog
from sentinel.otel import to_otel_spans, record_spans


def test_record_maps_to_genai_span(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.append(ToolCall(tool="get_quote", args={"symbol": "AAPL"}, agent_id="bot1"),
               Decision.ALLOW, "reads", "ok", [], Status.EXECUTED)
    spans = to_otel_spans(log.records())
    assert len(spans) == 1
    attrs = spans[0]["attributes"]
    assert attrs["gen_ai.operation.name"] == "execute_tool"
    assert attrs["gen_ai.tool.name"] == "get_quote"
    assert attrs["gen_ai.agent.id"] == "bot1"
    assert attrs["sentinel.decision"] == "allow"
    assert attrs["sentinel.compliance.eu_ai_act_art12"] is True


def test_blocked_record_maps_to_error_status(tmp_path):
    log = AuditLog(str(tmp_path / "a.db"))
    log.append(ToolCall(tool="delete_db"), Decision.BLOCK, "forbid", "denied", [], Status.BLOCKED)
    spans = to_otel_spans(log.records())
    assert spans[0]["status"]["code"] == "ERROR"


def test_record_spans_emits_real_otel_spans(tmp_path):
    pytest.importorskip("opentelemetry.sdk")
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("sentinel-test")

    log = AuditLog(str(tmp_path / "a.db"))
    log.append(ToolCall(tool="get_quote", args={"symbol": "AAPL"}, agent_id="bot1"),
               Decision.ALLOW, "reads", "ok", [], Status.EXECUTED)
    n = record_spans(log.records(), tracer)

    assert n == 1
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["gen_ai.tool.name"] == "get_quote"
