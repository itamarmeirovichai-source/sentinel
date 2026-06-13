"""Minimal control plane: a FastAPI app exposing the audit trail, integrity check,
policy, and the kill switch — plus a single-page dashboard.

The API and any running agent share state through the SQLite DB, so hitting KILL in
the dashboard genuinely stops a separate agent process on its next guarded call.
"""
from __future__ import annotations

import os
from collections import Counter
from typing import Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from sentinel.audit import AuditLog
from sentinel.config import Config
from sentinel.killswitch import KillSwitch
from sentinel.policy import Policy

_DASHBOARD_FILE = os.path.join(os.path.dirname(__file__), "dashboard", "index.html")


def create_app(config: Optional[Config] = None) -> FastAPI:
    cfg = config or Config.from_env()
    app = FastAPI(title="Sentinel Control Plane", version="0.1.0")
    audit = AuditLog(cfg.db_path, redact_keys=cfg.redact_keys)
    killswitch = KillSwitch(cfg.db_path)

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> HTMLResponse:
        with open(_DASHBOARD_FILE, "r", encoding="utf-8") as fh:
            return HTMLResponse(fh.read())

    @app.get("/api/status")
    def status() -> dict:
        v = audit.verify()
        recs = audit.records()
        return {
            "integrity": {"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message},
            "killswitch": killswitch.status(),
            "total_actions": len(recs),
            "by_status": dict(Counter(r.status for r in recs)),
            "by_decision": dict(Counter(r.decision for r in recs)),
        }

    @app.get("/api/actions")
    def actions(limit: int = 100) -> list:
        recs = audit.records()[-limit:]
        return [r.__dict__ for r in reversed(recs)]

    @app.get("/api/verify")
    def verify() -> dict:
        v = audit.verify()
        return {"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message}

    @app.get("/api/export")
    def export() -> dict:
        return audit.export()

    @app.get("/api/policy")
    def get_policy() -> dict:
        try:
            with open(cfg.policy_path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            text = ""
        return {"path": cfg.policy_path, "yaml": text}

    @app.put("/api/policy")
    def put_policy(payload: dict = Body(...)) -> dict:
        text = payload.get("yaml", "")
        try:
            Policy.from_yaml(text)  # validate before persisting
        except Exception as exc:  # noqa: BLE001 - surface parse error to the caller
            raise HTTPException(status_code=400, detail=f"invalid policy: {exc}")
        with open(cfg.policy_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return {"ok": True}

    @app.post("/api/kill")
    def kill(payload: dict = Body(default={})) -> dict:
        scope = payload.get("scope", "*")
        reason = payload.get("reason", "killed via dashboard")
        killswitch.arm(scope, reason=reason)
        return {"ok": True, "killswitch": killswitch.status()}

    @app.post("/api/unkill")
    def unkill(payload: dict = Body(default={})) -> dict:
        scope = payload.get("scope", "*")
        killswitch.disarm(scope)
        return {"ok": True, "killswitch": killswitch.status()}

    return app
