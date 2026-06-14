"""Catalog of real AI / data regulations and how Sentinel maps to each.

HONESTY (read this): these are *indicative engineering mappings*, NOT legal advice or a
conformity assessment. Each obligation's `coverage` is one of:
  * "full"    — Sentinel provides the control itself
  * "partial" — Sentinel provides evidence/infrastructure, but you must do more
  * "none"    — out of scope; listed so the gaps are explicit, not hidden
Verify everything against the current legal texts and your own obligations.

Citations are article/section identifiers for orientation; wording is paraphrased.
"""
from __future__ import annotations

from typing import Optional

DISCLAIMER = (
    "Indicative engineering mapping, not legal advice or a conformity assessment. "
    "Coverage values describe what Sentinel provides, not whether you are compliant. "
    "Verify against the current legal texts and your obligations."
)

_FRAMEWORKS: list[dict] = [
    {
        "key": "eu_ai_act",
        "name": "EU AI Act (Regulation 2024/1689)",
        "jurisdiction": "European Union",
        "status": "In force; most high-risk obligations apply from 2026-08-02.",
        "obligations": [
            {"id": "Art. 12", "title": "Record-keeping (automatic event logs)",
             "requirement": "High-risk AI systems must technically allow automatic recording of events (logs) over their lifetime.",
             "coverage": "full",
             "how": "Append-only, hash-chained audit log of every agent action; `sentinel export --format art12`."},
            {"id": "Art. 14", "title": "Human oversight",
             "requirement": "Enable humans to oversee operation, intervene, and stop the system ('stop button').",
             "coverage": "partial",
             "how": "Kill switch + human-in-the-loop approvals provide intervene/stop; you still design the oversight process and roles."},
            {"id": "Art. 19 / 26(6)", "title": "Retention of automatically generated logs",
             "requirement": "Keep logs for an appropriate period (deployers: at least 6 months unless other law applies).",
             "coverage": "partial",
             "how": "Durable store + tamper-evidence; you configure retention/backup (Postgres + archival on the roadmap)."},
            {"id": "Art. 26", "title": "Deployer obligations (monitoring, logs, oversight)",
             "requirement": "Deployers monitor operation, keep logs, and ensure human oversight by competent persons.",
             "coverage": "partial",
             "how": "Live action feed + audit + kill/approvals supply the monitoring & log evidence; org process is yours."},
            {"id": "Art. 72", "title": "Post-market monitoring",
             "requirement": "Providers collect and review data on system performance over its lifetime.",
             "coverage": "partial",
             "how": "Audit trail + detector flags are the raw monitoring data; analysis/review process is yours."},
            {"id": "Art. 50", "title": "Transparency to natural persons",
             "requirement": "Disclose AI interaction; mark synthetic/deepfake content.",
             "coverage": "none",
             "how": "Out of scope — Sentinel governs tool actions, not user-facing disclosure or content labelling."},
            {"id": "Art. 9 / Annex IV", "title": "Risk management system & technical documentation",
             "requirement": "Establish a risk-management process and maintain technical documentation.",
             "coverage": "none",
             "how": "Organisational process / documentation — not something a runtime tool produces."},
        ],
    },
    {
        "key": "gdpr",
        "name": "GDPR (Regulation 2016/679)",
        "jurisdiction": "European Union / EEA",
        "status": "In force since 2018.",
        "obligations": [
            {"id": "Art. 5(1)(c)", "title": "Data minimisation",
             "requirement": "Process only personal data that is adequate, relevant and limited to what is necessary.",
             "coverage": "partial",
             "how": "Secrets/PII are redacted before they reach the audit log; the detector flags PII in arguments."},
            {"id": "Art. 22", "title": "Automated individual decision-making",
             "requirement": "Right to obtain human intervention in decisions producing legal/significant effects.",
             "coverage": "partial",
             "how": "Require-approval + kill switch provide a human-in-the-loop checkpoint for sensitive actions."},
            {"id": "Art. 30", "title": "Records of processing activities",
             "requirement": "Maintain records of processing operations.",
             "coverage": "partial",
             "how": "The audit trail records each automated action with actor, decision and outcome."},
            {"id": "Art. 32", "title": "Security of processing",
             "requirement": "Implement appropriate technical measures (access control, integrity).",
             "coverage": "partial",
             "how": "Token-gated control plane + tamper-evident, redacted logs; broader security posture is yours."},
            {"id": "Art. 17", "title": "Right to erasure",
             "requirement": "Erase personal data on request in defined cases.",
             "coverage": "none",
             "how": "Tension by design: the audit log is append-only/immutable. Keep PII OUT of the log (redaction); manage erasure in source systems."},
        ],
    },
    {
        "key": "nist_ai_rmf",
        "name": "NIST AI Risk Management Framework 1.0 (+ Generative AI Profile)",
        "jurisdiction": "United States (voluntary)",
        "status": "Published 2023; widely referenced.",
        "obligations": [
            {"id": "GOVERN", "title": "Policies, accountability, audit",
             "requirement": "Cultivate a culture of risk management; define and enforce policies.",
             "coverage": "partial",
             "how": "Declarative default-deny policy engine + immutable audit give enforceable, reviewable policy."},
            {"id": "MAP", "title": "Context & risk framing",
             "requirement": "Establish context and categorise AI risks.",
             "coverage": "none",
             "how": "Analytical/process activity — not runtime tooling."},
            {"id": "MEASURE", "title": "Analyze, track, monitor risks",
             "requirement": "Assess and continuously monitor identified risks.",
             "coverage": "partial",
             "how": "Detector flags (injection, lethal-trifecta, PII, dangerous args) + the action feed are continuous monitoring signals."},
            {"id": "MANAGE", "title": "Respond, recover, communicate",
             "requirement": "Act on risks, including incident response.",
             "coverage": "partial",
             "how": "Kill switch (immediate stop) + forensic audit (incident evidence) support response & recovery."},
        ],
    },
    {
        "key": "iso_42001",
        "name": "ISO/IEC 42001:2023 (AI management system)",
        "jurisdiction": "International (certifiable)",
        "status": "Published 2023; basis for third-party AIMS certification.",
        "obligations": [
            {"id": "Annex A — operation", "title": "Operational controls & monitoring",
             "requirement": "Operate and monitor the AI system under defined controls.",
             "coverage": "partial",
             "how": "Runtime policy enforcement + live monitoring + audit provide operational control evidence."},
            {"id": "Annex A — logging", "title": "Event logging & records",
             "requirement": "Record events relevant to AI system operation.",
             "coverage": "partial",
             "how": "Tamper-evident audit trail; export for an auditor."},
            {"id": "Annex A — incident", "title": "Incident management",
             "requirement": "Detect and respond to AI incidents.",
             "coverage": "partial",
             "how": "Detector flags + kill switch + audit; the management process is yours."},
            {"id": "Clause 4-10 (AIMS)", "title": "Management-system processes",
             "requirement": "Establish the overall management system (leadership, planning, improvement).",
             "coverage": "none",
             "how": "Organisational management system — not a tool."},
        ],
    },
    {
        "key": "colorado_ai_act",
        "name": "Colorado AI Act (SB 24-205)",
        "jurisdiction": "United States — Colorado",
        "status": "Effective 2026-06-30 (amended timeline).",
        "obligations": [
            {"id": "Risk management", "title": "Risk-management policy & program",
             "requirement": "Deployers of high-risk systems maintain a risk-management program.",
             "coverage": "partial",
             "how": "Policy engine + audit are core evidence; the program itself is organisational."},
            {"id": "Recordkeeping", "title": "Records of system operation",
             "requirement": "Keep records supporting oversight of consequential decisions.",
             "coverage": "partial",
             "how": "Per-action audit trail with decisions and outcomes."},
            {"id": "AG notification", "title": "Notice of algorithmic discrimination",
             "requirement": "Notify the Attorney General of discovered algorithmic discrimination (within 90 days).",
             "coverage": "partial",
             "how": "Detector flags + audit help detect and evidence incidents; the notification itself is yours."},
            {"id": "Consumer notice", "title": "Notice & right to contest",
             "requirement": "Inform consumers and allow them to contest decisions.",
             "coverage": "none",
             "how": "User-facing process — out of scope."},
        ],
    },
    {
        "key": "sec_finra",
        "name": "SEC Rule 17a-4 / FINRA Rule 4511 (broker-dealer recordkeeping)",
        "jurisdiction": "United States — securities (relevant to trading agents)",
        "status": "In force; 17a-4 modernised 2022 (audit-trail alternative to WORM).",
        "obligations": [
            {"id": "17a-4(f)", "title": "Non-rewriteable records / audit-trail alternative",
             "requirement": "Preserve records in non-erasable form, or via a compliant audit-trail alternative.",
             "coverage": "partial",
             "how": "Hash-chained, tamper-evident audit is an audit-trail-style control; true WORM needs object-lock/Postgres storage (roadmap)."},
            {"id": "17a-4 / 4511", "title": "Retention periods",
             "requirement": "Retain records for the prescribed periods (often 3-6 years).",
             "coverage": "partial",
             "how": "Durable store; you configure long-term retention/archival."},
            {"id": "Supervision", "title": "Supervisory review of automated activity",
             "requirement": "Supervise and review automated/algorithmic trading activity.",
             "coverage": "partial",
             "how": "Action feed + kill switch + approvals give supervisory control; the supervisory program is yours."},
        ],
    },
]

