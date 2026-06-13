"""Sentinel core — the interception + enforcement loop.

Two non-negotiable safety properties live here:
  * default-deny  — delegated to the policy engine (no match -> block)
  * fail-closed   — any exception inside check() resolves to BLOCK, never execute

The SDK-wrapper interception (`guard`) is one implementation; the core `check()`
takes a ToolCall and is interceptor-agnostic, so an MCP-proxy adapter can call the
same path later without touching policy/audit/kill.
"""
from __future__ import annotations

import functools
import inspect
from typing import Callable, Optional

from sentinel.models import ToolCall, Decision, Status, CheckResult
from sentinel.policy import Policy
from sentinel.audit import AuditLog
from sentinel.killswitch import KillSwitch
from sentinel.detector import Detector


class BlockedError(RuntimeError):
    """Raised when Sentinel blocks a tool call. Carries the reason + the audit record."""

    def __init__(self, reason: str, record=None):
        super().__init__(reason)
        self.reason = reason
        self.record = record


class Sentinel:
    def __init__(self, policy: Policy, audit: AuditLog, killswitch: KillSwitch,
                 detector: Optional[Detector] = None,
                 agent_id: str = "default", session_id: str = "default"):
        self.policy = policy
        self.audit = audit
        self.killswitch = killswitch
        self.detector = detector or Detector()
        self.agent_id = agent_id
        self.session_id = session_id

    @classmethod
    def from_files(cls, policy: str, db: str, detector: Optional[Detector] = None,
                   agent_id: str = "default", session_id: str = "default") -> "Sentinel":
        return cls(policy=Policy.from_file(policy), audit=AuditLog(db),
                   killswitch=KillSwitch(db), detector=detector,
                   agent_id=agent_id, session_id=session_id)

    # --- core decision ----------------------------------------------------
    def check(self, call: ToolCall) -> CheckResult:
        try:
            if self.killswitch.is_active(call.agent_id):
                return CheckResult(Decision.BLOCK, "killswitch",
                                   f"kill switch active for agent '{call.agent_id}'", [])
            flags = self.detector.inspect(call)
            verdict = self.policy.evaluate(call)
            return CheckResult(verdict.decision, verdict.rule_id, verdict.reason, flags)
        except Exception as exc:  # fail-closed: a core error must never open the gate
            return CheckResult(Decision.BLOCK, "fail-closed", f"sentinel internal error: {exc!r}", [])

    # --- SDK interception -------------------------------------------------
    def guard(self, fn: Optional[Callable] = None, *, tool: Optional[str] = None):
        """Decorator/wrapper. Use as `@sentinel.guard` or `@sentinel.guard(tool="name")`."""
        if fn is None:
            return functools.partial(self.guard, tool=tool)

        tool_name = tool or getattr(fn, "__name__", "anonymous")
        try:
            sig = inspect.signature(fn)
        except (ValueError, TypeError):
            sig = None

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            call = ToolCall(tool=tool_name, args=self._bind(sig, args, kwargs),
                            agent_id=self.agent_id, session_id=self.session_id)
            result = self.check(call)
            flags = [f.as_str() for f in result.flags]

            if result.decision == Decision.ALLOW:
                try:
                    out = fn(*args, **kwargs)
                except Exception as exc:
                    self.audit.append(call, Decision.ALLOW, result.rule_id, result.reason,
                                      flags, Status.ERROR, error=repr(exc))
                    raise
                self.audit.append(call, Decision.ALLOW, result.rule_id, result.reason,
                                  flags, Status.EXECUTED)
                return out

            # Not allowed -> the tool is never invoked.
            if result.rule_id == "killswitch":
                status = Status.KILLED
            elif result.decision == Decision.REQUIRE_APPROVAL:
                status = Status.PENDING_APPROVAL
            else:
                status = Status.BLOCKED
            record = self.audit.append(call, result.decision, result.rule_id, result.reason,
                                       flags, status)
            raise BlockedError(result.reason, record=record)

        return wrapper

    @staticmethod
    def _bind(sig, args, kwargs) -> dict:
        if sig is not None:
            try:
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                mapped = dict(bound.arguments)
                mapped.pop("self", None)
                # flatten **kwargs catch-all if present
                for name, param in sig.parameters.items():
                    if param.kind == inspect.Parameter.VAR_KEYWORD and name in mapped:
                        extra = mapped.pop(name)
                        if isinstance(extra, dict):
                            mapped.update(extra)
                return mapped
            except TypeError:
                pass
        fallback = {f"arg{i}": a for i, a in enumerate(args)}
        fallback.update(kwargs)
        return fallback
