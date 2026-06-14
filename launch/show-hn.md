# Show HN post (copy-paste, then add your repo URL)

## Title (keep under ~80 chars)

Show HN: Sentinel – runtime guardrails + audit + kill switch for AI agents

## Body

Sentinel sits between any AI agent and its tools. Every tool call is checked against a
declarative policy *before* it runs, recorded into a tamper-evident (hash-chained) audit
log you can replay and export, and you can stop the agent instantly.

I built it because agents are starting to take real actions — send money, write to prod
DBs, run code — but there's almost no runtime layer that enforces what they're allowed to
do and leaves provable evidence of what they did.

What it does:
- default-deny policy (YAML): allow / block / require-approval, arg thresholds, rate limits
- tamper-evident audit trail (SHA-256 hash chain; `verify` catches any edit/reorder/delete)
- instant kill switch + human-in-the-loop approvals
- heuristic detection: prompt-injection, the "lethal trifecta" (secret → untrusted → egress), PII
- framework-agnostic: plain Python, LangChain, OpenAI Agents, CrewAI, MCP (proxy + server)
- monitor mode (observe-only) so you can shadow a live agent with zero risk first
- exports mapped to EU AI Act Art. 12 / GDPR / NIST / ISO 42001 (indicative, not legal advice)

What it's NOT: it's alpha; it's not a silver bullet for prompt injection (the detector is
heuristic v1); the compliance mappings are engineering aids, not certification.

Apache-2.0, ~80 tests, `pip install` + a CLI + a small dashboard.

Repo: <YOUR-GITHUB-URL>

I'd love feedback — especially from anyone running agents in production: what would you
need before you'd put something like this in front of a real agent?
