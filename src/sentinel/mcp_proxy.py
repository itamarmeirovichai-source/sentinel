"""MCP-proxy interceptor — a second `Interceptor` implementation.

It sits between an MCP client and upstream MCP server(s). Every tool call runs through
the same `Sentinel.enforce()` path as the SDK wrapper (default-deny, fail-closed,
two-phase audit, kill switch, approvals) before being forwarded upstream. Unlike the
SDK wrapper there is no un-wrapped path — the agent can only reach tools *through* here.

`upstream` is anything exposing `call_tool(name, arguments)` (e.g. a real
`mcp.ClientSession`) or a plain `callable(name, arguments)`. Keeping enforcement
transport-agnostic makes it fully testable; wiring this to a live MCP stdio/HTTP
transport (so an MCP client connects to Sentinel, which forwards to real servers) is a
thin shell on top — see ROADMAP.md.
"""
from __future__ import annotations

from typing import Any, Optional

from sentinel.models import ToolCall
from sentinel.sentinel import Sentinel


class MCPProxy:
    def __init__(self, sentinel: Sentinel, upstream: Any,
                 agent_id: Optional[str] = None, session_id: Optional[str] = None):
        self.sentinel = sentinel
        self.upstream = upstream
        self.agent_id = agent_id or sentinel.agent_id
        self.session_id = session_id or sentinel.session_id

    def _forward(self, name: str, arguments: dict) -> Any:
        if hasattr(self.upstream, "call_tool"):
            return self.upstream.call_tool(name, arguments)
        return self.upstream(name, arguments)

    def call_tool(self, name: str, arguments: Optional[dict] = None) -> Any:
        arguments = dict(arguments or {})
        call = ToolCall(tool=name, args=arguments,
                        agent_id=self.agent_id, session_id=self.session_id)
        return self.sentinel.enforce(call, lambda: self._forward(name, arguments))
