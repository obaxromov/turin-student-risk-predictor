"""Homework: marking, validation, deadlines, one attempt, and the live effect on the risk model."""
from datetime import timedelta

import pytest

from core import data, db, homework, service


@pytest.fixture()
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "hw.db")
    db.init_db(data.student_ids(), demo=True)
    return db


def _due(delta_hours):
    return (homework.now_utc() + timedelta(hours=delta_hours)).strftime(homework.FMT)


def _make(due_hours=24, title="HW1"):
    qs, err = homework.clean_questions([
        {"kind": "number", "prompt": "2+2", "answer": "4", "tolerance": 0, "points": 2},
        {"kind": "text", "prompt": "Protocol for secure web", "answer": "HTTPS | https secure", "points": 1},
        {"kind": "choice", "prompt": "Pick", "choices": "a|b|c", "answer": "B", "points": 1},
    ])
    assert err is None
    return homework.create(title, "", _due(due_hours), "teacher1", qs)


def test_checking_rules():
    n = {"kind": "number", "answer": "3.14", "tolerance": 0.01}
    assert homework.check(n, "3,15") and not homework.check(n, "3.2") and not homework.check(n, "abc") and not homework.check(n, "nan")
    t_ = {"kind": "text", "answer": "HTTPS|TLS"}
    assert homework.check(t_, "  https ") and homework.check(t_, "tls") and not homework.check(t_, "http")
    c = {"kind": "choice", "answer": "Blue"}
    assert homework.check(c, "blue") and not homework.check(c, "red") and not homework.check(c, None)


@pytest.mark.parametrize("row,why", [
    ({"kind": "x", "prompt": "q", "answer": "1"}, "hw_why_kind"),
    ({"kind": "number", "prompt": "q", "answer": "abc"}, "hw_why_number"),
    ({"kind": "choice", "prompt": "q", "choices": "a", "answer": "a"}, "hw_why_choices"),
    ({"kind": "choice", "prompt": "q", "choices": "a|b", "answer": "z"}, "hw_why_choices"),
    ({"kind": "text", "prompt": "", "answer": "x"}, "hw_why_prompt"),
    ({"kind": "text", "prompt": "q", "answer": ""}, "hw_why_answer"),
    ({"kind": "text", "prompt": "q", "answer": "x", "points": 0}, "hw_why_points"),
])
def test_bad_questions_are_rejected_with_row_number(row, why):
    qs, err = homework.clean_questions([row])
    assert qs == [] and err == (why, 1)


def test_empty_table_is_rejected():
    assert homework.clean_questions([{"kind": "number", "prompt": "", "answer": ""}])[1] == ("hw_err_noq", None)


def test_submit_marks_once_and_hides_key_from_students(fresh_db):
    aid = _make()
    qs = homework.questions(aid, with_answers=False)
    assert all("answer" not in q for q in qs)
    keyed = homework.questions(aid, with_answers=True)
    ans = {keyed[0]["id"]: "4", keyed[1]["id"]: "https", keyed[2]["id"]: "a"}
    assert homework.submit(aid, "S001", ans) is None
    sub = homework.submission(aid, "S001")
    assert (sub["score"], sub["max_score"]) == (3, 4)
    assert homework.submit(aid, "S001", ans) == "hw_err_done"


def test_closed_assignment_rejects_submission(fresh_db):
    aid = _make(due_hours=-1)
    assert homework.submit(aid, "S001", {}) == "hw_err_closed"


def test_delete_removes_questions_and_marks(fresh_db):
    aid = _make()
    keyed = homework.questions(aid, with_answers=True)
    homework.submit(aid, "S001", {keyed[0]["id"]: "4"})
    homework.delete(aid)
    assert homework.get(aid) is None and homework.submissions_for(aid) == []


def test_only_closed_assignments_feed_live_stats(fresh_db):
    _make(due_hours=24, title="open")
    assert homework.live_stats() == {}
    _make(due_hours=-2, title="closed")
    stats = homework.live_stats()
    assert set(stats) == set(homework.enrolled_students()) and stats["S001"]["hw_closed"] == 1 and stats["S001"]["hw_handed"] == 0


