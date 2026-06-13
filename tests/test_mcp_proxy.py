"""MCP-proxy interceptor contract — written before the implementation.

Proves the `Interceptor` abstraction: the proxy enforces via the same Sentinel core as
the SDK wrapper (default-deny, fail-closed, two-phase audit, kill switch), but nothing
the agent calls can bypass it.
"""
import asyncio

import pytest

from sentinel.audit import AuditLog
from sentinel.detector import Detector
from sentinel.killswitch import KillSwitch
from sentinel.mcp_proxy import AsyncMCPProxy, MCPProxy
from sentinel.models import Status
from sentinel.policy import Policy
from sentinel.sentinel import BlockedError, Sentinel

POLICY = """
version: 1
default: deny
rules:
  - id: reads
    match: { tool: ["get_*"] }
    action: allow
  - id: forbid
    match: { tool: ["delete_*"] }
    action: block
"""


class FakeUpstream:
    def __init__(self):
        self.calls = []

    def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return {"tool": name, "args": arguments, "result": "ok"}


def build(tmp_path):
    db = str(tmp_path / "m.db")
    s = Sentinel(policy=Policy.from_yaml(POLICY), audit=AuditLog(db),
                 killswitch=KillSwitch(db), detector=Detector(), agent_id="mcp-agent")
    up = FakeUpstream()
    return MCPProxy(s, up), s, up


def test_allowed_tool_is_forwarded_and_logged(tmp_path):
    proxy, s, up = build(tmp_path)
    out = proxy.call_tool("get_quote", {"symbol": "AAPL"})
    assert out["result"] == "ok"
    assert up.calls == [("get_quote", {"symbol": "AAPL"})]
    assert s.audit.records()[-1].status == Status.EXECUTED.value


def test_blocked_tool_is_never_forwarded(tmp_path):
    proxy, s, up = build(tmp_path)
    with pytest.raises(BlockedError):
        proxy.call_tool("delete_db", {})
    assert up.calls == []  # upstream never reached
    assert s.audit.records()[-1].status == Status.BLOCKED.value


def test_default_deny_unknown_tool(tmp_path):
    proxy, s, up = build(tmp_path)
    with pytest.raises(BlockedError):
        proxy.call_tool("transfer_funds", {"amount": 1})
    assert up.calls == []


def test_kill_switch_blocks_the_proxy(tmp_path):
    proxy, s, up = build(tmp_path)
    assert proxy.call_tool("get_quote", {"symbol": "AAPL"})["result"] == "ok"
    s.killswitch.arm("*", reason="incident")
    with pytest.raises(BlockedError):
        proxy.call_tool("get_quote", {"symbol": "AAPL"})
    assert s.audit.records()[-1].status == Status.KILLED.value


def test_upstream_can_be_a_plain_callable(tmp_path):
    db = str(tmp_path / "m.db")
    s = Sentinel(policy=Policy.from_yaml(POLICY), audit=AuditLog(db),
                 killswitch=KillSwitch(db), detector=Detector())
    seen = []

    def up(name, arguments):
        seen.append(name)
        return "done"

    proxy = MCPProxy(s, up)
    assert proxy.call_tool("get_x", {}) == "done"
    assert seen == ["get_x"]


class AsyncUpstream:
    def __init__(self):
        self.calls = []

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return {"ok": name}


def test_async_proxy_allows_then_blocks(tmp_path):
    db = str(tmp_path / "am.db")
    s = Sentinel(policy=Policy.from_yaml(POLICY), audit=AuditLog(db),
                 killswitch=KillSwitch(db), detector=Detector())
    up = AsyncUpstream()
    proxy = AsyncMCPProxy(s, up)

    out = asyncio.run(proxy.call_tool("get_quote", {"symbol": "AAPL"}))
    assert out == {"ok": "get_quote"}
    assert up.calls == [("get_quote", {"symbol": "AAPL"})]
    assert s.audit.records()[-1].status == Status.EXECUTED.value

    with pytest.raises(BlockedError):
        asyncio.run(proxy.call_tool("delete_db", {}))
    assert up.calls == [("get_quote", {"symbol": "AAPL"})]  # blocked -> upstream untouched
