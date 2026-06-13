# Changelog

## 0.1.0 (unreleased)

MVP of the audit/flight-recorder wedge, plus first hardening pass.

### Core
- Declarative, default-deny **policy engine** (YAML): glob + arg comparators + rate limits.
- Append-only, hash-chained **audit trail** (SQLite) with `verify` (tamper-evident) and a compliance `export`.
- **Two-phase logging**: intent (pre-exec) + outcome (post-exec) records linked by `action_id`.
- Persisted **kill switch** (global / per-agent) and `fail-closed` enforcement.
- **Detector v1** heuristics: lethal-trifecta, off-baseline, injection signatures.
- Secret **redaction** at write time; compliance mapping (EU AI Act Art. 12, OWASP Agentic).
- **Monitor mode** (observe-only): logs the would-be verdict, never blocks — but the kill switch still enforces. The trust bridge before flipping to enforcement.

### Interception
- **SDK wrapper** (`@sentinel.guard`) — the default interceptor.
- **MCP proxy** (`MCPProxy`) — second interceptor over the same `enforce()` path; no bypass.
- **Sentinel-guarded MCP server** (`SentinelMCPServer`) — expose tools over real MCP with enforcement built in (optional `mcp` extra).

### Control plane
- FastAPI **dashboard** + API: live feed, integrity verify, policy editor, kill switch, approvals.
- **API auth** via `SENTINEL_API_TOKEN` on mutating endpoints; `sentinel serve` auto-generates one.
- **Read-endpoint protection** (`SENTINEL_API_PROTECT_READS`) — gate the sensitive audit reads behind the token too.
- **Human-in-the-loop approvals**: `require_approval` parks a call; operator approves; next identical call runs once.
- Persistent **rate limiter** (survives restart / shared across processes).

### Tooling
- CLI: `serve | verify | export [--format json|otel] | kill | unkill | approvals | approve | demo`.
- **OpenTelemetry GenAI** export — JSON spans (`gen_ai.*` + `sentinel.*`) and real SDK span emission (`record_spans`, optional `otel` extra).
- Optional extras: `pip install "sentinel[mcp,otel]"`. Builds a clean wheel/sdist.
- CI (GitHub Actions, py3.11–3.13) with a ruff lint gate. Concurrency-safe SQLite (WAL + busy_timeout). Apache-2.0.

61 tests passing.
