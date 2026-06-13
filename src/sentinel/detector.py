"""Heuristic anomaly / injection detector (v1+).

It *flags*, it does not block — flags are recorded in the audit trail and can be
escalated by policy or surfaced for review. Rule-based and explainable; ML-based
behavioral baselining is future work (see ROADMAP.md).

Signals:
  * lethal_trifecta    — private-data access then external egress (full trifecta when
                         untrusted content was also ingested in the same session)
  * exfil_risk         — untrusted-content ingestion then egress (no secret seen)
  * off_baseline       — a tool outside the declared baseline
  * injection_signature — prompt-injection phrases in string args
  * dangerous_arg      — command / SQL / path-traversal / suspicious-URL patterns
  * pii_in_arg         — email / card-like / SSN-like values in string args
"""
from __future__ import annotations

import re
from typing import Optional

from sentinel.models import Flag, ToolCall

_INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (all )?previous instructions"),
    re.compile(r"(?i)disregard (the )?(above|previous|system)"),
    re.compile(r"(?i)exfiltrat"),
    re.compile(r"(?i)reveal (the )?(system prompt|secrets?|api[_ ]?keys?)"),
    re.compile(r"(?i)you are now (a|an|in)"),
]

_DANGEROUS_PATTERNS = [
    ("command_injection", re.compile(r"(?:;|\|\||&&|\$\(|`|\brm\s+-rf\b)")),
    ("sql_injection", re.compile(r"(?i)(?:\bdrop\s+table\b|\bunion\s+select\b|'\s*or\s*'1'\s*=\s*'1)")),
    ("path_traversal", re.compile(r"(?:\.\./|\.\.\\|/etc/passwd|%2e%2e/)")),
    ("suspicious_url", re.compile(r"(?i)(?:data:text/html|https?://\d{1,3}(?:\.\d{1,3}){3}|https?://[^\s]*\.(?:ru|tk|top|xyz)\b)")),
]

_PII_PATTERNS = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("card_like", re.compile(r"\b(?:\d{4}[ -]){3}\d{4}\b|\b\d{13,16}\b")),
    ("ssn_like", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
]


class Detector:
    def __init__(self, baseline_tools: Optional[list[str]] = None,
                 sensitive_tools: Optional[list[str]] = None,
                 egress_tools: Optional[list[str]] = None,
                 untrusted_tools: Optional[list[str]] = None):
        self.baseline = set(baseline_tools) if baseline_tools else None
        self.sensitive = set(sensitive_tools or [])
        self.egress = set(egress_tools or [])
        self.untrusted = set(untrusted_tools or [])
        self._touched_secret: set[str] = set()      # session_ids that accessed secrets
        self._touched_untrusted: set[str] = set()    # session_ids that ingested untrusted content

    def inspect(self, call: ToolCall) -> list[Flag]:
        flags: list[Flag] = []
        sid = call.session_id

        if call.tool in self.sensitive:
            self._touched_secret.add(sid)
        if call.tool in self.untrusted:
            self._touched_untrusted.add(sid)

        # Lethal trifecta / exfil risk on egress.
        if call.tool in self.egress:
            if sid in self._touched_secret:
                full = sid in self._touched_untrusted
                detail = ("the lethal trifecta: private data + untrusted content + egress"
                          if full else f"egress tool '{call.tool}' after secret access in session '{sid}'")
                flags.append(Flag("lethal_trifecta", "high", detail))
            elif sid in self._touched_untrusted:
                flags.append(Flag("exfil_risk", "warn",
                                  f"egress tool '{call.tool}' after untrusted-content ingestion"))

        # Off-baseline tool usage.
        if self.baseline is not None and call.tool not in self.baseline:
            flags.append(Flag("off_baseline", "warn", f"tool '{call.tool}' not in declared baseline"))

        # String-argument scans.
        for key, value in call.args.items():
            if not isinstance(value, str):
                continue
            for pat in _INJECTION_PATTERNS:
                if pat.search(value):
                    flags.append(Flag("injection_signature", "high", f"suspicious pattern in arg '{key}'"))
                    break
            for name, pat in _DANGEROUS_PATTERNS:
                if pat.search(value):
                    flags.append(Flag("dangerous_arg", "high", f"{name} pattern in arg '{key}'"))
                    break
            for name, pat in _PII_PATTERNS:
                if pat.search(value):
                    flags.append(Flag("pii_in_arg", "warn", f"{name} in arg '{key}'"))
                    break
        return flags
