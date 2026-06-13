"""Configuration via environment (.env is loaded if present; no extra dependency)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


@dataclass
class Config:
    db_path: str = "./data/sentinel.db"
    policy_path: str = "./policies/example.yaml"
    api_host: str = "127.0.0.1"
    api_port: int = 8787
    redact_keys: Optional[list[str]] = None

    @classmethod
    def from_env(cls, load_env: bool = True) -> "Config":
        if load_env:
            load_dotenv()
        keys = os.getenv("SENTINEL_REDACT_KEYS")
        return cls(
            db_path=os.getenv("SENTINEL_DB_PATH", "./data/sentinel.db"),
            policy_path=os.getenv("SENTINEL_POLICY_PATH", "./policies/example.yaml"),
            api_host=os.getenv("SENTINEL_API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("SENTINEL_API_PORT", "8787")),
            redact_keys=[k.strip() for k in keys.split(",") if k.strip()] if keys else None,
        )
