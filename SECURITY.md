# SECURITY.md — Sentinel

Sentinel sits on the most sensitive control point an organization has — between an
autonomous agent and its real-world tools. So Sentinel itself is a high-value target.
We take that seriously.

## Design posture (enforced in code + tests)

- **Fail-closed** — any error in the decision core resolves to *block*, never execute
  (`test_fail_closed_when_policy_errors`).
- **Default-deny** — an action with no matching allow rule is blocked
  (`test_default_deny_blocks_unknown_tool`).
- **Tamper-evident audit** — hash-chained log; edits/reorders/deletes are detected
  (`test_tampering_with_a_row_is_detected`, `test_deleting_a_middle_row_is_detected`).
- **Redaction at write time** — secret-shaped values never land in the log
  (`test_secrets_are_redacted_before_storage`).
- **Persisted, fail-closed kill switch** — survives restart (`test_persists_across_instances`).
- **No unsafe sinks** — `yaml.safe_load` only; no `eval`/`exec`/`subprocess`/`shell=True`.

## Self-check performed (2026-06-13)

| Check | Result |
|---|---|
| Secrets / DB / venv excluded from git | ✅ `.env`, `data/`, `.venv` git-ignored; nothing sensitive tracked |
| Real secrets in source | ✅ none (only obviously-fake demo fixtures in `examples/`) |
| Unsafe sinks (`eval`/`exec`/`yaml.load`/`shell=True`) | ✅ none found |
| Tamper detection | ✅ verified live (edit at seq N → `verify` fails at seq N) |
| Sensitive read endpoints lockable | ✅ `SENTINEL_API_PROTECT_READS` gates GET `/api/*` behind the token |
| Storage concurrency | ✅ WAL + busy_timeout (avoids "database is locked") |
| Static lint gate | ✅ ruff clean (E,F,W,I,B) in CI |

## Known limitations (tracked in [ROADMAP.md](ROADMAP.md))

- **SDK-wrapper bypass** — only wrapped tools are governed; an un-wrapped call escapes.
  Mitigation path: MCP-proxy / egress enforcement.
- **Tail-truncation** — deleting the *end* of the log isn't caught by the chain alone.
  Mitigation path: external anchoring of the chain head.
- **Heuristic detector** — v1 is rule-based and will have false positives/negatives.

## Threat model

See [ARCHITECTURE.md](ARCHITECTURE.md) §6 for the full table (T1–T8).

## Reporting

This is an MVP / research project. Security issues: open an issue or contact the
maintainer. Do not include live secrets in reports.
