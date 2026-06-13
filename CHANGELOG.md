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

### Interception
- **SDK wrapper** (`@sentinel.guard`) — the default interceptor.
- **MCP proxy** (`MCPProxy`) — second interceptor over the same `enforce()` path; no bypass.

### Control plane
- FastAPI **dashboard** + API: live feed, integrity verify, policy editor, kill switch, approvals.
- **API auth** via `SENTINEL_API_TOKEN` on mutating endpoints; `sentinel serve` auto-generates one.
- **Human-in-the-loop approvals**: `require_approval` parks a call; operator approves; next identical call runs once.
- Persistent **rate limiter** (survives restart / shared across processes).

### Tooling
- CLI: `serve | verify | export [--format json|otel] | kill | unkill | approvals | approve | demo`.
- **OpenTelemetry GenAI** export (`gen_ai.*` + `sentinel.*` attributes).
- CI (GitHub Actions, py3.11–3.13). Apache-2.0.

51 tests passing.
