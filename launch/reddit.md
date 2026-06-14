# Reddit post (good fits: r/AI_Agents, r/LLMDevs, r/LocalLLaMA)

## Title

I built an open-source runtime guardrail + audit + kill switch for AI agents (Apache-2.0)

## Body

I kept seeing the same gap: people are giving agents real tools — payments, DB writes,
shell, email — but there's almost no layer that enforces what the agent is *allowed* to do
at runtime, or leaves provable evidence of what it did. So I built **Sentinel**.

It sits between any agent and its tools and, on every tool call:
- checks a default-deny YAML policy (allow / block / require human approval / rate-limit)
- writes a **tamper-evident** audit record (hash chain — editing it is detectable)
- lets you hit a **kill switch** to stop the agent instantly
- flags prompt-injection, PII, and the "lethal trifecta" (secret → untrusted input → egress)

It's framework-agnostic (plain Python decorator, LangChain, OpenAI Agents, CrewAI, MCP),
has a **monitor mode** that only observes (zero risk to your agent), a small dashboard, and
can export audit reports mapped to EU AI Act / GDPR / NIST / ISO 42001 (indicative, not
legal advice).

Honest status: it's **alpha**, the injection detector is heuristic v1 (not a silver
bullet), and I have 0 production users yet — which is exactly why I'm posting.

Repo: https://github.com/itamarmeirovichai-source/sentinel

If you run agents: would you actually use something like this? What's missing for you?
