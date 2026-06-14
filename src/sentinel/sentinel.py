"""Sentinel core — the interception + enforcement loop.

Two non-negotiable safety properties live here:
  * default-deny  — delegated to the policy engine (no match -> block)
  * fail-closed   — any exception inside check() resolves to BLOCK, never execute

Allowed calls are logged in two phases (intent before exec, outcome after), linked by
an action_id, so a crash mid-execution still leaves a record of intent. `require_approval`
parks the call in the approvals store; an operator approves it and the next identical
call is allowed exactly once.
"""
from __future__ import annotations

import functools
import inspect
import uuid
from typing import Callable, Optional

from sentinel.approvals import Approvals
from sentinel.audit import AuditLog
from sentinel.detector import Detector
from sentinel.killswitch import KillSwitch
from sentinel.models import CheckResult, Decision, Status, ToolCall
from sentinel.policy import Policy
from sentinel.ratelimit import SqliteRateLimiter


class BlockedError(RuntimeError):
    """Raised when Sentinel blocks a tool call. Carries the reason + the audit record."""

    def __init__(self, reason: str, record=None):
        super().__init__(reason)
        self.reason = reason
        self.record = record


class Sentinel:
    def __init__(self, policy: Policy, audit: AuditLog, killswitch: KillSwitch,
                 detector: Optional[Detector] = None, approvals: Optional[Approvals] = None,
                 agent_id: str = "default", session_id: str = "default",
                 mode: str = "enforce"):
        self.policy = policy
        self.audit = audit
        self.killswitch = killswitch
        self.detector = detector or Detector()
        self.approvals = approvals
        self.agent_id = agent_id
        self.session_id = session_id
        # "enforce" (default) blocks; "monitor" observes-only (logs the would-be verdict,
        # never blocks) — except the kill switch, which always stops the agent.
        self.mode = mode

    @classmethod
    def from_files(cls, policy: str, db: str, detector: Optional[Detector] = None,
                   agent_id: str = "default", session_id: str = "default",
                   mode: str = "enforce") -> "Sentinel":
        return cls(
            policy=Policy.from_file(policy, limiter=SqliteRateLimiter(db)),
            audit=AuditLog(db),
            killswitch=KillSwitch(db),
            detector=detector,
            approvals=Approvals(db),
            agent_id=agent_id,
            session_id=session_id,
            mode=mode,
        )

    # --- core decision ----------------------------------------------------
    def check(self, call: ToolCall) -> CheckResult:
        try:
            if self.killswitch.is_active(call.agent_id):
                return CheckResult(Decision.BLOCK, "killswitch",
                                   f"kill switch active for agent '{call.agent_id}'", [])
            flags = self.detector.inspect(call)
            verdict = self.policy.evaluate(call)
            decision, rule, reason = verdict.decision, verdict.rule_id, verdict.reason

            if decision == Decision.REQUIRE_APPROVAL and self.approvals is not None:
                if self.approvals.consume(call):
                    decision, rule, reason = Decision.ALLOW, "approved", "operator-approved (consumed)"
                else:
                    approval_id = self.approvals.request(call)
                    reason = f"awaiting operator approval (id={approval_id})"

            return CheckResult(decision, rule, reason, flags)
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
            return self.enforce(call, lambda: fn(*args, **kwargs))

        return wrapper

    def wrap_all(self, tools):
        """Guard many tools at once. Accepts a dict {name: fn} or a list [fn] and returns
        the same shape with every callable guarded — handy for a whole agent toolset."""
        if isinstance(tools, dict):
            return {name: self.guard(fn, tool=name) for name, fn in tools.items()}
        return [self.guard(fn) for fn in tools]

    # --- shared decision + logging (used by both enforce and aenforce) ----
    def _decide(self, call: ToolCall):
        result = self.check(call)
        flags = [f.as_str() for f in result.flags]
        action_id = uuid.uuid4().hex
        # monitor mode: observe-only for policy verdicts; the kill switch still enforces.
        monitored = self.mode == "monitor" and result.rule_id != "killswitch"
        if monitored and result.decision != Decision.ALLOW:
            flags = flags + [f"monitor_mode:would_{result.decision.value}"]
        runs = result.decision == Decision.ALLOW or monitored
        return result, flags, action_id, runs

    def _log(self, call, result, flags, action_id, status, error=None, phase="outcome"):
        return self.audit.append(call, result.decision, result.rule_id, result.reason,
                                 flags, status, error=error, action_id=action_id, phase=phase)

    def _block(self, call, result, flags, action_id):
        if result.rule_id == "killswitch":
            status = Status.KILLED
        elif result.decision == Decision.REQUIRE_APPROVAL:
            status = Status.PENDING_APPROVAL
        else:
            status = Status.BLOCKED
        record = self._log(call, result, flags, action_id, status, phase="event")
        raise BlockedError(result.reason, record=record)

    def enforce(self, call: ToolCall, run: Callable[[], object]):
        """Check `call`, then either run() it (two-phase logged) or block and raise.

        The single enforcement path shared by every interceptor (SDK wrapper, MCP proxy).
        """
        result, flags, action_id, runs = self._decide(call)
        if not runs:
            self._block(call, result, flags, action_id)  # raises
        self._log(call, result, flags, action_id, Status.EXECUTING, phase="intent")
        try:
            out = run()
        except Exception as exc:
            self._log(call, result, flags, action_id, Status.ERROR, error=repr(exc))
            raise
        self._log(call, result, flags, action_id, Status.EXECUTED)
        return out

    async def aenforce(self, call: ToolCall, run):
        """Async mirror of enforce() — awaits `run`. For async interceptors (live MCP)."""
        result, flags, action_id, runs = self._decide(call)
        if not runs:
            self._block(call, result, flags, action_id)  # raises
        self._log(call, result, flags, action_id, Status.EXECUTING, phase="intent")
        try:
            out = await run()
        except Exception as exc:
            self._log(call, result, flags, action_id, Status.ERROR, error=repr(exc))
            raise
        self._log(call, result, flags, action_id, Status.EXECUTED)
        return out

    @staticmethod
    def _bind(sig, args, kwargs) -> dict:
        if sig is not None:
            try:
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                mapped = dict(bound.arguments)
                mapped.pop("self", None)
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
