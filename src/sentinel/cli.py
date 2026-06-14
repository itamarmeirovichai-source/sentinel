"""`sentinel` command-line entry point."""
from __future__ import annotations

import argparse
import json
import os
import runpy
import sys

from sentinel.config import Config


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="sentinel", description="Sentinel control plane")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("serve", help="run the control API + dashboard")
    sub.add_parser("verify", help="verify the audit log integrity")
    ex = sub.add_parser("export", help="export a compliance report")
    ex.add_argument("--out", default=None, help="write the report to this file")
    ex.add_argument("--format", choices=["json", "otel", "art12"], default="json",
                    help="json report (default), OpenTelemetry GenAI spans, or EU AI Act Art.12 report")
    kill = sub.add_parser("kill", help="arm the kill switch")
    kill.add_argument("--scope", default="*")
    kill.add_argument("--reason", default="armed via cli")
    unkill = sub.add_parser("unkill", help="disarm the kill switch")
    unkill.add_argument("--scope", default="*")
    sub.add_parser("approvals", help="list pending human-in-the-loop approvals")
    approve = sub.add_parser("approve", help="approve a pending action by id")
    approve.add_argument("id")
    gc = sub.add_parser("gc", help="purge stale approvals + rate-limit state (not the audit log)")
    gc.add_argument("--older-than-days", type=float, default=7)
    comp = sub.add_parser("compliance", help="map Sentinel to AI/data regulations (indicative)")
    comp.add_argument("--framework", default=None, help="framework key (e.g. eu_ai_act, gdpr, sec_finra)")
    comp.add_argument("--all", action="store_true", help="coverage summary across all frameworks")
    comp.add_argument("--out", default=None, help="write the report to this file")
    sub.add_parser("demo", help="run the example trading agent end-to-end")

    args = parser.parse_args(argv)
    cfg = Config.from_env()

    if args.cmd == "serve":
        import secrets

        import uvicorn

        from sentinel.api import create_app

        if not cfg.api_token:
            cfg.api_token = secrets.token_urlsafe(24)
            print(f"Generated control token (paste into the dashboard): {cfg.api_token}")
        print(f"Sentinel dashboard -> http://{cfg.api_host}:{cfg.api_port}")
        uvicorn.run(create_app(cfg), host=cfg.api_host, port=cfg.api_port)

    elif args.cmd == "verify":
        from sentinel.audit import AuditLog

        v = AuditLog(cfg.db_path).verify()
        print(json.dumps({"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message}, indent=2))
        sys.exit(0 if v.ok else 1)

    elif args.cmd == "export":
        from sentinel.audit import AuditLog

        log = AuditLog(cfg.db_path)
        if args.format == "otel":
            from sentinel.otel import to_otel_spans

            spans = to_otel_spans(log.records())
            text, count = json.dumps({"spans": spans}, indent=2, default=str), len(spans)
        elif args.format == "art12":
            import time as _time

            from sentinel.compliance import art12_report

            v = log.verify()
            report = art12_report(log.records(), verify_ok=v.ok, generated_at=_time.time(),
                                  system_name=os.getenv("SENTINEL_SYSTEM_NAME", "unspecified AI system"),
                                  provider=os.getenv("SENTINEL_PROVIDER", "unspecified"))
            text, count = json.dumps(report, indent=2, default=str), report["event_count"]
        else:
            report = log.export()
            text, count = json.dumps(report, indent=2, default=str), report["count"]
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"wrote {args.out}: {count} records ({args.format})")
        else:
            print(text)

    elif args.cmd == "kill":
        from sentinel.killswitch import KillSwitch

        KillSwitch(cfg.db_path).arm(args.scope, reason=args.reason)
        print(f"kill switch ARMED for scope '{args.scope}'")

    elif args.cmd == "unkill":
        from sentinel.killswitch import KillSwitch

        KillSwitch(cfg.db_path).disarm(args.scope)
        print(f"kill switch DISARMED for scope '{args.scope}'")

    elif args.cmd == "approvals":
        from sentinel.approvals import Approvals

        pend = Approvals(cfg.db_path).pending()
        if not pend:
            print("no pending approvals")
        for p in pend:
            print(f"{p['id']}  {p['agent_id']}  {p['tool']}({p['args']})")

    elif args.cmd == "approve":
        from sentinel.approvals import Approvals

        ok = Approvals(cfg.db_path).approve(args.id, by="cli")
        print("approved" if ok else "no such pending approval")

    elif args.cmd == "gc":
        from sentinel.approvals import Approvals
        from sentinel.ratelimit import SqliteRateLimiter

        secs = args.older_than_days * 86400
        removed_approvals = Approvals(cfg.db_path).purge(secs)
        removed_hits = SqliteRateLimiter(cfg.db_path).purge(secs)
        print(f"purged {removed_approvals} approval rows + {removed_hits} rate-limit rows "
              f"(older than {args.older_than_days}d); audit log untouched")

    elif args.cmd == "compliance":
        import time as _time

        from sentinel import frameworks

        if args.all:
            out = frameworks.coverage_summary()
        elif args.framework:
            from sentinel.audit import AuditLog

            log = AuditLog(cfg.db_path)
            out = frameworks.framework_report(
                args.framework, records=log.records(), verify_ok=log.verify().ok,
                generated_at=_time.time(),
                system_name=os.getenv("SENTINEL_SYSTEM_NAME", "unspecified AI system"),
                provider=os.getenv("SENTINEL_PROVIDER", "unspecified"))
        else:
            out = {"frameworks": frameworks.list_frameworks(),
                   "hint": "use --framework <key> for the full mapping, or --all for a coverage summary"}
        text = json.dumps(out, indent=2, default=str)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"wrote {args.out}")
        else:
            print(text)

    elif args.cmd == "demo":
        path = os.path.join(os.getcwd(), "examples", "generic_agent.py")
        if not os.path.exists(path):
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(repo_root, "examples", "generic_agent.py")
        runpy.run_path(path, run_name="__main__")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
