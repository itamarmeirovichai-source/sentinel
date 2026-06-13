# Sentinel

**The compliance-grade flight recorder + kill switch for AI agents.**

Sentinel sits between an autonomous AI agent and its tools. Every action is
checked against your policy *before* it runs, recorded into a tamper-evident
audit trail you can replay and export as compliance evidence, and you can stop
the agent instantly. The point is provability: knowing — and being able to
prove — exactly what your agent did.

> Status: **MVP / Phase 3.** This is the narrow wedge of a larger vision (see
> [RESEARCH.md](RESEARCH.md) and [ROADMAP.md](ROADMAP.md)). It is **not** another
> prompt-injection filter — it leads with deterministic enforcement + provable audit.

## Why

Teams can't get sign-off to let agents touch high-stakes systems (trading,
billing, prod DBs) because there's no audit-grade record of what the agent did,
no enforcement of what it's allowed to do, and no instant stop. Regulation now
forces the issue: **EU AI Act Article 12** mandates automatic event logging for
high-risk systems (enforcement from **2026-08-02**). Sentinel is the layer that
produces that evidence. Full market/competitive analysis: [RESEARCH.md](RESEARCH.md).

## Core guarantees

- **Default-deny** — an action with no matching allow rule is blocked.
- **Fail-closed** — if the decision core itself errors, the action is blocked, not run.
- **Tamper-evident** — the audit log is hash-chained; any edit/reorder/delete is detectable via `verify`.

## Architecture (one glance)

```
agent ─tool_call─► Interceptor ─► KillSwitch? ─► Detector(flags) ─► Policy(default-deny)
                                                                         │
                              audit (hash-chained, redacted) ◄── execute / block
```

Interception is an SDK wrapper today, behind an `Interceptor` interface so an
MCP-proxy adapter slots in later without touching the policy/audit/kill core.
Details + threat model: [ARCHITECTURE.md](ARCHITECTURE.md).

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# run the tests (security-critical core is tested first)
pytest

# run the end-to-end demo (see DEMO.md)
python examples/trading_agent.py

# launch the control API + dashboard
sentinel serve            # then open http://127.0.0.1:8787
```

## Usage sketch

```python
from sentinel import Sentinel

sentinel = Sentinel.from_files(policy="policies/example.yaml", db="data/sentinel.db")

@sentinel.guard                      # every call is checked, logged, killable
def place_order(symbol: str, amount: float): ...

# over-policy / killed / suspicious calls raise BlockedError and are recorded;
# allowed calls run normally and are recorded with their outcome.
```

## Documents

| File | What |
|---|---|
| [RESEARCH.md](RESEARCH.md) | Market & competitive research, wedge recommendation |
| [PRD.md](PRD.md) | Product requirements for this MVP |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, data flow, threat model |
| [DECISIONS.md](DECISIONS.md) | Decision log |
| [DEMO.md](DEMO.md) | How to run the end-to-end demo |
| [ROADMAP.md](ROADMAP.md) | What's next, and the known-limitation → feature map |

## License

Apache-2.0.
