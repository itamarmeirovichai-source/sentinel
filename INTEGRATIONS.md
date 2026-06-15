# INTEGRATIONS.md — add Sentinel to any AI agent

Sentinel is **framework-agnostic**. Whatever you build your agent with, the same core
(`Sentinel.enforce`) governs each tool call — default-deny policy, human-in-the-loop
approvals, kill switch, tamper-evident audit, and injection/exfil/PII detection. Start
from [`policies/starter.yaml`](policies/starter.yaml) and tune to your tools.

```python
from sentinel import Sentinel
sentinel = Sentinel.from_files(policy="policies/starter.yaml", db="data/sentinel.db")
```

## Plain Python functions (works everywhere)

```python
@sentinel.guard
def send_email(to, subject, body): ...

# …or guard a whole toolset at once:
tools = sentinel.wrap_all({"send_email": send_email, "search_web": search_web})
tools["search_web"]("q3 revenue")          # checked, logged, killable
```

## LangChain / LangGraph

A LangChain tool wraps a function — guard that function:

```python
from langchain_core.tools import tool

@tool
@sentinel.guard
def search(q: str) -> str:
    ...
```
For pre-built tools, wrap the underlying callable (`my_tool.func = sentinel.guard(my_tool.func)`).

## OpenAI Agents SDK / function calling

You dispatch tool calls yourself, so route them through guarded callables:

```python
guarded = sentinel.wrap_all({name: fn for name, fn in my_tools.items()})
# in your tool-dispatch loop:
result = guarded[tool_name](**tool_args)   # raises BlockedError if Sentinel blocks it
```

## CrewAI / LlamaIndex / Autogen / custom loops

Same pattern — wrap the underlying tool callables with `@sentinel.guard` or `wrap_all(...)`.
Sentinel doesn't care how the LLM decides to call a tool; it governs the call itself.

## MCP (Model Context Protocol)

```python
# (a) Guard tools you EXPOSE over MCP:
from sentinel import SentinelMCPServer
srv = SentinelMCPServer(sentinel)
srv.add_tool("search", search)
await srv.run_stdio()          # any MCP client now talks to a guarded server

# (b) Sit in front of an UPSTREAM MCP server (man-in-the-middle):
from sentinel import AsyncMCPProxy
proxy = AsyncMCPProxy(sentinel, session)        # session = an mcp.ClientSession
await proxy.call_tool("search", {"q": "..."})   # enforced, then forwarded upstream
```
Install the MCP extra: `pip install "guardledger[mcp]"`.

## Multi-agent / per-agent control

Give each agent its own `agent_id` (and `session_id`) so the audit, kill switch, and
detector are scoped per agent:

```python
sentinel = Sentinel.from_files(policy="policies/starter.yaml", db="data/sentinel.db",
                               agent_id="support-bot", session_id="conv-123")
sentinel.killswitch.arm("support-bot")   # stop just this agent; "*" stops all
```

## What you get, regardless of framework

Default-deny enforcement · human approvals · instant kill switch · tamper-evident audit ·
injection / lethal-trifecta / PII flags · monitor mode (observe-only) · OpenTelemetry +
EU AI Act / GDPR / NIST / ISO 42001 / Colorado / SEC-FINRA compliance reports. Configure
once, reuse for every agent you build.
