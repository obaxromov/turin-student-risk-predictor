"""Homework: assignments with a deadline, and two ways to mark them.

  'key' mode  — auto-marked questions (number / text / choice). The app only COMPARES answers
                with the teacher's key. It never runs anything a student sends.
  'file' mode — for a test, essay or anything written on paper or in another program: the teacher
                may attach material (a PDF, the question sheet) and the student uploads one file
                in reply (or, for something handed in on paper, the teacher can grade with no file
                at all). The teacher enters the mark and an optional comment by hand; nothing is
                auto-graded here, because there is nothing safe to compare a free-form file against.

Both modes feed the risk model the same way once an assignment is closed (see live_stats/blend) —
an ungraded 'file' submission does not count as handed in with a mark until it is graded.
"""
from __future__ import annotations

import json
import math
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core import data, db

UTC_OFFSET = timedelta(hours=float(os.environ.get("APP_UTC_OFFSET", "5")))  # Tashkent = UTC+5, no daylight saving
FMT = "%Y-%m-%d %H:%M"
KINDS = ("number", "text", "choice")
CATEGORIES = ("homework", "test", "exam")
MAX_QUESTIONS = 30
PRIOR = 3  # earlier (CSV) homework data counts as this many assignments when mixing in live marks

FILES_DIR = Path(os.environ.get("APP_FILES_DIR", data.DATA_DIR / "files"))
MAX_FILE_BYTES = 20_000_000
ALLOWED_EXT = {".pdf", ".doc", ".docx", ".odt", ".txt", ".md", ".png", ".jpg", ".jpeg", ".zip"}


def save_file(raw: bytes, filename: str) -> tuple[str, str] | str:
    """Write an uploaded file to disk under a random name. Returns (stored_path, safe_filename) or an error key."""
    if len(raw) > MAX_FILE_BYTES:
        return "hw_err_file_big"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        return "hw_err_file_type"
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{ext}"
    (FILES_DIR / stored).write_bytes(raw)
    safe_name = re.sub(r"[^\w.\- ]", "_", Path(filename).name)[:120] or f"file{ext}"
    return str(FILES_DIR / stored), safe_name


def read_file(stored_path: str) -> bytes | None:
    try:
        p = Path(stored_path)
        return p.read_bytes() if p.is_file() and p.resolve().is_relative_to(FILES_DIR.resolve()) else None
    except OSError:
        return None


# ---------- time ----------
def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def local_to_utc(local: datetime) -> str:
    return (local - UTC_OFFSET).strftime(FMT)


def to_local(due_utc: str) -> datetime:
    return datetime.strptime(due_utc, FMT) + UTC_OFFSET


def is_closed(due_utc: str, now: datetime | None = None) -> bool:
    return datetime.strptime(due_utc, FMT) <= (now or now_utc())


# ---------- questions and marking ----------
def parse_options(text: str) -> list[str]:
    return [o.strip() for o in (text or "").split("|") if o.strip()]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _to_float(s: str) -> float | None:
    try:
        v = float(str(s).strip().replace(",", "."))
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def check(q: dict, given: str) -> bool:
    given = "" if given is None else str(given)
    if q["kind"] == "number":
        g, a = _to_float(given), _to_float(q["answer"])
        return g is not None and a is not None and abs(g - a) <= float(q.get("tolerance") or 0) + 1e-9
    if q["kind"] == "choice":
        return _norm(given) == _norm(q["answer"])
    return _norm(given) in {_norm(a) for a in parse_options(q["answer"]) or [q["answer"]]}


def grade(questions: list[dict], answers: dict[int, str]) -> tuple[float, float, dict[int, bool]]:
    ok = {q["id"]: check(q, answers.get(q["id"], "")) for q in questions}
    score = sum(q["points"] for q in questions if ok[q["id"]])
    return score, sum(q["points"] for q in questions), ok


