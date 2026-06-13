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
    ex.add_argument("--format", choices=["json", "otel"], default="json",
                    help="json compliance report (default) or OpenTelemetry GenAI spans")
    kill = sub.add_parser("kill", help="arm the kill switch")
    kill.add_argument("--scope", default="*")
    kill.add_argument("--reason", default="armed via cli")
    unkill = sub.add_parser("unkill", help="disarm the kill switch")
    unkill.add_argument("--scope", default="*")
    sub.add_parser("approvals", help="list pending human-in-the-loop approvals")
    approve = sub.add_parser("approve", help="approve a pending action by id")
    approve.add_argument("id")
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

    elif args.cmd == "demo":
        path = os.path.join(os.getcwd(), "examples", "trading_agent.py")
        if not os.path.exists(path):
            repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            path = os.path.join(repo_root, "examples", "trading_agent.py")
        runpy.run_path(path, run_name="__main__")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
