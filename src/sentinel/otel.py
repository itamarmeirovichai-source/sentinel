"""Export the audit trail as OpenTelemetry GenAI-semantic-convention spans.

Interoperability without a hard dependency: this produces plain dicts shaped like OTLP
spans using the `gen_ai.*` conventions (plus `sentinel.*` for the policy verdict), so the
trail can be shipped to Langfuse / Datadog / any OTel backend. Wiring a real
opentelemetry-sdk exporter is a thin adapter over this shape (see ROADMAP.md).
"""
from __future__ import annotations

from typing import Iterable

from sentinel.models import AuditRecord

_ERROR_STATUSES = {"error", "blocked", "killed"}


def _to_span(rec: AuditRecord) -> dict:
    start_ns = int(rec.ts * 1_000_000_000)
    return {
        "name": f"execute_tool {rec.tool}",
        "start_time_unix_nano": start_ns,
        "end_time_unix_nano": start_ns,
        "attributes": {
            "gen_ai.operation.name": "execute_tool",
            "gen_ai.tool.name": rec.tool,
            "gen_ai.agent.id": rec.agent_id,
            "gen_ai.conversation.id": rec.session_id,
            "sentinel.decision": rec.decision,
            "sentinel.status": rec.status,
            "sentinel.phase": rec.phase,
            "sentinel.policy_rule": rec.policy_rule,
            "sentinel.action_id": rec.action_id,
            "sentinel.flags": list(rec.flags),
            "sentinel.audit.seq": rec.seq,
            "sentinel.audit.hash": rec.hash,
            "sentinel.compliance.eu_ai_act_art12": bool(rec.compliance.get("eu_ai_act_art12")),
            "sentinel.compliance.owasp_agentic": rec.compliance.get("owasp_agentic", []),
        },
        "status": {
            "code": "ERROR" if rec.status in _ERROR_STATUSES else "OK",
            "message": rec.reason,
        },
    }


def to_otel_spans(records: Iterable[AuditRecord]) -> list[dict]:
    return [_to_span(r) for r in records]


def _attr(value):
    if value is None:
        return None
    if isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return [str(x) for x in value]
    return str(value)


def record_spans(records: Iterable[AuditRecord], tracer) -> int:
    """Emit each audit record as a *real* OpenTelemetry span via `tracer`. Returns the count.

    Requires `opentelemetry-sdk` (the `otel` extra). The caller wires up the tracer and
    exporter (OTLP to a collector, console, or in-memory). None-valued attributes are skipped.
    """
    from opentelemetry.trace import Status as OtelStatus, StatusCode  # lazy import

    count = 0
    for rec in records:
        span_dict = _to_span(rec)
        with tracer.start_as_current_span(span_dict["name"]) as span:
            for key, value in span_dict["attributes"].items():
                attr = _attr(value)
                if attr is not None:
                    span.set_attribute(key, attr)
            if span_dict["status"]["code"] == "ERROR":
                span.set_status(OtelStatus(StatusCode.ERROR, span_dict["status"]["message"]))
        count += 1
    return count