def clean_questions(rows: list[dict]) -> tuple[list[dict], tuple[str, int | None] | None]:
    """Validate the teacher's question table. Returns (questions, None) or ([], (why_key, row_number))."""
    out = []
    rows = [r for r in rows if any(str(r.get(k) or "").strip() for k in ("prompt", "answer"))]
    if not rows:
        return [], ("hw_err_noq", None)
    if len(rows) > MAX_QUESTIONS:
        return [], ("hw_err_many", None)
    for n, r in enumerate(rows, start=1):
        kind = str(r.get("kind") or "").strip().lower()
        prompt = str(r.get("prompt") or "").strip()
        answer = str(r.get("answer") or "").strip()
        choices = str(r.get("choices") or "").strip()
        try:
            points = float(r.get("points") if r.get("points") not in (None, "") else 1)
            tol = float(r.get("tolerance") if r.get("tolerance") not in (None, "") else 0)
        except (TypeError, ValueError):
            return [], ("hw_why_points", n)
        if kind not in KINDS:
            return [], ("hw_why_kind", n)
        if not prompt or len(prompt) > 300:
            return [], ("hw_why_prompt", n)
        if not answer or len(answer) > 200:
            return [], ("hw_why_answer", n)
        if not (0 < points <= 100) or not (0 <= tol <= 1e6) or not math.isfinite(points + tol):
            return [], ("hw_why_points", n)
        if kind == "number" and _to_float(answer) is None:
            return [], ("hw_why_number", n)
        if kind == "choice":
            opts = parse_options(choices)
            if len(opts) < 2 or len(opts) > 8 or _norm(answer) not in {_norm(o) for o in opts}:
                return [], ("hw_why_choices", n)
            choices = "|".join(opts)
            answer = next(o for o in opts if _norm(o) == _norm(answer))
        else:
            choices = ""
        out.append({"kind": kind, "prompt": prompt, "choices": choices, "answer": answer,
                    "tolerance": tol if kind == "number" else 0.0, "points": points})
    return out, None


# ---------- storage ----------
def _store_materials(materials: list[tuple[bytes, str]]) -> list[tuple[str, str, int]] | str:
    saved = []
    for raw, name in materials:
        out = save_file(raw, name)
        if isinstance(out, str):
            return out
        saved.append((out[0], out[1], len(raw)))
    return saved


def create(title: str, description: str, due_utc: str, user: str, questions: list[dict], course_id: int | None = None,
           category: str = "homework", materials: list[tuple[bytes, str]] | None = None) -> int | str:
    """A 'key' (auto-marked) assignment. `materials` = optional (bytes, filename) attachments, e.g. the book to study."""
    if category not in CATEGORIES:
        category = "homework"
    saved = _store_materials(materials or [])
    if isinstance(saved, str):
        return saved
    with db.conn() as c:
        cur = c.execute("INSERT INTO assignments (title, description, due_at, mode, category, course_id, created_by, created_at)"
                        " VALUES (?,?,?,'key',?,?,?,?)",
                        (title.strip()[:100], description.strip()[:2000], due_utc, category, course_id, user, db._now()))
        aid = cur.lastrowid
        for i, q in enumerate(questions):
            c.execute("INSERT INTO hw_questions (assignment_id, position, kind, prompt, choices, answer, tolerance, points)"
                      " VALUES (?,?,?,?,?,?,?,?)",
                      (aid, i, q["kind"], q["prompt"], q["choices"], q["answer"], q["tolerance"], q["points"]))
        for stored_path, filename, size in saved:
            c.execute("INSERT INTO materials (assignment_id, filename, stored_path, size_bytes) VALUES (?,?,?,?)",
                      (aid, filename, stored_path, size))
    return aid


