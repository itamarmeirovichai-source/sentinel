"""Micro-benchmark: Sentinel's per-call overhead (closes the PRD latency success metric).

Times N allowed tool calls guarded by Sentinel vs. raw, on a throwaway DB. The guarded
path includes the policy check, the detector, and TWO durable audit writes (intent +
outcome) — so most of the overhead is durable logging, not the decision itself.

Run:  python examples/benchmark.py
"""
from __future__ import annotations

import os
import tempfile
import time

from sentinel import AuditLog, Detector, KillSwitch, Policy, Sentinel


def run(n: int = 2000) -> float:
    db = os.path.join(tempfile.mkdtemp(), "bench.db")
    s = Sentinel(policy=Policy.from_yaml("version: 1\ndefault: allow\nrules: []\n"),
                 audit=AuditLog(db), killswitch=KillSwitch(db), detector=Detector())

    def raw(x):
        return x

    guarded = s.guard(raw)

    t0 = time.perf_counter()
    for i in range(n):
        raw(i)
    t_raw = time.perf_counter() - t0

    t0 = time.perf_counter()
    for i in range(n):
        guarded(i)
    t_guard = time.perf_counter() - t0

    per_call_ms = (t_guard - t_raw) / n * 1000
    print(f"calls:          {n}")
    print(f"raw total:      {t_raw * 1000:8.1f} ms")
    print(f"guarded total:  {t_guard * 1000:8.1f} ms")
    print(f"overhead/call:  {per_call_ms:7.3f} ms  (policy + detector + 2 durable audit writes)")
    print(f"audit records:  {len(s.audit.records())}  (2 per call: intent + outcome)")
    return per_call_ms


if __name__ == "__main__":
    run()
