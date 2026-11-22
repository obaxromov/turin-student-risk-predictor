"""Core logic: data, model, database, translations."""
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import data, db, model
from core.i18n import S

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- data
def test_simulated_values_stay_in_range():
    df = data.simulate(500, seed=1, with_outcome=True)
    for col, (lo, hi) in data.RANGES.items():
        assert df[col].between(lo, hi).all(), col
    assert 0.10 < df["failed"].mean() < 0.40  # a plausible failure rate


def test_current_cohort_has_weekly_columns_and_no_outcome():
    cur = data.current_cohort()
    assert len(cur) == 180 and cur["student_id"].is_unique
    assert all(c in cur.columns for c in data.WEEK_COLS)
    assert "failed" not in cur.columns


def test_validate_features():
    ok = pd.DataFrame({f: [50.0] for f in data.FEATURES})
    assert data.validate_features(ok) == []
    assert data.validate_features(ok.drop(columns=["attendance"]))[0]["kind"] == "missing"
    assert data.validate_features(ok.iloc[0:0])[0]["kind"] == "empty"
    bad = ok.copy()
    bad.loc[0, "attendance"] = 140
    assert data.validate_features(bad)[0]["kind"] == "range"
    bad = ok.astype(object)
    bad.loc[0, "test_avg"] = "abc"
    assert data.validate_features(bad)[0]["kind"] == "nan"


# ---------------------------------------------------------------- model
@pytest.fixture(scope="module")
def trained():
    return model.train(data.history())


def test_model_beats_chance_and_finds_failing_students(trained):
    m = trained.metrics
    assert m["roc_auc"] > 0.70
    assert m["recall_flag"] > 0.55
    assert m["accuracy"] >= m["baseline_accuracy"] - 0.02


def test_tiers_are_ordered_by_real_failure_rate(trained):
    r = trained.tier_table.set_index("tier")["fail_rate"]
    assert r["help"] > r["watch"] > r["ok"]


def test_tier_thresholds():
    assert model.tier_of(0.9) == "help"
    assert model.tier_of(model.HELP_T) == "help"
    assert model.tier_of(model.WATCH_T) == "watch"
    assert model.tier_of(0.05) == "ok"


def test_worse_attendance_raises_risk(trained):
    base = pd.DataFrame([trained.medians])
    worse = base.copy()
    worse["attendance"] = 40
    worse["hw_completion"] = 30
    assert model.predict(trained, worse)["risk"].iloc[0] > model.predict(trained, base)["risk"].iloc[0]


def test_contributions_point_at_the_weak_feature(trained):
    row = pd.DataFrame([trained.medians])
    row["attendance"] = 35
    contrib = model.contributions(trained, row).iloc[0]
    assert contrib.idxmax() == "attendance"
    assert model.top_reasons(contrib)[0][0] == "attendance"


def test_typical_student_has_no_reasons(trained):
    row = pd.DataFrame([trained.medians])
    assert model.top_reasons(model.contributions(trained, row).iloc[0]) == []


def test_names_and_demographics_are_never_model_inputs():
    banned = {"name", "gender", "age", "income", "nationality"}
    assert not banned & set(data.FEATURES)


# ---------------------------------------------------------------- database
@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    ids = [f"S{i:03d}" for i in range(1, 11)]
    db.init_db(ids, demo=True)
    return ids


def test_seeded_logins_work_and_wrong_password_fails(fresh_db):
    assert db.authenticate("teacher1", "teacher123")["role"] == "teacher"
    assert db.authenticate("TEACHER1", "teacher123") is not None  # usernames are case-insensitive
    assert db.authenticate("teacher1", "wrong") is None
    assert db.authenticate("nobody", "x") is None
    assert db.authenticate("student1", "student1pass")["student_id"] == "S001"


def test_passwords_are_hashed_and_sql_injection_is_harmless(fresh_db):
    stored = db.list_users()
    assert all("pw_hash" not in u for u in stored)
    with db.conn() as c:
        row = c.execute("SELECT pw_hash FROM users WHERE username='teacher1'").fetchone()
    assert row["pw_hash"].startswith("pbkdf2$") and "teacher123" not in row["pw_hash"]
    assert db.authenticate("' OR '1'='1", "' OR '1'='1") is None


