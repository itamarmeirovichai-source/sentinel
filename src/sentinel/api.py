"""Minimal control plane: a FastAPI app exposing the audit trail, integrity check,
policy, approvals, and the kill switch — plus a single-page dashboard.

The API and any running agent share state through the SQLite DB, so hitting KILL in
the dashboard genuinely stops a separate agent process on its next guarded call.

Auth: if `config.api_token` is set, every *mutating* endpoint (kill/unkill/policy/
approve) requires `Authorization: Bearer <token>`. Read endpoints stay open (intended
for a localhost bind). `sentinel serve` auto-generates a token if none is configured.
"""
from __future__ import annotations

import os
import secrets
from collections import Counter
from typing import Optional

from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

from sentinel.approvals import Approvals
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
    approvals = Approvals(cfg.db_path)

    def require_token(authorization: str = Header(default="")) -> None:
        if not cfg.api_token:
            return  # auth disabled
        if not secrets.compare_digest(authorization, f"Bearer {cfg.api_token}"):
            raise HTTPException(status_code=401, detail="missing or invalid control token")

    auth = [Depends(require_token)]
    read_auth = auth if cfg.protect_reads else []

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> HTMLResponse:
        with open(_DASHBOARD_FILE, "r", encoding="utf-8") as fh:
            return HTMLResponse(fh.read())

    @app.get("/api/status", dependencies=read_auth)
    def status() -> dict:
        v = audit.verify()
        recs = audit.records()
        return {
            "integrity": {"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message},
            "killswitch": killswitch.status(),
            "total_actions": len(recs),
            "by_status": dict(Counter(r.status for r in recs)),
            "by_decision": dict(Counter(r.decision for r in recs)),
            "pending_approvals": len(approvals.pending()),
            "auth_required": bool(cfg.api_token),
        }

    @app.get("/api/actions", dependencies=read_auth)
    def actions(limit: int = 100) -> list:
        recs = audit.records()[-limit:]
        return [r.__dict__ for r in reversed(recs)]

    @app.get("/api/verify", dependencies=read_auth)
    def verify() -> dict:
        v = audit.verify()
        return {"ok": v.ok, "first_bad_seq": v.first_bad_seq, "message": v.message}

    @app.get("/api/export", dependencies=read_auth)
    def export() -> dict:
        return audit.export()

    @app.get("/api/approvals", dependencies=read_auth)
    def list_approvals() -> list:
        return approvals.pending()

    @app.get("/api/policy", dependencies=read_auth)
    def get_policy() -> dict:
        try:
            with open(cfg.policy_path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            text = ""
        return {"path": cfg.policy_path, "yaml": text}

    @app.put("/api/policy", dependencies=auth)
    def put_policy(payload: dict = Body(...)) -> dict:
        text = payload.get("yaml", "")
        try:
            Policy.from_yaml(text)  # validate before persisting
        except Exception as exc:  # noqa: BLE001 - surface parse error to the caller
            raise HTTPException(status_code=400, detail=f"invalid policy: {exc}")
        with open(cfg.policy_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return {"ok": True}

    @app.post("/api/kill", dependencies=auth)
    def kill(payload: dict = Body(default={})) -> dict:
        scope = payload.get("scope", "*")
        reason = payload.get("reason", "killed via dashboard")
        killswitch.arm(scope, reason=reason)
        return {"ok": True, "killswitch": killswitch.status()}

    @app.post("/api/unkill", dependencies=auth)
    def unkill(payload: dict = Body(default={})) -> dict:
        scope = payload.get("scope", "*")
        killswitch.disarm(scope)
        return {"ok": True, "killswitch": killswitch.status()}

    @app.post("/api/approve", dependencies=auth)
    def approve(payload: dict = Body(...)) -> dict:
        approval_id = payload.get("id")
        if not approval_id:
            raise HTTPException(status_code=400, detail="missing approval id")
        ok = approvals.approve(approval_id, by=payload.get("by", "dashboard"))
        if not ok:
            raise HTTPException(status_code=404, detail="no such pending approval")
        return {"ok": True}

    return app