_COVERAGE_VALUES = {"full", "partial", "none"}


def list_frameworks() -> list[dict]:
    return [
        {"key": f["key"], "name": f["name"], "jurisdiction": f["jurisdiction"],
         "obligation_count": len(f["obligations"])}
        for f in _FRAMEWORKS
    ]


def get_framework(key: str) -> Optional[dict]:
    return next((f for f in _FRAMEWORKS if f["key"] == key), None)


def _counts(framework: dict) -> dict:
    counts = {"full": 0, "partial": 0, "none": 0}
    for ob in framework["obligations"]:
        counts[ob["coverage"]] += 1
    return counts


def coverage_summary() -> dict:
    per = []
    totals = {"full": 0, "partial": 0, "none": 0}
    for f in _FRAMEWORKS:
        c = _counts(f)
        for k in totals:
            totals[k] += c[k]
        per.append({"key": f["key"], "name": f["name"], "jurisdiction": f["jurisdiction"], **c})
    return {"disclaimer": DISCLAIMER, "frameworks": per, "totals": totals}


def framework_report(key: str, *, records=None, verify_ok: Optional[bool] = None,
                     generated_at: float = 0.0, system_name: str = "unspecified AI system",
                     provider: str = "unspecified") -> dict:
    f = get_framework(key)
    if f is None:
        raise KeyError(f"unknown framework '{key}'; try one of {[x['key'] for x in _FRAMEWORKS]}")
    report = {
        "disclaimer": DISCLAIMER,
        "generated_at": generated_at,
        "system": {"name": system_name, "provider": provider},
        "framework": {"key": f["key"], "name": f["name"],
                      "jurisdiction": f["jurisdiction"], "status": f["status"]},
        "coverage": _counts(f),
        "obligations": f["obligations"],
        "audit_evidence": None,
    }
    if records is not None:
        report["audit_evidence"] = {
            "event_count": len(records),
            "logging_period": {
                "start": records[0].ts if records else None,
                "end": records[-1].ts if records else None,
            },
            "integrity_intact": verify_ok,
        }
    return report
