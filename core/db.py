"""SQLite storage: accounts, name mapping (kept apart from model data), contact log, notes, audit log."""
from __future__ import annotations

import hashlib
import hmac
import os
import random
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

def default_db_path() -> Path:
    """Isolate demo notes/submissions/accounts from imported historical cohorts.

    A previous demo database has student IDs such as S001, which can refer to a
    completely different person after importing a new OULAD sample.  Never
    silently attach those notes/grades to an imported cohort.  A deterministic
    fingerprint gives repeated imports of identical CSVs the same local DB.
    APP_DB remains an explicit override for managed deployments.
    """
    data_dir = Path(__file__).resolve().parents[1] / "data"
    history, current = data_dir / "history.csv", data_dir / "current_students.csv"
    if history.is_file() and current.is_file():
        h = hashlib.sha256()
        for source in (history, current):
            with source.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    h.update(block)
        return data_dir / f"app-cohort-{h.hexdigest()[:12]}.db"
    return data_dir / "app.db"


DB_PATH = Path(os.environ.get("APP_DB") or default_db_path())
ROLES = ("teacher", "student", "admin")
MIN_PASSWORD = 8
ITERATIONS = 200_000


# ---------- passwords ----------
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iters))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


# ---------- connection ----------
@contextmanager
def conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
    pw_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('teacher','student','admin')),
    student_id TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS identities (          -- real names live ONLY here
    student_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
    student_id TEXT PRIMARY KEY,
    contacted_at TEXT NOT NULL,
    by_user TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    due_at TEXT NOT NULL,                        -- UTC, "YYYY-MM-DD HH:MM"
    category TEXT NOT NULL DEFAULT 'homework' CHECK (category IN ('homework','test','exam')),
    mode TEXT NOT NULL DEFAULT 'key' CHECK (mode IN ('key','file')),  -- 'key' = auto-marked, 'file' = upload + teacher grades by hand
    max_score REAL NOT NULL DEFAULT 0,            -- 'file' mode only: the possible total, set by the teacher
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS materials (            -- files the teacher attaches to a 'file'-mode assignment
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS hw_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('number','text','choice')),
    prompt TEXT NOT NULL,
    choices TEXT NOT NULL DEFAULT '',
    answer TEXT NOT NULL,
    tolerance REAL NOT NULL DEFAULT 0,
    points REAL NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    score REAL,                                    -- NULL until a 'file' submission is graded
    max_score REAL NOT NULL,
    answers TEXT NOT NULL DEFAULT '{}',             -- 'key' mode: {question_id: answer}; 'file' mode: '{}'
    file_name TEXT,                                 -- 'file' mode: the student's uploaded file
    stored_path TEXT,
    comment TEXT,                                    -- teacher's written feedback
    graded_by TEXT,
    graded_at TEXT,
    UNIQUE (assignment_id, student_id)
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    username TEXT NOT NULL,
    action TEXT NOT NULL,
    target TEXT NOT NULL DEFAULT ''
);
"""

FIRST = ["Aziz", "Madina", "Jasur", "Dilnoza", "Timur", "Sevara", "Bekzod", "Nodira", "Sardor", "Malika",
         "Otabek", "Zarina", "Rustam", "Gulnora", "Javlon", "Nilufar", "Shaxzod", "Kamola", "Anvar", "Lola"]
LAST = ["Karimov", "Rahimova", "Tursunov", "Saidova", "Nazarov", "Mirzayev", "Abdullayev", "Qodirova",
        "Hasanov", "Yusupova", "Ismoilov", "Aliyeva", "Normatov", "Ergasheva"]


COURSES = ["Mathematics 1", "Mathematics 2", "Physics 1", "Physics 2", "Academic Writing", "Programming 1",
           "Programming 2", "Foreign Language 1", "Foreign Language 2", "New History of Uzbekistan", "Philosophy",
           "Religious Studies", "Data Structures and Algorithms"]


def _columns(c: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in c.execute(f"PRAGMA table_info({table})")}


def _migrate(c: sqlite3.Connection) -> None:
    """Bring a database made by an older version up to date without losing anything."""
    cols = _columns(c, "assignments")
    for col, ddl in (("category", "TEXT NOT NULL DEFAULT 'homework'"), ("mode", "TEXT NOT NULL DEFAULT 'key'"), ("max_score", "REAL NOT NULL DEFAULT 0"),
                     ("course_id", "INTEGER REFERENCES courses(id) ON DELETE SET NULL")):
        if col not in cols:
            c.execute(f"ALTER TABLE assignments ADD COLUMN {col} {ddl}")
    # Older submissions had score NOT NULL and no file/grade columns; SQLite cannot relax NOT NULL in place, so rebuild.
    if "file_name" not in _columns(c, "submissions"):
        c.execute("ALTER TABLE submissions RENAME TO submissions_old")
        c.executescript(SCHEMA)  # recreates the new submissions table
        c.execute("INSERT INTO submissions (id, assignment_id, student_id, submitted_at, score, max_score, answers) "
                  "SELECT id, assignment_id, student_id, submitted_at, score, max_score, answers FROM submissions_old")
        c.execute("DROP TABLE submissions_old")


def init_db(student_ids: list[str], demo: bool = True, seed_names: bool = True) -> None:
    """Create tables; in demo mode seed demo accounts and fictional names once."""
    with conn() as c:
        c.executescript(SCHEMA)
        _migrate(c)
        if c.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            c.executemany("INSERT INTO courses (name, position) VALUES (?,?)", [(n, i) for i, n in enumerate(COURSES)])
        if not demo:
            return
        if seed_names and c.execute("SELECT COUNT(*) FROM identities").fetchone()[0] == 0:
            rnd = random.Random(2026)
            for sid in student_ids:
                name = f"{rnd.choice(FIRST)} {rnd.choice(LAST)}"
                c.execute("INSERT INTO identities VALUES (?, ?)", (sid, name))
        if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            seeds = [("admin1", os.environ.get("APP_ADMIN_PASSWORD", "admin123"), "admin", None), ("teacher1", os.environ.get("APP_TEACHER_PASSWORD", "teacher123"), "teacher", None)]
            seeds += [(f"student{i}", os.environ.get("APP_STUDENT_PASSWORD", f"student{i}pass"), "student", student_ids[i - 1]) for i in range(1, min(5, len(student_ids)) + 1)]
            for u, pw, role, sid in seeds:
                c.execute(
                    "INSERT INTO users (username, pw_hash, role, student_id, created_at) VALUES (?,?,?,?,?)",
                    (u, hash_password(pw), role, sid, _now()),
                )


# ---------- accounts ----------
def authenticate(username: str, password: str) -> dict | None:
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    # verify even when the user is missing, so timing does not reveal which usernames exist
    stored = row["pw_hash"] if row else hash_password("x")
    ok = verify_password(password, stored)
    if row and ok and row["active"]:
        return {"username": row["username"], "role": row["role"], "student_id": row["student_id"]}
    return None


def list_users() -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT id, username, role, student_id, active, created_at FROM users ORDER BY id")]


def create_user(username: str, password: str, role: str, student_id: str | None) -> str | None:
    """Return None on success, or an error key for the UI."""
    username = username.strip()
    if not username or len(username) > 40 or not username.replace("_", "").replace(".", "").isalnum():
        return "err_username"
    if len(password) < MIN_PASSWORD:
        return "err_password"
    if role not in ROLES:
        return "err_role"
    if role == "student" and not student_id:
        return "err_student_link"
    try:
        with conn() as c:
            c.execute(
                "INSERT INTO users (username, pw_hash, role, student_id, created_at) VALUES (?,?,?,?,?)",
                (username, hash_password(password), role, student_id if role == "student" else None, _now()),
            )
    except sqlite3.IntegrityError:
        return "err_taken"
    return None


def _admin_count(c) -> int:
    return c.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND active=1").fetchone()[0]


def set_role(user_id: int, role: str, student_id: str | None = None) -> str | None:
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return "err_not_found"
        if row["role"] == "admin" and role != "admin" and row["active"] and _admin_count(c) <= 1:
            return "err_last_admin"
        if role == "student" and not (student_id or row["student_id"]):
            return "err_student_link"
        c.execute("UPDATE users SET role=?, student_id=? WHERE id=?",
                  (role, (student_id or row["student_id"]) if role == "student" else None, user_id))
    return None


def set_active(user_id: int, active: bool) -> str | None:
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            return "err_not_found"
        if not active and row["role"] == "admin" and row["active"] and _admin_count(c) <= 1:
            return "err_last_admin"
        c.execute("UPDATE users SET active=? WHERE id=?", (1 if active else 0, user_id))
    return None


def reset_password(user_id: int, password: str) -> str | None:
    if len(password) < MIN_PASSWORD:
        return "err_password"
    with conn() as c:
        c.execute("UPDATE users SET pw_hash=? WHERE id=?", (hash_password(password), user_id))
    return None


# ---------- identities (teacher-only "reveal name") ----------
def get_name(student_id: str) -> str | None:
    with conn() as c:
        row = c.execute("SELECT full_name FROM identities WHERE student_id=?", (student_id,)).fetchone()
    return row["full_name"] if row else None


# ---------- contacts and notes ----------
def contacted() -> dict[str, dict]:
    with conn() as c:
        return {r["student_id"]: dict(r) for r in c.execute("SELECT * FROM contacts")}


def toggle_contacted(student_id: str, username: str) -> bool:
    """Flip the 'contacted' mark. Returns the new state."""
    with conn() as c:
        row = c.execute("SELECT 1 FROM contacts WHERE student_id=?", (student_id,)).fetchone()
        if row:
            c.execute("DELETE FROM contacts WHERE student_id=?", (student_id,))
            return False
        c.execute("INSERT INTO contacts VALUES (?,?,?)", (student_id, _now(), username))
        return True


def add_note(student_id: str, author: str, body: str) -> None:
    body = body.strip()[:1000]
    if body:
        with conn() as c:
            c.execute("INSERT INTO notes (student_id, author, body, created_at) VALUES (?,?,?,?)",
                      (student_id, author, body, _now()))


def get_notes(student_id: str) -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT author, body, created_at FROM notes WHERE student_id=? ORDER BY id DESC", (student_id,))]


# ---------- audit ----------
def log(username: str, action: str, target: str = "") -> None:
    with conn() as c:
        c.execute("INSERT INTO audit (ts, username, action, target) VALUES (?,?,?,?)",
                  (_now(), username, action, target))


def get_audit(limit: int = 200) -> list[dict]:
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT ts, username, action, target FROM audit ORDER BY id DESC LIMIT ?", (limit,))]