def test_missing_homework_raises_risk_and_marks_lower_it(fresh_db):
    base = service.bundle().df.set_index("student_id")
    for i in range(4):
        _make(due_hours=-2 - i, title=f"old{i}")
    after = service.live().df.set_index("student_id")
    assert after.loc["S001", "hw_completion"] < base.loc["S001", "hw_completion"]
    assert after.loc["S001", "risk"] >= base.loc["S001", "risk"]
    assert after.loc["S050", "risk"] == base.loc["S050", "risk"]  # no account -> unchanged
    # full marks on every assignment keep completion up
    for a in homework.list_assignments():
        keyed = homework.questions(a["id"], with_answers=True)
        with db.conn() as c:
            c.execute("INSERT INTO submissions (assignment_id, student_id, submitted_at, score, max_score, answers) VALUES (?,?,?,?,?,?)",
                      (a["id"], "S001", "2026-01-01 00:00", 4, 4, "{}"))
    better = service.live().df.set_index("student_id")
    assert better.loc["S001", "hw_completion"] > after.loc["S001", "hw_completion"]
    assert better.loc["S001", "risk"] <= after.loc["S001", "risk"]


# ---- courses, categories, written work ----
def _file_assignment(category, due_hours, title="Written", course=None, mats=None):
    return homework.create_file_assignment(title, "", _due(due_hours), "teacher1", 100, mats or [], course, category)


def test_thirteen_courses(fresh_db):
    names = [c["name"] for c in homework.courses()]
    assert len(names) == 13 and "Data Structures and Algorithms" in names and "Religious Studies" in names


def test_exam_marks_feed_test_average_and_missed_exam_is_zero(fresh_db):
    aid = _file_assignment("exam", -2)
    stats = homework.live_stats()
    assert stats["S001"]["test_n"] == 1 and stats["S001"]["test_sum"] == 0  # missed
    with db.conn() as c:
        c.execute("INSERT INTO submissions (assignment_id, student_id, submitted_at, score, max_score, answers) VALUES (?,?,?,?,?,?)",
                  (aid, "S001", "2026-01-01 00:00", 80, 100, "{}"))
    stats = homework.live_stats()
    assert stats["S001"]["test_n"] == 1 and stats["S001"]["test_sum"] == 80
    assert stats["S001"]["hw_closed"] == 0  # an exam is not homework


def test_written_submission_text_then_manual_grade(fresh_db):
    aid = _file_assignment("homework", 24)
    assert homework.submit_file(aid, "S001", None, None, text="my essay") is None
    s = homework.submission(aid, "S001")
    assert s["score"] is None and "my essay" in str(s)
    assert homework.submit_file(aid, "S001", None, None, text="again") is not None  # one attempt only
    assert homework.grade_file(aid, "S001", 150, "", "teacher1") is not None  # above the maximum
    assert homework.grade_file(aid, "S001", 70, "good", "teacher1") is None
    assert homework.submission(aid, "S001")["score"] == 70


def test_empty_written_submission_counts_as_handed_in_on_paper(fresh_db):
    aid = _file_assignment("homework", 24)
    assert homework.submit_file(aid, "S001", None, None) is None


def test_file_validation_and_materials(fresh_db):
    assert isinstance(homework.save_file(b"x", "malware.exe"), str)
    assert isinstance(homework.save_file(b"x" * (21 * 1024 * 1024), "big.pdf"), str)
    ok = homework.save_file(b"%PDF-1.4", "notes.pdf")
    assert not isinstance(ok, str) and homework.read_file(ok[0]) == b"%PDF-1.4"
    assert homework.read_file("../../etc/passwd") is None
    aid = _file_assignment("homework", 24, mats=[(b"book", "book.txt")])
    assert [m["filename"] for m in homework.materials_for(aid)] == ["book.txt"]


def test_course_overview_and_filter(fresh_db):
    cid = homework.courses()[0]["id"]
    _file_assignment("homework", 24, course=cid)
    _make(due_hours=24)
    rows = {r["id"]: r for r in homework.course_overview("S001")}
    assert rows[cid]["assignments"] == 1 and rows[cid]["open"] == 1
    assert len(homework.list_assignments(cid)) == 1 and len(homework.list_assignments()) == 2


def test_csv_import_roundtrip(fresh_db):
    qs, err = homework.questions_from_csv(homework.CSV_TEMPLATE.encode() if isinstance(homework.CSV_TEMPLATE, str) else homework.CSV_TEMPLATE)
    assert err is None and len(qs) >= 1
