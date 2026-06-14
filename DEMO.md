# DEMO.md — running Sentinel end-to-end

## Setup (once)

```bash
cd sentinel
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env      # optional; sensible defaults work without it
```

## 1. The end-to-end demo (the headline)

```bash
sentinel demo            # a GENERIC agent; vertical example: python examples/trading_agent.py
```

A generic AI agent runs **through** Sentinel (the trading version shows the same controls
for a financial agent). You'll see the same scenarios either way:

| Scenario | Tool call | What Sentinel does |
|---|---|---|
| Normal trading | `get_quote`, `get_balance`, `place_order($100)` | **allowed** + logged |
| Oversized order | `place_order(TSLA, $5000)` | **blocked** — policy needs approval above $500 |
| Suspicious (trifecta) | `read_api_secret()` then `http_post(...)` | **allowed but FLAGGED** — secret-then-egress |
| Suspicious (injection) | `get_news("…ignore previous instructions…")` | **allowed but FLAGGED** — injection signature |
| Destructive | `delete_account()` | **blocked** — forbidden by policy |
| Kill switch | `get_quote()` after `kill` | **blocked** — agent stopped |

It ends by printing the audit summary and confirming the hash chain is intact.

## 2. Prove the audit is tamper-evident

```bash
sentinel verify          # -> ok: true

# now tamper with the SQLite log directly (simulating an attacker hiding a trade)
python - <<'PY'
import sqlite3
c = sqlite3.connect("data/sentinel.db")
c.execute("UPDATE audit SET args=? WHERE seq=4", ('{"amount": 1}',))
c.commit(); c.close()
PY

sentinel verify          # -> ok: false, first_bad_seq: 4  (exit code 1)
```

This is the wedge: you cannot quietly rewrite what the agent did.

## 3. Export a compliance report

```bash
sentinel export --out report.json
```

Every record carries an integrity status plus `eu_ai_act_art12` and OWASP Agentic
tags — hand it to a compliance reviewer or auditor.

## 4. The dashboard (live control plane)

```bash
sentinel serve           # -> http://127.0.0.1:8787
```

The dashboard polls the same audit DB, so:

- **watch** actions land live with their decision, status, flags, and matched rule;
- click **VERIFY CHAIN** to re-check integrity on demand;
- click **KILL ALL** — then in another terminal run `sentinel demo` again: the agent
  is **blocked on its next call**, because the kill state is shared through SQLite.
  This is a real cross-process kill switch, not a toy.
- edit the **policy** YAML and save (validated before it's written).

> Note: the live dashboard couldn't be auto-screenshotted here because the preview
> sandbox blocks the project's `.venv`; it runs fine under plain `sentinel serve`,
> and its endpoints are covered by `tests/test_api.py`.

## 5. Measure the overhead

```bash
python examples/benchmark.py    # ~0.4 ms/call on a dev laptop (incl. 2 durable audit writes)
```

## 6. See the compliance mapping

```bash
sentinel compliance --all                  # full/partial/none across 6 regulations
sentinel compliance --framework eu_ai_act  # mapping + your audit evidence
```

