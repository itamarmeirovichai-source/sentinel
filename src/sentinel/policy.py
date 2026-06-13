"""Declarative, default-deny policy engine (YAML).

Rules are evaluated first-match-wins. Each rule may match on tool name (glob, or a
list of globs) and/or on argument comparators, and may carry a sliding-window rate
limit. Anything that matches no rule falls through to `default` (deny unless set to
allow). Unknown actions resolve to BLOCK (fail-safe).
"""
from __future__ import annotations

import fnmatch
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

import yaml

from sentinel.models import Decision, ToolCall


@dataclass
class PolicyResult:
    decision: Decision
    rule_id: Optional[str]
    reason: str


_COMPARATORS: dict[str, Callable[[Any, Any], bool]] = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gt": lambda a, b: a > b,
    "gte": lambda a, b: a >= b,
    "lt": lambda a, b: a < b,
    "lte": lambda a, b: a <= b,
    "in": lambda a, b: a in b,
    "contains": lambda a, b: b in a,
}

_ACTIONS = {
    "allow": Decision.ALLOW,
    "block": Decision.BLOCK,
    "deny": Decision.BLOCK,
    "require_approval": Decision.REQUIRE_APPROVAL,
}


class Policy:
    def __init__(self, spec: dict, clock: Callable[[], float] = time.monotonic, limiter=None):
        self.spec = spec or {}
        self.default = str(self.spec.get("default", "deny")).lower()
        self.rules = self.spec.get("rules") or []
        self._clock = clock
        self._limiter = limiter  # if set, used instead of the in-memory window
        self._hits: dict[tuple, list[float]] = {}

    @classmethod
    def from_yaml(cls, text: str, clock: Callable[[], float] = time.monotonic, limiter=None) -> "Policy":
        return cls(yaml.safe_load(text) or {}, clock=clock, limiter=limiter)

    @classmethod
    def from_file(cls, path: str, clock: Callable[[], float] = time.monotonic, limiter=None) -> "Policy":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_yaml(fh.read(), clock=clock, limiter=limiter)

    def evaluate(self, call: ToolCall) -> PolicyResult:
        for rule in self.rules:
            rid = rule.get("id", "<unnamed>")
            if not self._matches(rule.get("match", {}), call):
                continue
            if "rate_limit" in rule and not self._under_rate_limit(rid, call, rule["rate_limit"]):
                return PolicyResult(Decision.BLOCK, rid, f"rate limit exceeded for rule '{rid}'")
            action = str(rule.get("action", "block")).lower()
            return PolicyResult(_ACTIONS.get(action, Decision.BLOCK), rid, f"matched rule '{rid}'")

        if self.default == "allow":
            return PolicyResult(Decision.ALLOW, None, "default-allow (no rule matched)")
        return PolicyResult(Decision.BLOCK, None, "default-deny (no rule matched)")

    # --- matching ---------------------------------------------------------
    def _matches(self, match: dict, call: ToolCall) -> bool:
        if not match:
            return False
        tool_pat = match.get("tool")
        if tool_pat is not None and not self._tool_matches(tool_pat, call.tool):
            return False
        arg_spec = match.get("args")
        if arg_spec and not self._args_match(arg_spec, call.args):
            return False
        return True

    @staticmethod
    def _tool_matches(pattern, tool: str) -> bool:
        pats = pattern if isinstance(pattern, list) else [pattern]
        return any(fnmatch.fnmatchcase(tool, str(p)) for p in pats)

    def _args_match(self, arg_spec: dict, args: dict) -> bool:
        for key, expected in arg_spec.items():
            if key not in args:
                return False
            actual = args[key]
            if isinstance(expected, dict):
                for op, operand in expected.items():
                    fn = _COMPARATORS.get(op)
                    if fn is None:
                        return False
                    try:
                        if not fn(actual, operand):
                            return False
                    except TypeError:
                        return False  # incomparable types -> not a match
            elif actual != expected:
                return False
        return True

    # --- rate limiting (in-memory sliding window) -------------------------
    def _under_rate_limit(self, rid: str, call: ToolCall, rl: dict) -> bool:
        max_n = int(rl.get("max", 0))
        per = float(rl.get("per_seconds", 60))
        if self._limiter is not None:
            return self._limiter.allow(f"{rid}|{call.agent_id}", max_n, per)
        now = self._clock()
        key = (rid, call.agent_id)
        hits = [t for t in self._hits.get(key, []) if now - t < per]
        if len(hits) >= max_n:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True
