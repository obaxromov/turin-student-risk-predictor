"""Web API + static front end.   Run:  uvicorn api.main:app --port 7860

The web front end and API share the Python `core/` model, database, and homework package.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from api import sessions
from core import data, db, service
from core.data import HELP_T, WATCH_T, WEEK_COLS, WEEKS
from core.i18n import S

DEMO_MODE = os.environ.get("APP_DEMO", "1") != "0"
# Disable public role-shortcut logins without preventing the database from seeding.
DEMO_LOGIN_ENABLED = DEMO_MODE and os.environ.get("APP_DEMO_LOGIN", "1") != "0"
# Optional private passwords for FIRST-TIME seeding in a NEW database only.
DEMO_ACCOUNTS = {
    "teacher": ("teacher1", os.environ.get("APP_TEACHER_PASSWORD", "teacher123")),
    "student": ("student1", os.environ.get("APP_STUDENT_PASSWORD", "student1pass")),
    "admin": ("admin1", os.environ.get("APP_ADMIN_PASSWORD", "admin123")),
}
WEB_DIR = Path(__file__).resolve().parents[1] / "web"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Historical OULAD records have no names. Never seed fictional identities.
    db.init_db(data.student_ids(), demo=DEMO_MODE,
               seed_names=not (data.DATA_DIR / "current_students.csv").exists())
    service.warm_up()  # model trains/loads in the background; login never waits for it
    yield


app = FastAPI(title="Student Risk Predictor", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

# A streaming ASGI guard: Content-Length alone cannot be trusted. Avoid
# materialising an unbounded base64 JSON upload before validation occurs.
MAX_REQUEST_BYTES = 30_000_000


class RequestBodySizeLimit:
    """Reject API upload/request bodies over 30MB with HTTP 413."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope.get("path", "").startswith("/api/"):
            await self.app(scope, receive, send)
            return
        from fastapi.responses import JSONResponse
        from starlette.types import Message

        headers = dict(scope.get("headers", []))
        try:
            size = int(headers.get(b"content-length", b"0"))
        except (TypeError, ValueError):
            size = MAX_REQUEST_BYTES + 1  # invalid lengths are not trusted
        if size > MAX_REQUEST_BYTES:
            await JSONResponse({"detail": "request_too_large"}, status_code=413)(scope, receive, send)
            return
        total = 0

        class RequestTooLarge(Exception):
            pass

        async def limited_receive() -> Message:
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > MAX_REQUEST_BYTES:
                    raise RequestTooLarge()
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestTooLarge:
            await JSONResponse({"detail": "request_too_large"}, status_code=413)(scope, receive, send)


app.add_middleware(RequestBodySizeLimit)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer"
    # No inline scripts or styles; framing is allowed because Hugging Face shows Spaces inside an iframe.
    resp.headers["Content-Security-Policy"] = ("default-src 'self'; img-src 'self' data:; object-src 'none'; "
                                               "base-uri 'none'; form-action 'self'")
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


# ---------- auth helpers ----------
def _token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def current_user(authorization: str | None = Header(default=None)) -> dict:
    user = sessions.get(_token(authorization))
    if not user:
        raise HTTPException(401, "not_signed_in")
    return user


def require_role(*roles: str):
    def dep(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, "forbidden")
        return user
    return dep


# ---------- public ----------
class LoginIn(BaseModel):
    username: str = Field(max_length=60)
    password: str = Field(max_length=200)


class DemoIn(BaseModel):
    role: str = Field(max_length=20)


@app.get("/api/config")
def config() -> dict:
    return {"demo_mode": DEMO_MODE, "demo_login_enabled": DEMO_LOGIN_ENABLED, "langs": {"en": "EN", "ru": "RU", "uz": "UZ"}}


@app.get("/api/i18n")
def i18n() -> dict:
    """Every text in EN / RU / UZ; the browser picks the language."""
    return {k: list(v) for k, v in S.items()}


@app.post("/api/login")
def login(body: LoginIn) -> JSONResponse:
    key = body.username.strip().lower()[:60]
    wait = sessions.lock_remaining(key)
    if wait > 0:
        return JSONResponse({"error": "locked", "seconds": wait}, status_code=429)
    user = db.authenticate(body.username, body.password)
    if not user:
        sessions.record_failure(key)
        db.log(key or "-", "login_failed")
        return JSONResponse({"error": "bad_credentials"}, status_code=401)
    sessions.clear_failures(key)
    db.log(user["username"], "login_ok")
    return JSONResponse({"token": sessions.create(user), "user": user})


@app.post("/api/demo-login")
def demo_login(body: DemoIn) -> JSONResponse:
    if not DEMO_LOGIN_ENABLED or body.role not in DEMO_ACCOUNTS:
        raise HTTPException(404, "not_found")
    user = db.authenticate(*DEMO_ACCOUNTS[body.role])
    if not user:
        raise HTTPException(404, "not_found")
    db.log(user["username"], "login_ok")
    return JSONResponse({"token": sessions.create(user), "user": user})


@app.post("/api/logout")
def logout(authorization: str | None = Header(default=None)) -> dict:
    token = _token(authorization)
    user = sessions.get(token)
    if user:
        db.log(user["username"], "logout")
    sessions.destroy(token)
    return {"ok": True}


@app.get("/api/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {"user": user, "demo": service.bundle().demo if DEMO_MODE else False}


# ---------- teacher ----------
@app.get("/api/overview")
def overview(user: dict = Depends(require_role("teacher"))) -> dict:
    b = service.live()
    df = b.df
    done = set(db.contacted())

    counts = df["tier"].value_counts()
    cnt = {k: int(counts.get(k, 0)) for k in ("help", "watch", "ok")}
    half = len(WEEK_COLS) // 2
    early, late = float(df[WEEK_COLS[:half]].mean().mean()), float(df[WEEK_COLS[half:]].mean().mean())
    trend = (late / early - 1) * 100 if early else 0.0

    top = df[~df["student_id"].isin(done)].sort_values("risk", ascending=False).head(8)
    urgent = []
    for _, r in top.iterrows():
        reason = None
        if r["reasons"]:
            f, _ = r["reasons"][0]
            reason = {"feature": f, "value": float(r[f]), "median": float(b.class_median[f])}
        urgent.append({"student_id": r["student_id"], "tier": r["tier"], "risk": round(float(r["risk"]) * 100),
                       "reason": reason, "weeks": [round(float(r[w]), 1) for w in WEEK_COLS]})

    by_tier = df.groupby("tier")[WEEK_COLS].mean()
    series = {k: [round(float(x), 1) for x in by_tier.loc[k]] for k in ("help", "watch", "ok") if k in by_tier.index}
    flagged = (df.assign(flag=df["tier"].isin(["help", "watch"])).groupby("group")["flag"].mean().mul(100).round(0))
    return {
        "demo": b.demo, "weeks": WEEKS, "students": len(df), "counts": cnt, "trend": round(trend, 1),
        "urgent": urgent, "tier_series": series, "groups": [{"group": g, "flagged": int(v)} for g, v in flagged.items()],
        "thresholds": {"help": round(HELP_T * 100), "watch": round(WATCH_T * 100)},
        "auc": round(float(b.tr.metrics["roc_auc"]), 2),
    }


from api.features import setup as setup_feature_routes
setup_feature_routes(app, require_role)

# ---------- front end ----------
@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=WEB_DIR), name="web")
