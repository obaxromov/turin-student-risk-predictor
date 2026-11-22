"""Server-side sessions and a sign-in lock. In memory: fine for one demo process, reset on restart.

The browser keeps an opaque random token and sends it as `Authorization: Bearer <token>`.
No cookie is used, so there is no CSRF risk and sign-in also works inside the Hugging Face iframe.
"""
from __future__ import annotations

import secrets
import threading
import time

SESSION_SECONDS = 8 * 3600
MAX_ATTEMPTS = 5
LOCK_SECONDS = 30

_lock = threading.Lock()
_sessions: dict[str, dict] = {}
_fails: dict[str, dict] = {}


def create(user: dict) -> str:
    token = secrets.token_urlsafe(32)
    with _lock:
        now = time.time()
        for k in [k for k, v in _sessions.items() if v["exp"] < now]:
            _sessions.pop(k, None)
        _sessions[token] = {"user": user, "exp": now + SESSION_SECONDS}
    return token


def get(token: str | None) -> dict | None:
    if not token:
        return None
    with _lock:
        s = _sessions.get(token)
        if not s:
            return None
        if s["exp"] < time.time():
            _sessions.pop(token, None)
            return None
        return s["user"]


def destroy(token: str | None) -> None:
    with _lock:
        _sessions.pop(token or "", None)


def lock_remaining(key: str) -> int:
    with _lock:
        f = _fails.get(key)
        return max(0, int(f["until"] - time.time())) if f else 0


def record_failure(key: str) -> None:
    with _lock:
        f = _fails.setdefault(key, {"n": 0, "until": 0.0})
        f["n"] += 1
        if f["n"] >= MAX_ATTEMPTS:
            f["n"] = 0
            f["until"] = time.time() + LOCK_SECONDS


def clear_failures(key: str) -> None:
    with _lock:
        _fails.pop(key, None)
