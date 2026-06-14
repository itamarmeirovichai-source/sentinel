# X / Twitter launch thread (copy-paste; add repo URL + a 20s screen recording of the dashboard)

1/
AI agents are starting to send money, write to prod, and run code — with almost nothing
enforcing what they're allowed to do, or proving what they did.

So I built Sentinel: an open-source runtime guardrail + audit + kill switch for AI agents. 🧵

2/
It sits between any agent and its tools. Every tool call is checked against your policy
*before* it runs:
✅ allowed → runs
🟠 over a limit → needs human approval
🔴 forbidden → blocked
…and you can kill the agent instantly.

3/
Everything is written to a tamper-evident audit log — a SHA-256 hash chain.
Try to quietly edit what the agent did, and `verify` catches it.
That's the part regulators (EU AI Act Art. 12) and your boss actually want.

4/
It flags suspicious behavior too: prompt-injection, PII in arguments, and the "lethal
trifecta" (read a secret → ingest untrusted content → send it out).
Heuristic v1 — flags, doesn't pretend to be a silver bullet.

5/
Framework-agnostic: plain Python (@guard), LangChain, OpenAI Agents, CrewAI, or MCP
(proxy + server). And a "monitor mode" that only watches — so you can shadow a live agent
with zero risk before you let it block anything.

6/
It's alpha, Apache-2.0, ~80 tests, pip-installable, with a tiny dashboard.
Repo: <YOUR-GITHUB-URL>

If you build agents: what would you need before you'd put a layer like this in front of a
real one? Genuinely asking.
