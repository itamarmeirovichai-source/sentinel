"""Core data models shared across Sentinel components.

Plain dataclasses + string enums so everything is trivially JSON-serializable
(important: the audit hash chain hashes a canonical JSON form of each record).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Decision(str, Enum):
    """The policy verdict for a single attempted action."""

    ALLOW = "allow"
    BLOCK = "block"
    REQUIRE_APPROVAL = "require_approval"


class Status(str, Enum):
    """What actually happened to the action after the verdict."""

    EXECUTED = "executed"
    BLOCKED = "blocked"
    ERROR = "error"
    PENDING_APPROVAL = "pending_approval"
    KILLED = "killed"


@dataclass
class ToolCall:
    """A single attempted tool invocation by an agent — the unit Sentinel governs."""

    tool: str
    args: dict[str, Any] = field(default_factory=dict)
    agent_id: str = "default"
    session_id: str = "default"


@dataclass
class Flag:
    """A heuristic suspicion raised by the detector. Recorded; does not block by default."""

    rule: str
    severity: str  # "info" | "warn" | "high"
    detail: str

    def as_str(self) -> str:
        return f"{self.rule}[{self.severity}]: {self.detail}"


@dataclass
class CheckResult:
    """The combined verdict returned by Sentinel.check() before a tool runs."""

    decision: Decision
    rule_id: Optional[str]
    reason: str
    flags: list[Flag] = field(default_factory=list)


@dataclass
class AuditRecord:
    """One immutable, hash-chained entry in the flight recorder.

    `hash` is computed by AuditLog as sha256(prev_hash + canonical_json(payload)),
    where payload is every field except `hash` itself.
    """

    seq: int
    ts: float
    agent_id: str
    session_id: str
    tool: str
    args: dict[str, Any]
    decision: str
    policy_rule: Optional[str]
    reason: str
    flags: list[str]
    status: str
    error: Optional[str]
    compliance: dict[str, Any]
    prev_hash: str
    hash: str = ""
