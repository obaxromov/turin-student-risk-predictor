"""Web-only packaging and minimal-login regression checks."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_only_one_frontend_and_stylesheet():
    assert not (ROOT / "app.py").exists()
    assert not (ROOT / "views").exists()
    assert not (ROOT / ".streamlit").exists()
    assert not (ROOT / "core" / "ui.py").exists()
    assert not (ROOT / "web" / "studio.css").exists()
    assert "streamlit" not in (ROOT / "requirements-web.txt").read_text().lower().replace("no streamlit needed", "")
    html = (ROOT / "web" / "index.html").read_text()
    assert html.count('rel="stylesheet"') == 1
    assert 'href="/style.css"' in html


def test_login_has_one_window_not_two_columns():
    js = (ROOT / "web" / "app.js").read_text()
    assert 'class: "auth-card"' in js
    assert 'class: "auth-page"' in js
    assert 'class: "login-intro"' not in js
    assert 'class: "login-preview"' not in js


def test_system_font_and_normal_tracking():
    css = (ROOT / "web" / "style.css").read_text()
    assert '"Segoe UI"' in css
    assert 'BlinkMacSystemFont' in css
    assert 'letter-spacing:normal' in css
    assert 'letter-spacing:-' not in css  # tight letter spacing made the type look compressed
    assert '.auth-card' in css
    assert '.auth-page' in css
