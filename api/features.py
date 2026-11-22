"""Web adapters for existing core features. All sensitive endpoints require role checks.
No new machine-learning/business logic is introduced by this module.
"""
from __future__ import annotations
import base64
import binascii
import io
from datetime import datetime
from typing import Any
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from core import data, db, homework, model, service
from core.data import FEATURES, RANGES, WEEK_COLS
router = APIRouter(prefix='/api')

def _fail(error: str, status: int=400):
    raise HTTPException(status, detail=error)

def _row(sid: str):
    b = service.live()
    matched = b.df.loc[b.df.student_id == sid]
    if matched.empty:
        raise HTTPException(404, 'student_not_found')
    return (b, matched.iloc[0])

def _basic(r):
    return {'student_id': str(r.student_id), 'group': str(r['group']), 'tier': str(r.tier), 'risk': round(float(r.risk) * 100), 'agreement': str(r.agreement), 'attendance': round(float(r.attendance), 1), 'test_avg': round(float(r.test_avg), 1), 'hw_completion': round(float(r.hw_completion), 1), 'weeks': [round(float(r[w]), 1) for w in WEEK_COLS]}

def _reasons(r, med):
    return [{'feature': f, 'value': round(float(r[f]), 2), 'median': round(float(med[f]), 2)} for f, _ in r.reasons]

def _files(items: list[dict]) -> list[tuple[bytes, str]]:
    result = []
    if len(items) > 3:
        _fail('too_many_files')
    for obj in items:
        filename = str(obj.get('name', ''))[:200]
        raw = str(obj.get('data', ''))
        if len(raw) > 28000000:
            _fail('hw_err_size')
        try:
            content = base64.b64decode(raw, validate=True)
        except (ValueError, binascii.Error):
            _fail('bad_file')
        if len(content) > 20000000:
            _fail('hw_err_size')
        result.append((content, filename))
    return result

def summarize_recent_activity(weeks: list[float]) -> dict[str, float | str]:
    """Report recent *observed* engagement, not an unreliable linear forecast.

    The latest four weekly summaries are too noisy to extrapolate four more
    weeks. A falling trend is a supportive message, never a projected zero.
    """
    recent = [float(x) for x in weeks[-4:] if np.isfinite(float(x))]
    if not recent:
        return {'recent_average': 0.0, 'status': 'unknown'}
    average = round(float(np.mean(recent)), 1)
    if len(recent) < 4:
        status = 'unknown'
    elif recent[-1] <= recent[0] - 10:
        status = 'falling'
    elif recent[-1] >= recent[0] + 10:
        status = 'rising'
    else:
        status = 'steady'
    return {'recent_average': average, 'status': status}

class Note(BaseModel):
    body: str = Field(min_length=1, max_length=1000)

class PredictInput(BaseModel):
    values: dict[str, float]

class CsvInput(BaseModel):
    content: str = Field(max_length=2000000)

class NewAssignment(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default='', max_length=2000)
    due_local: str = Field(max_length=30)
    course_id: int | None = None
    category: str = 'homework'
    mode: str = 'key'
    max_score: float = 100
    questions: list[dict[str, Any]] = Field(default_factory=list, max_length=100)
    materials: list[dict[str, str]] = Field(default_factory=list, max_length=3)

class Due(BaseModel):
    due_local: str = Field(max_length=30)

class Submit(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)
    text: str = Field(default='', max_length=20000)
    file: dict[str, str] | None = None

class Grade(BaseModel):
    student_id: str = Field(max_length=30)
    score: float
    comment: str = Field(default='', max_length=1000)

class NewUser(BaseModel):
    username: str = Field(max_length=40)
    password: str = Field(max_length=200)
    role: str
    student_id: str | None = None

class AccountUpdate(BaseModel):
    role: str | None = None
    student_id: str | None = None
    active: bool | None = None
    password: str | None = Field(default=None, max_length=200)