def test_create_user_rules(fresh_db):
    assert db.create_user("newteacher", "longenough1", "teacher", None) is None
    assert db.create_user("newteacher", "longenough1", "teacher", None) == "err_taken"
    assert db.create_user("x y", "longenough1", "teacher", None) == "err_username"
    assert db.create_user("short", "123", "teacher", None) == "err_password"
    assert db.create_user("nolink", "longenough1", "student", None) == "err_student_link"
    assert db.authenticate("newteacher", "longenough1")["role"] == "teacher"


def test_deactivated_user_cannot_sign_in_and_last_admin_is_protected(fresh_db):
    uid = next(u["id"] for u in db.list_users() if u["username"] == "teacher1")
    assert db.set_active(uid, False) is None
    assert db.authenticate("teacher1", "teacher123") is None
    admin = next(u["id"] for u in db.list_users() if u["username"] == "admin1")
    assert db.set_active(admin, False) == "err_last_admin"
    assert db.set_role(admin, "teacher") == "err_last_admin"


def test_reset_password(fresh_db):
    uid = next(u["id"] for u in db.list_users() if u["username"] == "student2")
    assert db.reset_password(uid, "short") == "err_password"
    assert db.reset_password(uid, "brandnewpass") is None
    assert db.authenticate("student2", "student2pass") is None
    assert db.authenticate("student2", "brandnewpass") is not None


def test_contacts_notes_audit_and_identities(fresh_db):
    assert db.toggle_contacted("S003", "teacher1") is True
    assert "S003" in db.contacted()
    assert db.toggle_contacted("S003", "teacher1") is False
    db.add_note("S003", "teacher1", "  spoke after class  ")
    db.add_note("S003", "teacher1", "   ")  # blank notes are ignored
    notes = db.get_notes("S003")
    assert len(notes) == 1 and notes[0]["body"] == "spoke after class"
    db.log("teacher1", "reveal_name", "S003")
    assert db.get_audit()[0]["action"] == "reveal_name"
    assert db.get_name("S003") and db.get_name("nope") is None


# ---------------------------------------------------------------- translations
def test_every_text_has_three_languages():
    assert all(len(v) == 3 and all(x.strip() for x in v) for v in S.values())


def test_every_key_used_in_code_exists():
    used = set()
    for p in list((ROOT / "api").glob("*.py")) + [x for x in (ROOT / "core").glob("*.py") if x.name != "i18n.py"]:
        used |= set(re.findall(r'\bt\(\s*"([a-z_0-9]+)"', p.read_text()))
    web_js = (ROOT / "web" / "app.js").read_text()
    used |= set(re.findall(r'\bt\(\s*"([a-z_0-9]+)"', web_js))
    # Web-only labels can be defined in the small local L dictionary, instead of core.i18n.S.
    local_keys = set(re.findall(r'^\s*([a-z_0-9]+):\s*\[', web_js, re.MULTILINE))
    used = {k for k in used if not k.endswith("_")}  # dynamic prefix keys checked below
    assert not [k for k in used if k not in S and k not in local_keys]
    dynamic = [f"{pre}_{f}" for pre in ("feat", "why") for f in data.FEATURES]
    dynamic += [f"tier_{k}" for k in ("help", "watch", "ok")] + [f"role_{r}" for r in db.ROLES]
    dynamic += [f"conf_{k}" for k in ("high", "medium", "low")]
    dynamic += ["err_username", "err_password", "err_role", "err_student_link", "err_taken", "err_not_found", "err_last_admin"]
    assert not [k for k in dynamic if k not in S]


def test_format_placeholders_match_across_languages():
    for key, variants in S.items():
        names = [set(re.findall(r"{(\w+)}", v)) for v in variants]
        if key.startswith("why_"):  # trend reasons legitimately have no {m}
            continue
        assert names[0] == names[1] == names[2], key
