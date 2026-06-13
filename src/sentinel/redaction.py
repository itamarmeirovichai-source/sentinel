"""Redaction of secret-looking values before they ever reach the audit log.

Threat T3/T7 (ARCHITECTURE.md §6): the audit log must never become a place where
secrets accumulate. Redaction is applied at write time, by key name and by value
shape, recursively through nested dicts/lists.
"""
from __future__ import annotations

import re
from typing import Any

DEFAULT_REDACT_KEYS = [
    "api_key", "apikey", "token", "password", "passwd", "secret",
    "authorization", "access_token", "private_key",
]

REDACTED = "***REDACTED***"

# Conservative value-shape heuristics (avoid redacting ordinary prose).
_VALUE_PATTERNS = [
    re.compile(r"(?i)bearer\s+[a-z0-9._\-]+"),                 # bearer tokens
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),                    # sk-... style keys
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                       # AWS access key ids
    # long opaque tokens that contain BOTH a letter and a digit
    re.compile(r"\b(?=[A-Za-z0-9_\-]*[A-Za-z])(?=[A-Za-z0-9_\-]*[0-9])[A-Za-z0-9_\-]{40,}\b"),
]


def redact(args: dict[str, Any], redact_keys: list[str] | None = None) -> dict[str, Any]:
    keys = {k.lower() for k in (redact_keys if redact_keys is not None else DEFAULT_REDACT_KEYS)}
    return {k: _redact_value(k, v, keys) for k, v in args.items()}


def _redact_value(key: str, value: Any, keys: set[str]) -> Any:
    if key.lower() in keys:
        return REDACTED
    if isinstance(value, str):
        out = value
        for pat in _VALUE_PATTERNS:
            out = pat.sub(REDACTED, out)
        return out
    if isinstance(value, dict):
        return {k: _redact_value(k, v, keys) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_value(key, v, keys) for v in value]
    return value