def setup(app, require_role):
    teacher = require_role('teacher')
    student = require_role('student')
    teacher_or_student = require_role('teacher', 'student')
    admin = require_role('admin')

    @router.get('/students')
    def students(user=Depends(teacher)):
        """Teacher only. Return all pseudonymous students in the cohort."""
        b = service.live()
        records = [_basic(r) for _, r in b.df.sort_values('student_id').iterrows()]
        return {'students': records, 'total': len(records), 'weeks': len(WEEK_COLS), 'demo': b.demo, 'source': b.source}

    @router.get('/students/{sid}')
    def student_detail(sid: str, user=Depends(teacher)):
        """Teacher only. Return academic indicators, notes and assignment statuses for one student."""
        b, r = _row(sid)
        return {'student': _basic(r), 'reasons': _reasons(r, b.class_median), 'features': {f: round(float(r[f]), 1) for f in FEATURES}, 'medians': {f: round(float(b.class_median[f]), 1) for f in FEATURES}, 'class_weeks': [round(float(b.class_median[w]), 1) for w in WEEK_COLS], 'contacted': sid in db.contacted(), 'notes': db.get_notes(sid), 'assignments': homework.student_overview(sid), 'demo': b.demo, 'source': b.source}

    @router.post('/students/{sid}/reveal')
    def reveal(sid: str, user=Depends(teacher)):
        """Teacher only. Reveal a demo student name and audit the action; historical records have none."""
        b, _ = _row(sid)
        if not b.demo:
            _fail('no_names_in_anonymized_data', 404)
        db.log(user['username'], 'reveal_name', sid)
        return {'name': db.get_name(sid)}

    @router.post('/students/{sid}/contact')
    def contact(sid: str, user=Depends(teacher)):
        """Teacher only. Toggle whether a student has been contacted."""
        _row(sid)
        val = db.toggle_contacted(sid, user['username'])
        db.log(user['username'], 'mark_contacted' if val else 'unmark_contacted', sid)
        return {'contacted': val}

    @router.post('/students/{sid}/notes')
    def note(sid: str, body: Note, user=Depends(teacher)):
        """Teacher only. Add a private teacher note for a pseudonymous student."""
        _row(sid)
        db.add_note(sid, user['username'], body.body)
        db.log(user['username'], 'add_note', sid)
        return {'notes': db.get_notes(sid)}

    @router.get('/model')
    def model_page(user=Depends(teacher)):
        """Teacher only. Show held-out model evaluation and feature importance."""
        b = service.bundle()
        tr = b.tr
        return {'metrics': tr.metrics, 'importance': tr.importance.to_dict('records'), 'tiers': tr.tier_table.to_dict('records'), 'n_train': tr.n_train, 'n_test': tr.n_test, 'base_rate': round(tr.base_rate * 100, 1), 'medians': {f: float(tr.medians[f]) for f in FEATURES}, 'demo': b.demo, 'source': b.source, 'features': FEATURES}

    def _validate(values: dict):
        if set(FEATURES) - set(values):
            _fail('missing_features')
        for f in FEATURES:
            try:
                v = float(values[f])
            except (ValueError, TypeError):
                _fail('bad_feature')
            if not np.isfinite(v) or not RANGES[f][0] <= v <= RANGES[f][1]:
                _fail('range_' + f)
        return {f: float(values[f]) for f in FEATURES}

    @router.post('/predict')
    def predict(body: PredictInput, user=Depends(teacher)):
        """Teacher only. Validate eight inputs, then calculate a model risk score."""
        b = service.bundle()
        vals = _validate(body.values)
        X = pd.DataFrame([vals])
        row = model.predict(b.tr, X).iloc[0]
        contributions = model.contributions(b.tr, X).iloc[0]
        return {'risk': round(float(row.risk) * 100), 'tier': row.tier, 'reasons': [{'feature': f, 'value': vals[f], 'median': float(b.tr.medians[f])} for f, _ in model.top_reasons(contributions)], 'demo': b.demo, 'source': b.source}

    @router.post('/predict/csv')
    def predict_csv(body: CsvInput, user=Depends(teacher)):
        """Teacher only. Score uploaded CSV rows without changing training data."""
        try:
            frame = pd.read_csv(io.StringIO(body.content), nrows=5001)
        except Exception:
            _fail('bad_csv')
        if len(frame) > 5000:
            _fail('too_many_rows')
        problems = data.validate_features(frame)
        if problems:
            return {'problems': problems}
        b = service.bundle()
        p = model.predict(b.tr, frame[FEATURES].apply(pd.to_numeric))
        return {'rows': [{'student_id': str(frame.iloc[i].get('student_id', f'Row {i + 1}'))[:80], 'risk': round(float(p.iloc[i]['risk']) * 100), 'tier': p.iloc[i]['tier']} for i in range(len(frame))]}

    @router.post('/questions/parse-csv')
    def import_questions_csv(body: CsvInput, user=Depends(teacher)):
        """Teacher only. Parse questions CSV for the assignment editor."""
        raw = body.content.encode('utf-8-sig')
        questions, error = homework.questions_from_csv(raw)
        if error:
            _fail(error[0])
        return {'questions': questions}

    @router.get('/courses')
    def courses(user=Depends(teacher_or_student)):
        """Teacher or Student. Show course statistics for the authorized user."""
        return {'courses': homework.course_overview(user.get('student_id') if user['role'] == 'student' else None), 'source': service.bundle().source}

    @router.get('/assignments')
    def assignments(user=Depends(teacher_or_student)):
        """Teacher or Student. List assignments and the user-visible submission state."""
        items = homework.list_assignments()
        sid = user.get('student_id')
        my = {i['id']: i for i in homework.student_overview(sid)} if sid and user['role'] == 'student' else {}
        cnt = {i['id']: len(homework.submissions_for(i['id'])) for i in items} if user['role'] == 'teacher' else {}
        return {'assignments': [{**a, 'closed': homework.is_closed(a['due_at']), 'submitted_count': cnt.get(a['id']) if user['role'] == 'teacher' else None, 'mine': my.get(a['id']) if user['role'] == 'student' else None} for a in items], 'courses': homework.courses()}

    @router.get('/assignments/{aid}')
    def assignment_detail(aid: int, user=Depends(teacher_or_student)):
        """Teacher or Student. Hide answer keys from students and show authorized submissions."""
        a = homework.get(aid)
        if a is None:
            _fail('err_not_found', 404)
        teach = user['role'] == 'teacher'
        sid = user.get('student_id')
        subs = homework.submissions_for(aid) if teach else []
        mine = homework.submission(aid, sid) if sid and (not teach) else None
        if mine:
            mine.pop('stored_path', None)
        details = {}
        for row in subs:
            detail = homework.submission(aid, row['student_id'])
            details[row['student_id']] = {'text': detail.get('text', ''), 'answers': detail.get('answers', {})} if detail else {}
        return {'assignment': {**a, 'closed': homework.is_closed(a['due_at'])}, 'questions': homework.questions(aid, with_answers=teach), 'materials': [{'id': m['id'], 'filename': m['filename'], 'size_bytes': m['size_bytes']} for m in homework.materials_for(aid)], 'submissions': subs, 'submission_details': details if teach else {}, 'mine': mine}

    @router.post('/assignments')
    def assignment_create(body: NewAssignment, user=Depends(teacher)):
        """Teacher only. Validate and create a quiz or teacher-graded assignment."""
        if body.course_id not in {c['id'] for c in homework.courses()}:
            _fail('invalid_course')
        if body.category not in homework.CATEGORIES:
            _fail('invalid_category')
        try:
            local = datetime.fromisoformat(body.due_local)
            if local.tzinfo is not None:
                _fail('invalid_local_time')
            due = homework.local_to_utc(local)
            if homework.is_closed(due):
                _fail('deadline_in_past')
        except ValueError:
            _fail('invalid_date')
        files = _files(body.materials)
        if body.mode == 'key':
            qs, err = homework.clean_questions(body.questions)
            if err:
                _fail(err[0])
            if not qs:
                _fail('no_questions')
            result = homework.create(body.title, body.description, due, user['username'], qs, body.course_id, body.category, files)
        elif body.mode == 'file':
            result = homework.create_file_assignment(body.title, body.description, due, user['username'], body.max_score, files, body.course_id, body.category)
        else:
            _fail('invalid_mode')
        if isinstance(result, str):
            _fail(result)
        db.log(user['username'], 'create_assignment', str(result))
        return {'id': result}

    @router.put('/assignments/{aid}/due')
    def assignment_due(aid: int, body: Due, user=Depends(teacher)):
        """Teacher only. Update an assignment deadline after validation."""
        if not homework.get(aid):
            _fail('err_not_found', 404)
        try:
            local = datetime.fromisoformat(body.due_local)
            if local.tzinfo is not None:
                _fail('invalid_local_time')
            due = homework.local_to_utc(local)
            if homework.is_closed(due):
                _fail('deadline_in_past')
        except ValueError:
            _fail('invalid_date')
        homework.set_due(aid, due)
        db.log(user['username'], 'change_deadline', str(aid))
        return {'ok': True}

    @router.delete('/assignments/{aid}')
    def assignment_delete(aid: int, user=Depends(teacher)):
        """Teacher only. Delete an assignment and its dependent records."""
        if not homework.get(aid):
            _fail('err_not_found', 404)
        homework.delete(aid)
        db.log(user['username'], 'delete_assignment', str(aid))
        return {'ok': True}

    @router.post('/assignments/{aid}/submit')
    def assignment_submit(aid: int, body: Submit, user=Depends(student)):
        """Student only. Submit answers or one permitted file before the deadline."""
        sid = user.get('student_id')
        if not sid:
            _fail('hm_no_link')
        a = homework.get(aid)
        if not a:
            _fail('err_not_found', 404)
        if a['mode'] == 'key':
            answers = {int(k): v[:300] for k, v in body.answers.items() if k.isdigit()}
            error = homework.submit(aid, sid, answers)
        else:
            upload = _files([body.file]) if body.file else []
            error = homework.submit_file(aid, sid, upload[0][0] if upload else None, upload[0][1] if upload else None, body.text)
        if error:
            _fail(error)
        db.log(user['username'], 'submit_assignment', f'{aid}:{sid}')
        return {'ok': True}

    @router.post('/assignments/{aid}/grade')
    def assignment_grade(aid: int, body: Grade, user=Depends(teacher)):
        """Teacher only. Grade and comment on a student written submission."""
        error = homework.grade_file(aid, body.student_id, body.score, body.comment, user['username'])
        if error:
            _fail(error)
        db.log(user['username'], 'grade_assignment', f'{aid}:{body.student_id}')
        return {'ok': True}

    @router.get('/materials/{mid}')
    def material(mid: int, user=Depends(teacher_or_student)):
        """Teacher or Student. Download permitted assignment materials."""
        with db.conn() as c:
            m = c.execute('SELECT filename,stored_path FROM materials WHERE id=?', (mid,)).fetchone()
        if m is None:
            _fail('err_not_found', 404)
        raw = homework.read_file(m['stored_path'])
        if raw is None:
            _fail('err_not_found', 404)
        from urllib.parse import quote
        return Response(raw, media_type='application/octet-stream', headers={'Content-Disposition': "attachment; filename*=UTF-8''" + quote(m['filename'])})

    @router.get('/submissions/{aid}/{sid}/file')
    def submission_file(aid: int, sid: str, user=Depends(teacher)):
        """Teacher only. Download a submitted document for grading."""
        sub = homework.submission(aid, sid)
        if not sub or not sub.get('stored_path'):
            _fail('err_not_found', 404)
        raw = homework.read_file(sub['stored_path'])
        if raw is None:
            _fail('err_not_found', 404)
        from urllib.parse import quote
        return Response(raw, media_type='application/octet-stream', headers={'Content-Disposition': "attachment; filename*=UTF-8''" + quote(sub['file_name'])})

    @router.get('/home')
    def home(user=Depends(student)):
        """Student only. Return only personal progress and observed activity, never a risk tier."""
        sid = user.get('student_id')
        if not sid:
            return {'linked': False}
        try:
            b, r = _row(sid)
        except HTTPException:
            return {'linked': False}
        weeks = [float(r[w]) for w in WEEK_COLS]
        pace = summarize_recent_activity(weeks)
        future = [pace['recent_average']] * 4
        own = {f: round(float(r[f]), 1) for f in ('attendance', 'test_avg', 'hw_completion')}
        due = [a for a in homework.student_overview(sid) if not homework.is_closed(a['due_at']) and (not a['submitted_at'])]
        due.sort(key=lambda r: r['due_at'])
        overall = round(float(np.mean(list(own.values()))), 1)
        return {'linked': True, 'student_id': sid, 'overall': overall, 'features': own, 'targets': {'attendance': 75, 'test_avg': 60, 'hw_completion': 80, 'weekly_activity': 55}, 'weeks': weeks, 'projected': future, 'recent_average': pace['recent_average'], 'pace_status': pace['status'], 'on_pace': pace['recent_average'] >= 55, 'due': due[:3], 'demo': b.demo, 'source': b.source}

    @router.get('/accounts')
    def accounts(user=Depends(admin)):
        """Admin only. List account metadata and the audit trail."""
        b = service.bundle()
        return {'users': db.list_users(), 'audit': db.get_audit(100), 'student_ids': b.df.student_id.tolist(), 'demo': b.demo, 'source': b.source}

    @router.post('/accounts')
    def account_create(body: NewUser, user=Depends(admin)):
        """Admin only. Create a validated account with an optional student link."""
        if body.role == 'student' and body.student_id not in service.bundle().df.student_id.values:
            _fail('err_student_link')
        if body.role == 'student' and any((u['student_id'] == body.student_id for u in db.list_users())):
            _fail('student_link_taken')
        err = db.create_user(body.username, body.password, body.role, body.student_id)
        if err:
            _fail(err)
        db.log(user['username'], 'create_user', f'{body.username} ({body.role})')
        return {'ok': True}

    @router.patch('/accounts/{uid}')
    def account_update(uid: int, body: AccountUpdate, user=Depends(admin)):
        """Admin only. Change role, active flag or password, preserving last-admin safeguards."""
        users = {u['id']: u for u in db.list_users()}
        target = users.get(uid)
        if target is None:
            _fail('err_not_found', 404)
        if target['username'] == user['username'] and (body.active is False or (body.role and body.role != 'admin')):
            _fail('cannot_disable_self')
        if body.role is not None:
            if body.role not in db.ROLES:
                _fail('err_role')
            if body.role == 'student':
                sid = body.student_id or target['student_id']
                if sid not in service.bundle().df.student_id.values:
                    _fail('err_student_link')
                if any((u['id'] != uid and u['student_id'] == sid for u in users.values())):
                    _fail('student_link_taken')
            else:
                sid = None
            err = db.set_role(uid, body.role, sid)
            if err:
                _fail(err)
            db.log(user['username'], 'set_role', f"{target['username']} -> {body.role}")
        if body.active is not None:
            err = db.set_active(uid, body.active)
            if err:
                _fail(err)
            db.log(user['username'], 'activate' if body.active else 'deactivate', target['username'])
        if body.password is not None:
            err = db.reset_password(uid, body.password)
            if err:
                _fail(err)
            db.log(user['username'], 'reset_password', target['username'])
        return {'ok': True}
    app.include_router(router)
