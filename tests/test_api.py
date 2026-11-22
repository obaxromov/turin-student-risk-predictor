"""Web API: sign-in, roles, lock-out, overview. Uses the same throw-away database as the other tests."""
import pytest
from fastapi.testclient import TestClient

from api import sessions
from api.main import app


@pytest.fixture()
def client():
    sessions._fails.clear()
    with TestClient(app) as c:  # runs the startup hook (database seed, model warm-up)
        yield c


def _login(c, user, pw):
    return c.post("/api/login", json={"username": user, "password": pw})


def _auth(c, user, pw):
    r = _login(c, user, pw)
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["token"]}


def test_public_endpoints(client):
    assert client.get("/api/config").json()["demo_mode"] is True
    tr = client.get("/api/i18n").json()
    assert tr["tier_help"] == ["Needs help", "Нужна помощь", "Yordam kerak"]
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200


def test_login_good_and_bad(client):
    assert _login(client, "teacher1", "wrong").status_code == 401
    assert _login(client, "nobody", "x").status_code == 401
    r = _login(client, "teacher1", "teacher123")
    assert r.status_code == 200 and r.json()["user"]["role"] == "teacher"
    assert "pw_hash" not in r.text


def test_lockout_after_five_failures(client):
    for _ in range(5):
        assert _login(client, "student2", "bad").status_code == 401
    r = _login(client, "student2", "student2pass")  # even the right password waits
    assert r.status_code == 429 and r.json()["seconds"] > 0


def test_overview_needs_teacher_session(client):
    assert client.get("/api/overview").status_code == 401
    assert client.get("/api/overview", headers={"Authorization": "Bearer nonsense"}).status_code == 401
    assert client.get("/api/overview", headers=_auth(client, "student3", "student3pass")).status_code == 403
    assert client.get("/api/overview", headers=_auth(client, "admin1", "admin123")).status_code == 403


def test_overview_content(client):
    d = client.get("/api/overview", headers=_auth(client, "teacher1", "teacher123")).json()
    assert d["students"] == sum(d["counts"].values()) == 180
    assert len(d["urgent"]) == 8 and all(len(u["weeks"]) == 8 for u in d["urgent"])
    risks = [u["risk"] for u in d["urgent"]]
    assert risks == sorted(risks, reverse=True)
    assert d["thresholds"] == {"help": 50, "watch": 25}
    assert "name" not in str(d).lower()  # real names stay hidden behind the Reveal button


def test_logout_kills_token(client):
    h = _auth(client, "teacher1", "teacher123")
    assert client.get("/api/me", headers=h).status_code == 200
    client.post("/api/logout", headers=h)
    assert client.get("/api/me", headers=h).status_code == 401


def test_demo_login_and_headers(client):
    r = client.post("/api/demo-login", json={"role": "teacher"})
    assert r.status_code == 200 and r.json()["user"]["username"] == "teacher1"
    assert client.post("/api/demo-login", json={"role": "hacker"}).status_code == 404
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["cache-control"] == "no-store"


def test_oversized_input_rejected(client):
    assert _login(client, "a" * 500, "x").status_code == 422
