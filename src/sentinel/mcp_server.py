"""A Sentinel-guarded MCP server: expose your tools over MCP with enforcement built in.

`handle_call` is the pure, enforced entry point and has NO dependency on the `mcp`
package — every tool call runs through the same `Sentinel.enforce` path (default-deny,
fail-closed, two-phase audit, kill switch, approvals, monitor mode). `build_server()` /
`run_stdio()` lazily wrap it in a real `mcp` Server so any MCP client can connect; install
the optional extra with `pip install "sentinel[mcp]"`.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from sentinel.models import ToolCall
from sentinel.sentinel import Sentinel


class SentinelMCPServer:
    def __init__(self, sentinel: Sentinel, name: str = "sentinel-guarded"):
        self.sentinel = sentinel
        self.name = name
        self._tools: dict[str, dict] = {}

    def add_tool(self, name: str, fn: Callable, description: str = "",
                 input_schema: Optional[dict] = None) -> Callable:
        self._tools[name] = {
            "fn": fn,
            "description": description,
            "input_schema": input_schema or {"type": "object"},
        }
        return fn

    def tool(self, name: Optional[str] = None, **kw):
        def deco(fn):
            self.add_tool(name or fn.__name__, fn, **kw)
            return fn
        return deco

    def handle_call(self, name: str, arguments: Optional[dict] = None) -> Any:
        """Enforced tool invocation. Raises BlockedError if Sentinel blocks it."""
        arguments = dict(arguments or {})
        if name not in self._tools:
            raise KeyError(f"unknown tool '{name}'")
        fn = self._tools[name]["fn"]
        call = ToolCall(tool=name, args=arguments,
                        agent_id=self.sentinel.agent_id, session_id=self.sentinel.session_id)
        return self.sentinel.enforce(call, lambda: fn(**arguments))

    # --- real MCP wiring (lazy imports; optional `mcp` extra) -------------
    def build_server(self):
        import mcp.types as types  # noqa: PLC0415
        from mcp.server import Server  # noqa: PLC0415

        from sentinel.sentinel import BlockedError

        server = Server(self.name)

        @server.list_tools()
        async def _list_tools():
            return [
                types.Tool(name=n, description=t["description"], inputSchema=t["input_schema"])
                for n, t in self._tools.items()
            ]

        @server.call_tool()
        async def _call_tool(name: str, arguments: dict):
            try:
                result = self.handle_call(name, arguments)
            except BlockedError as exc:
                return [types.TextContent(type="text", text=f"BLOCKED by Sentinel: {exc.reason}")]
            return [types.TextContent(type="text", text=str(result))]

        return server

    async def run_stdio(self) -> None:
        from mcp.server.stdio import stdio_server  # noqa: PLC0415

        server = self.build_server()
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
