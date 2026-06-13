"""Sentinel-guarded MCP server contract.

`handle_call` is the pure, enforced entry point (no mcp dependency); `build_server()`
wraps it in a real `mcp` Server. Core tests hit handle_call; the mcp wiring is smoke-tested.
"""
import pytest

from sentinel.audit import AuditLog
from sentinel.detector import Detector
from sentinel.killswitch import KillSwitch
from sentinel.mcp_server import SentinelMCPServer
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
"""


def build(tmp_path):
    db = str(tmp_path / "ms.db")
    s = Sentinel(policy=Policy.from_yaml(POLICY), audit=AuditLog(db),
                 killswitch=KillSwitch(db), detector=Detector())
    srv = SentinelMCPServer(s)
    srv.add_tool("get_quote", lambda symbol: {"price": 1, "symbol": symbol})
    srv.add_tool("delete_db", lambda: "boom")
    return srv, s


def test_allowed_tool_runs_and_is_logged(tmp_path):
    srv, s = build(tmp_path)
    out = srv.handle_call("get_quote", {"symbol": "AAPL"})
    assert out["symbol"] == "AAPL"
    assert s.audit.records()[-1].status == Status.EXECUTED.value


def test_denied_tool_blocked_unknown_tool_keyerror(tmp_path):
    srv, s = build(tmp_path)
    with pytest.raises(BlockedError):
        srv.handle_call("delete_db", {})        # default-deny
    with pytest.raises(KeyError):
        srv.handle_call("nonexistent", {})


def test_kill_switch_blocks_the_mcp_server(tmp_path):
    srv, s = build(tmp_path)
    s.killswitch.arm("*", reason="x")
    with pytest.raises(BlockedError):
        srv.handle_call("get_quote", {"symbol": "AAPL"})


def test_build_real_mcp_server_smoke(tmp_path):
    pytest.importorskip("mcp")
    srv, _ = build(tmp_path)
    server = srv.build_server()
    assert server is not None