def create_file_assignment(title: str, description: str, due_utc: str, user: str, max_score: float,
                           materials: list[tuple[bytes, str]], course_id: int | None = None,
                           category: str = "homework") -> int | str:
    """A 'file' (teacher-graded) assignment: a test, essay or anything handed in as a document.
    `materials` is a list of (file_bytes, filename) the teacher attaches, e.g. the question sheet."""
    if not (0 < max_score <= 1000):
        return "hw_why_points"
    if category not in CATEGORIES:
        category = "homework"
    saved = _store_materials(materials)
    if isinstance(saved, str):
        return saved
    with db.conn() as c:
        cur = c.execute("INSERT INTO assignments (title, description, due_at, mode, category, max_score, course_id, created_by, created_at)"
                        " VALUES (?,?,?,'file',?,?,?,?,?)",
                        (title.strip()[:100], description.strip()[:2000], due_utc, category, max_score, course_id, user, db._now()))
        aid = cur.lastrowid
        for stored_path, filename, size in saved:
            c.execute("INSERT INTO materials (assignment_id, filename, stored_path, size_bytes) VALUES (?,?,?,?)",
                      (aid, filename, stored_path, size))
    return aid


def materials_for(aid: int) -> list[dict]:
    with db.conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM materials WHERE assignment_id=? ORDER BY id", (aid,))]


def list_assignments(course_id: int | None = None) -> list[dict]:
    with db.conn() as c:
        if course_id is None:
            rows = c.execute("SELECT * FROM assignments ORDER BY due_at DESC, id DESC")
        else:
            rows = c.execute("SELECT * FROM assignments WHERE course_id=? ORDER BY due_at DESC, id DESC", (course_id,))
        return [dict(r) for r in rows]


def courses() -> list[dict]:
    with db.conn() as c:
        return [dict(r) for r in c.execute("SELECT id, name FROM courses ORDER BY position, id")]


def course_names() -> dict[int, str]:
    return {c["id"]: c["name"] for c in courses()}


def questions_from_csv(raw: bytes) -> tuple[list[dict], tuple[str, int | None] | None]:
    """Read a CSV with columns kind,prompt,choices,answer,points,tolerance and validate it like the table editor does."""
    import csv
    import io
    if len(raw) > 500_000:
        return [], ("hw_err_csv", None)
    try:
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
    except (UnicodeDecodeError, csv.Error):
        return [], ("hw_err_csv", None)
    if not rows or not {"kind", "prompt", "answer"} <= set(rows[0].keys()):
        return [], ("hw_err_csv", None)
    return clean_questions([{k: (v or "") for k, v in r.items() if k} for r in rows])


def get(aid: int) -> dict | None:
    with db.conn() as c:
        r = c.execute("SELECT * FROM assignments WHERE id=?", (aid,)).fetchone()
    return dict(r) if r else None


def questions(aid: int, with_answers: bool) -> list[dict]:
    """Students get with_answers=False: the key never leaves the database for them before the deadline."""
    cols = "id, position, kind, prompt, choices, points" + (", answer, tolerance" if with_answers else "")
    with db.conn() as c:
        return [dict(r) for r in c.execute(f"SELECT {cols} FROM hw_questions WHERE assignment_id=? ORDER BY position", (aid,))]


def set_due(aid: int, due_utc: str) -> None:
    with db.conn() as c:
        c.execute("UPDATE assignments SET due_at=? WHERE id=?", (due_utc, aid))


def delete(aid: int) -> None:
    with db.conn() as c:
        c.execute("DELETE FROM assignments WHERE id=?", (aid,))


def submit(aid: int, student_id: str, answers: dict[int, str]) -> str | None:
    """Mark and store one attempt on a 'key' assignment. Returns None on success or an error key."""
    a = get(aid)
    if not a:
        return "err_not_found"
    if a["mode"] != "key":
        return "err_not_found"
    if is_closed(a["due_at"]):
        return "hw_err_closed"
    qs = questions(aid, with_answers=True)
    clipped = {q["id"]: str(answers.get(q["id"], ""))[:300] for q in qs}
    score, mx, _ = grade(qs, clipped)
    try:
        with db.conn() as c:
            c.execute("INSERT INTO submissions (assignment_id, student_id, submitted_at, score, max_score, answers) VALUES (?,?,?,?,?,?)",
                      (aid, student_id, db._now(), score, mx, json.dumps({str(k): v for k, v in clipped.items()})))
    except Exception as e:  # UNIQUE(assignment_id, student_id)
        if "UNIQUE" in str(e):
            return "hw_err_done"
        raise
    return None


