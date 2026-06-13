"""Indicative mapping of each audited action to compliance frameworks.

These are deliberately modest, *labeled* mappings — not certified control coverage.
- EU AI Act Art. 12: every Sentinel record IS an automatic event-log entry, so each
  record carries `eu_ai_act_art12 = True`.
- OWASP Agentic / LLM tags are derived from the verdict + detector flags.

The point for the MVP is that audit records are framework-aware out of the box, so an
export can be handed to a compliance reviewer. Mappings are easy to extend.
"""
from __future__ import annotations

from sentinel.models import Decision


def map_compliance(decision: Decision, flags: list[str]) -> dict:
    blob = " ".join(flags).lower()
    owasp: list[str] = []
    if "injection" in blob:
        owasp.append("LLM01:2025 Prompt Injection")
    if "lethal_trifecta" in blob or "exfil" in blob:
        owasp.append("LLM02:2025 Sensitive Information Disclosure")
    if "off_baseline" in blob:
        owasp.append("ASI Unexpected Tool Invocation")
    if decision == Decision.BLOCK:
        owasp.append("ASI Policy Violation Blocked")
    if decision == Decision.REQUIRE_APPROVAL:
        owasp.append("ASI Human-in-the-loop Checkpoint")
    return {"eu_ai_act_art12": True, "owasp_agentic": owasp}


def art12_report(records, *, verify_ok: bool, generated_at: float,
                 system_name: str, provider: str) -> dict:
    """Build an EU AI Act Article 12 (record-keeping) report from audit records.

    Article 12 requires high-risk AI systems to automatically record events over their
    lifetime, supporting risk identification, post-market monitoring, and operation
    monitoring; Article 19 sets a >= 6-month retention. This frames Sentinel's audit
    trail in those terms and attaches the tamper-evidence status.
    """
    events = [
        {
            "seq": r.seq,
            "timestamp": r.ts,
            "event": "tool_invocation",
            "phase": r.phase,
            "agent_id": r.agent_id,
            "session_id": r.session_id,
            "tool": r.tool,
            "decision": r.decision,
            "outcome": r.status,
            "policy_rule": r.policy_rule,
            "flags": list(r.flags),
            "record_hash": r.hash,
        }
        for r in records
    ]
    return {
        "framework": "EU AI Act — Article 12 (record-keeping / automatic event logs)",
        "system": {"name": system_name, "provider": provider},
        "generated_at": generated_at,
        "automatic_logging": True,
        "logging_period": {
            "start": records[0].ts if records else None,
            "end": records[-1].ts if records else None,
        },
        "retention": "Event logs retained for at least 6 months (Article 19), unless other law requires longer.",
        "tamper_evidence": {
            "method": "SHA-256 hash chain over each record",
            "intact": verify_ok,
            "how_to_verify": "sentinel verify",
        },
        "event_count": len(events),
        "events": events,
    }
