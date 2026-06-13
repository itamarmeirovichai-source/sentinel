"""Heuristic anomaly / injection detector (v1).

It *flags*, it does not block — flags are recorded in the audit trail and can be
escalated by policy later. This is intentionally simple, rule-based, and explainable;
ML-based behavioral baselining is future work (see ROADMAP.md).
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


class Detector:
    def __init__(self, baseline_tools: Optional[list[str]] = None,
                 sensitive_tools: Optional[list[str]] = None,
                 egress_tools: Optional[list[str]] = None):
        self.baseline = set(baseline_tools) if baseline_tools else None
        self.sensitive = set(sensitive_tools or [])
        self.egress = set(egress_tools or [])
        self._touched_secret: set[str] = set()  # session_ids that have accessed secrets

    def inspect(self, call: ToolCall) -> list[Flag]:
        flags: list[Flag] = []

        # Lethal trifecta: secret access followed by external egress within a session.
        if call.tool in self.sensitive:
            self._touched_secret.add(call.session_id)
        if call.tool in self.egress and call.session_id in self._touched_secret:
            flags.append(Flag(
                "lethal_trifecta", "high",
                f"egress tool '{call.tool}' after secret access in session '{call.session_id}'",
            ))

        # Off-baseline tool usage.
        if self.baseline is not None and call.tool not in self.baseline:
            flags.append(Flag("off_baseline", "warn", f"tool '{call.tool}' not in declared baseline"))

        # Injection signatures inside string arguments.
        for key, value in call.args.items():
            if isinstance(value, str):
                for pat in _INJECTION_PATTERNS:
                    if pat.search(value):
                        flags.append(Flag("injection_signature", "high",
                                          f"suspicious pattern in arg '{key}'"))
                        break
        return flags