def submit_file(aid: int, student_id: str, raw: bytes | None, filename: str | None, text: str = "") -> str | None:
    """Hand in a 'file' assignment: typed text, an uploaded file, both, or neither (e.g. handed in on paper).
    Ungraded: score stays NULL until the teacher grades it. Returns None on success or an error key."""
    a = get(aid)
    if not a:
        return "err_not_found"
    if a["mode"] != "file":
        return "err_not_found"
    if is_closed(a["due_at"]):
        return "hw_err_closed"
    stored_path = safe_name = None
    if raw is not None:
        out = save_file(raw, filename or "submission")
        if isinstance(out, str):
            return out
        stored_path, safe_name = out
    try:
        with db.conn() as c:
            c.execute("INSERT INTO submissions (assignment_id, student_id, submitted_at, max_score, answers, file_name, stored_path)"
                      " VALUES (?,?,?,?,?,?,?)",
                      (aid, student_id, db._now(), a["max_score"], json.dumps({"text": text.strip()[:20000]}), safe_name, stored_path))
    except Exception as e:  # UNIQUE(assignment_id, student_id)
        if "UNIQUE" in str(e):
            return "hw_err_done"
        raise
    return None


def grade_file(aid: int, student_id: str, score: float, comment: str, grader: str) -> str | None:
    a = get(aid)
    if not a:
        return "err_not_found"
    if not (0 <= score <= a["max_score"]):
        return "hw_err_score_range"
    with db.conn() as c:
        cur = c.execute(
            "UPDATE submissions SET score=?, comment=?, graded_by=?, graded_at=? WHERE assignment_id=? AND student_id=?",
            (score, comment.strip()[:1000], grader, db._now(), aid, student_id))
        if cur.rowcount == 0:
            return "hw_err_not_submitted"
    return None


def submission(aid: int, student_id: str) -> dict | None:
    with db.conn() as c:
        r = c.execute("SELECT * FROM submissions WHERE assignment_id=? AND student_id=?", (aid, student_id)).fetchone()
    if not r:
        return None
    d = dict(r)
    raw = json.loads(d["answers"] or "{}")
    d["answers"] = {int(k): v for k, v in raw.items() if str(k).isdigit()}
    d["text"] = str(raw.get("text", ""))
    return d


def submissions_for(aid: int) -> list[dict]:
    with db.conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT student_id, score, max_score, submitted_at, file_name, comment, graded_at FROM submissions WHERE assignment_id=?", (aid,))]


def enrolled_students() -> list[str]:
    """Pseudonymous ids of active student accounts: the students homework applies to."""
    with db.conn() as c:
        return [r[0] for r in c.execute(
            "SELECT DISTINCT student_id FROM users WHERE role='student' AND active=1 AND student_id IS NOT NULL ORDER BY student_id")]


def student_overview(student_id: str) -> list[dict]:
    """Every assignment with this student's mark (None = not submitted, or submitted but not yet graded)."""
    with db.conn() as c:
        rows = c.execute(
            "SELECT a.id, a.title, a.due_at, a.mode, a.category, a.course_id, c.name AS course_name, s.score, s.max_score, s.submitted_at, s.file_name, s.comment "
            "FROM assignments a LEFT JOIN courses c ON c.id=a.course_id "
            "LEFT JOIN submissions s ON s.assignment_id=a.id AND s.student_id=? "
            "ORDER BY a.due_at DESC, a.id DESC",
            (student_id,)).fetchall()
    return [dict(r) for r in rows]


