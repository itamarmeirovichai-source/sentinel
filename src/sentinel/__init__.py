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
from sentinel.approvals import Approvals
from sentinel.ratelimit import SqliteRateLimiter
from sentinel.sentinel import Sentinel, BlockedError
from sentinel.mcp_proxy import MCPProxy
from sentinel.mcp_server import SentinelMCPServer

__version__ = "0.1.0"

__all__ = [
    "Sentinel",
    "BlockedError",
    "MCPProxy",
    "SentinelMCPServer",
    "Policy",
    "PolicyResult",
    "AuditLog",
    "VerifyResult",
    "KillSwitch",
    "Detector",
    "Approvals",
    "SqliteRateLimiter",
    "ToolCall",
    "Decision",
    "Status",
    "Flag",
    "CheckResult",
    "AuditRecord",
    "__version__",
]
