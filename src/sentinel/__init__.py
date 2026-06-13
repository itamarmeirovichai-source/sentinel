"""Sentinel — compliance-grade flight recorder + kill switch for AI agents.

Typical use:

    from sentinel import Sentinel
    s = Sentinel.from_files(policy="policies/example.yaml", db="data/sentinel.db")

    @s.guard
    def place_order(symbol: str, amount: float): ...
"""

from sentinel.models import (
    AuditRecord,
    CheckResult,
    Decision,
    Flag,
    Status,
    ToolCall,
)
from sentinel.policy import Policy, PolicyResult
from sentinel.audit import AuditLog, VerifyResult
from sentinel.killswitch import KillSwitch
from sentinel.detector import Detector
from sentinel.sentinel import Sentinel, BlockedError

__version__ = "0.1.0"

__all__ = [
    "Sentinel",
    "BlockedError",
    "Policy",
    "PolicyResult",
    "AuditLog",
    "VerifyResult",
    "KillSwitch",
    "Detector",
    "ToolCall",
    "Decision",
    "Status",
    "Flag",
    "CheckResult",
    "AuditRecord",
    "__version__",
]