# ---------- live figures for the model ----------
def live_stats(now: datetime | None = None) -> dict[str, dict[str, float]]:
    """Per enrolled student, from CLOSED assignments only:

      hw_closed, hw_handed   homework assignments that are closed / that the student handed in
      hw_graded, hw_avg      how many handed-in homework have a mark, and their average mark %
      test_n, test_sum       closed tests/exams that count (marked, or missed = 0 marks) and the sum of their mark %

    A 'file' submission counts as handed in as soon as it arrives; its mark only counts once graded.
    A closed test or exam the student never handed in counts as 0, because a missed exam is a failed exam;
    a handed-in but not yet graded one is left out until the teacher marks it.
    """
    now = now or now_utc()
    closed = [a for a in list_assignments() if is_closed(a["due_at"], now)]
    students = enrolled_students()
    if not closed or not students:
        return {}
    cat = {a["id"]: a["category"] for a in closed}
    out = {s: {"hw_closed": 0, "hw_handed": 0, "hw_graded": 0, "hw_avg": 0.0, "test_n": 0, "test_sum": 0.0} for s in students}
    hw_closed = sum(1 for a in closed if a["category"] == "homework")
    for s in students:
        out[s]["hw_closed"] = hw_closed
    seen: set[tuple[str, int]] = set()
    marks: dict[str, list[float]] = {s: [] for s in students}
    with db.conn() as c:
        q = ",".join("?" * len(cat))
        for r in c.execute(f"SELECT assignment_id, student_id, score, max_score FROM submissions WHERE assignment_id IN ({q})", list(cat)):
            sid = r["student_id"]
            if sid not in out:
                continue
            seen.add((sid, r["assignment_id"]))
            pct = 100.0 * r["score"] / r["max_score"] if r["score"] is not None and r["max_score"] > 0 else None
            if cat[r["assignment_id"]] == "homework":
                out[sid]["hw_handed"] += 1
                if pct is not None:
                    marks[sid].append(pct)
            elif pct is not None:
                out[sid]["test_n"] += 1
                out[sid]["test_sum"] += pct
    for sid in students:  # missed tests and exams count as 0
        for aid, cname in cat.items():
            if cname != "homework" and (sid, aid) not in seen:
                out[sid]["test_n"] += 1
    for sid, m in marks.items():
        out[sid]["hw_graded"] = len(m)
        out[sid]["hw_avg"] = sum(m) / len(m) if m else 0.0
    return out


def blend(csv_value: float, live_sum: float, live_n: int) -> float:
    """Mix the earlier CSV figure (weight PRIOR) with the live figures (weight live_n)."""
    return (PRIOR * csv_value + live_sum) / (PRIOR + live_n)


CSV_TEMPLATE = (
    "kind,prompt,choices,answer,tolerance,points\n"
    "number,What is 17 * 3?,,51,0,2\n"
    "text,Which protocol secures web traffic with TLS?,,https,,1\n"
    "choice,Which of these is a hash function?,AES|SHA-256|RSA,SHA-256,,1\n"
)


# ---------- courses ----------
def course_overview(student_id: str | None = None) -> list[dict]:
    """One row per course: assignment counts, next open deadline and (for a student) their own average mark."""
    now = now_utc()
    names = courses()
    rows = []
    subs: dict[int, dict] = {}
    if student_id:
        with db.conn() as c:
            for r in c.execute("SELECT assignment_id, score, max_score FROM submissions WHERE student_id=?", (student_id,)):
                subs[r["assignment_id"]] = dict(r)
    allas = list_assignments()
    for course in names:
        mine = [a for a in allas if a["course_id"] == course["id"]]
        open_ = [a for a in mine if not is_closed(a["due_at"], now)]
        marks = [100.0 * subs[a["id"]]["score"] / subs[a["id"]]["max_score"]
                 for a in mine if a["id"] in subs and subs[a["id"]]["score"] is not None and subs[a["id"]]["max_score"] > 0]
        rows.append({
            "id": course["id"], "name": course["name"], "assignments": len(mine), "open": len(open_),
            "next_due": min((a["due_at"] for a in open_), default=None),
            "avg": sum(marks) / len(marks) if marks else None,
        })
    return rows
