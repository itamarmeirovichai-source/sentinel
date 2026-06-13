# ROADMAP.md — Sentinel

The MVP is the narrow wedge (see [RESEARCH.md](RESEARCH.md) §8). This is where it goes,
and crucially: **every known limitation of the MVP is mapped to a future feature.** That
mapping is the product plan.

## Known limitation → feature (the honest map)

| Today's limitation | What it becomes |
|---|---|
| SDK wrapper can be bypassed (un-wrapped tool) | **Edge / proxy enforcement** — MCP-proxy adapter + egress proxy so interception is unavoidable (the `Interceptor` interface already exists for this) |
| Heuristic detector → false positives | **Risk scoring + anomaly ranking** — rank flags by severity & context instead of binary |
| Blind to agent↔agent interactions | **Trust graph** — the agent reputation layer (Period 2); fed by audit data |
| No drift awareness | **Behavioral baselining** — learn each agent's normal tool/arg distribution |
| In-process latency on every call | **Policy caching + async approval** — keep the hot path fast |
| Compliance mapping is indicative | **Auto-updated compliance templates** — track EU AI Act / ISO 42001 control changes |
| Liability is unaddressed | **Forensic audit + insurance** — the risk data we hold underwrites a policy (Period 3) |
| Single-process, one framework | **Unified control plane** — multi-agent, multi-framework, cross-protocol (MCP + A2A) |
| Tail-truncation of the log isn't caught | **External anchoring** — periodically anchor the chain head (e.g., notarize / append-only object store) |
| `require_approval` just blocks | **Human-in-the-loop approval workflow** — notify, hold, approve/deny, resume |

## The three periods (from the vision, sequenced honestly)

1. **Period 1 — tool that sells today (this MVP):** the compliance flight recorder +
   kill switch. Single-customer value, no network needed.
2. **Period 2 — network (~3 yrs):** the **trust graph**. The audit trail is the data
   moat that makes it possible — we already capture traces, outcomes, and violations in
   a schema designed to feed a reputation score. This is the "FICO for agents" layer the
   research found genuinely open ([RESEARCH.md](RESEARCH.md) §1.E).
3. **Period 3 — settlement (long-term):** integrate (don't rebuild) AP2 / x402 / ACK;
   our neutral risk score underwrites agent-to-agent commerce.

## Near-term concrete next steps

1. **MCP-proxy adapter** — second `Interceptor` implementation; framework-agnostic, no code change. Touches the live MCP-security frontier.
2. **Two-phase logging** — write an intent record before execution and an outcome record after, closing the "process dies mid-call" gap.
3. **Approval workflow** — turn `require_approval` from a block into a real hold/resume.
4. **More detectors** — untrusted-content tracking for the full lethal-trifecta, tool-arg anomaly baselining.
5. **Postgres backend** + retention policy (EU AI Act Art. 12 ≥ 6 months).
6. **Package & publish** — `pip install sentinel`, quickstart, OSS license, OpenTelemetry GenAI export so we're interoperable from day one.

## Honest risk note

Timing is the live risk ([RESEARCH.md](RESEARCH.md) §4): agent adoption is real but
early, and the runtime-control space is consolidating fast (9 acquisitions in 12 months).
The audit/compliance lane is the least-crowded and is pulled forward by the Aug 2026
EU AI Act deadline — but the window is finite. The realistic outcomes are OSS standard-
setter, a regulated-vertical wedge (financial agents first), or build-to-acquire.
