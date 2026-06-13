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
