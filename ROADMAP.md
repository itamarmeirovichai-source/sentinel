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

## Shipped since the MVP (this session)

- ✅ **MCP-proxy adapter** (`MCPProxy`) over a shared `Sentinel.enforce` path — no bypass.
- ✅ **Two-phase logging** (intent + outcome, linked by `action_id`).
- ✅ **Approval workflow** — `require_approval` parks; operator approves; runs once.
- ✅ **Persisted rate limiter** (SQLite, survives restart).
- ✅ **Dashboard auth** (`SENTINEL_API_TOKEN` on mutating endpoints).
- ✅ **Monitor mode** — observe-only enforcement (the trust bridge); kill switch still enforces.
- ✅ **Sentinel-guarded MCP server** (`SentinelMCPServer`) — expose tools over real `mcp` with enforcement.
- ✅ **OpenTelemetry** — JSON spans + real SDK emission (`record_spans`); Apache-2.0; CI (3.11–3.13); clean wheel/sdist build verified.
- ✅ **Stronger detector** — full lethal-trifecta (untrusted-content tracking), dangerous-arg (cmd/SQL/path/URL) + PII signals.
- ✅ **Retention** — approval TTL + `purge`, rate-limit purge, `sentinel gc` (the audit log itself is never pruned).
- ✅ **Upstream MCP man-in-the-middle** — `AsyncMCPProxy` over a live `mcp.ClientSession` (async `aenforce`).
- ✅ **Concurrency-safe storage** (WAL + busy_timeout); **ruff** lint gate.
- ✅ **EU AI Act Art.12 report** (`export --format art12`); **PyPI release automation** (Trusted Publishing) + PUBLISHING.md.

## Near-term concrete next steps

1. **Publish to PyPI** — automation is ready (`release.yml`); needs your account + a likely rename (`sentinel` is probably taken). See PUBLISHING.md.
2. **Risk scoring over flags** — rank the detector's raw flags into a score; ML behavioral baselining.
3. **Postgres backend** + external anchoring of the chain head (closes tail-truncation).
4. **First design partner** — one real team (or a monitor-mode dogfood). This, not more code, is the bottleneck.

## Honest risk note

Timing is the live risk ([RESEARCH.md](RESEARCH.md) §4): agent adoption is real but
early, and the runtime-control space is consolidating fast (9 acquisitions in 12 months).
The audit/compliance lane is the least-crowded and is pulled forward by the Aug 2026
EU AI Act deadline — but the window is finite. The realistic outcomes are OSS standard-
setter, a regulated-vertical wedge (financial agents first), or build-to-acquire.
