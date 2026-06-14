# Changelog

## 0.1.0 (unreleased)

MVP of the audit/flight-recorder wedge, plus first hardening pass.

### Core
- Declarative, default-deny **policy engine** (YAML): glob + arg comparators + rate limits.
- Append-only, hash-chained **audit trail** (SQLite) with `verify` (tamper-evident) and a compliance `export`.
- **Two-phase logging**: intent (pre-exec) + outcome (post-exec) records linked by `action_id`.
- Persisted **kill switch** (global / per-agent) and `fail-closed` enforcement.
- **Detector** heuristics: full lethal-trifecta (untrusted-content tracking), off-baseline, injection signatures, dangerous-arg (cmd/SQL/path/URL), PII-in-arg.
- Secret **redaction** at write time; compliance mapping (EU AI Act Art. 12, OWASP Agentic).
- **Monitor mode** (observe-only): logs the would-be verdict, never blocks — but the kill switch still enforces. The trust bridge before flipping to enforcement.

### Interception
- **SDK wrapper** (`@sentinel.guard`) — the default interceptor.
- **MCP proxy** (`MCPProxy`) — second interceptor over the same `enforce()` path; no bypass.
- **Sentinel-guarded MCP server** (`SentinelMCPServer`) — expose tools over real MCP with enforcement built in (optional `mcp` extra).
- **Upstream MCP proxy** (`AsyncMCPProxy`) — man-in-the-middle over a live `mcp.ClientSession` (async `aenforce`).
- **Framework-agnostic by default**: generic `policies/starter.yaml` + a generic demo (`sentinel demo`); `Sentinel.wrap_all()` guards a whole toolset; INTEGRATIONS.md covers plain functions / LangChain / OpenAI Agents / CrewAI / MCP. (Trading is now just a vertical example.)

### Control plane
- FastAPI **dashboard** + API: live feed, integrity verify, policy editor, kill switch, approvals.
- **API auth** via `SENTINEL_API_TOKEN` on mutating endpoints; `sentinel serve` auto-generates one.
- **Read-endpoint protection** (`SENTINEL_API_PROTECT_READS`) — gate the sensitive audit reads behind the token too.
- **Human-in-the-loop approvals**: `require_approval` parks a call; operator approves; next identical call runs once.
- Persistent **rate limiter** (survives restart / shared across processes).

### Tooling
- CLI: `serve | verify | export [--format json|otel] | kill | unkill | approvals | approve | demo`.
- **Retention**: approval TTL + `sentinel gc` purges stale approvals / rate-limit state (audit log untouched).
- **Multi-framework compliance mapping** (`sentinel compliance`): EU AI Act, GDPR, NIST AI RMF, ISO 42001, Colorado AI Act, SEC/FINRA — honest full/partial/none coverage (COMPLIANCE.md).
- **EU AI Act Art.12 report** (`export --format art12`); OpenTelemetry GenAI export (JSON spans + real SDK emission).
- **PyPI release automation** (Trusted Publishing) — see PUBLISHING.md.
- Optional extras: `pip install "sentinel[mcp,otel]"`. Clean wheel/sdist build.
- Pre-launch security: dashboard HTML-escaping (anti-XSS), disclaimers (alpha / not legal advice), concurrency-safe audit append.
- CI (GitHub Actions, py3.11–3.13) with a ruff lint gate. Concurrency-safe SQLite (WAL + busy_timeout). Apache-2.0.

78 tests passing.
