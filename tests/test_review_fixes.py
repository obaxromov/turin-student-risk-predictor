"""November reviewer acceptance tests (A, B, C). No real OULAD score is faked."""
from datetime import datetime, timedelta
from pathlib import Path
import re

from fastapi.testclient import TestClient
from api import main as api_main
from api.features import summarize_recent_activity
from core import db

ROOT = Path(__file__).resolve().parents[1]


def auth(client, role):
    response = client.post('/api/demo-login', json={'role': role})
    assert response.status_code == 200, response.text
    return {'Authorization': 'Bearer ' + response.json()['token']}


def test_a1_falling_activity_is_message_not_zero_forecast():
    row = summarize_recent_activity([75, 67, 62, 57, 21, 3.5, 0, 0])
    assert row['status'] == 'falling'
    assert row['recent_average'] == 6.1
    assert summarize_recent_activity([12, 11])['status'] == 'unknown'
    js = (ROOT / 'web/pages.js').read_text()
    assert "class:'projection-big'" not in js
    assert "t('pace'" in js


def test_a1_home_endpoint_does_not_leak_risk_or_median():
    with TestClient(api_main.app) as client:
        response = client.get('/api/home', headers=auth(client, 'student'))
        assert response.status_code == 200
        body = response.json()
        assert body['linked'] and body['pace_status'] in ('falling','rising','steady','unknown')
        assert len(body['projected']) == 4  # old clients still work
        assert set(body).isdisjoint({'risk','tier','class_median','medians'})
        assert body['projected'] == [body['recent_average']] * 4


def test_a2_dark_pill_tokens_and_a3_course_wrapping():
    css = (ROOT / 'web/style.css').read_text()
    assert '--help:#ffabb4;--help-bg:#422a31' in css
    assert '.badge{background:var(--cb);color:var(--c);' in css
    assert 'course-meta' in css and 'overflow-wrap:anywhere' in css


def test_b1_b2_model_captions_and_auc_number():
    js = (ROOT / 'web/pages.js').read_text()
    assert "paneHeading(t('mlSummary'),t('modelSubtitle')" in js
    assert "key==='roc'?Number(v).toFixed(2)" in js
    assert "t(key+'Caption')" in js
    assert "'AUC × 100'" not in js


def test_b4_profile_assignments_show_real_course_name():
    with TestClient(api_main.app) as client:
        teacher = auth(client, 'teacher')
        future = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
        a = client.post('/api/assignments', headers=teacher, json={
            'title':'Profile class display', 'course_id':1, 'due_local':future,
            'mode':'file', 'max_score':20,
        })
        assert a.status_code == 200, a.text
        try:
            detail = client.get('/api/students/S001', headers=teacher).json()
            match = next(r for r in detail['assignments'] if r['title']=='Profile class display')
            assert match['course_name'] == 'Mathematics 1'
            assert 'score' in match and 'submitted_at' in match
            js = (ROOT / 'web/pages.js').read_text()
            assert 'profileAssignmentsTable(d.assignments)' in js
            assert "tableHead([t('assignmentTitle'),t('course'),t('dueDate'),t('status'),t('mark')])" in js
        finally:
            client.delete('/api/assignments/' + str(a.json()['id']), headers=teacher)


def test_b6_all_13_courses_have_translations_and_plural_rules():
    from core.db import COURSES
    js = (ROOT / 'web/pages.js').read_text()
    for name in COURSES:
        assert '"' + name + '":' in js
    assert "'задание'" in js and "'задания'" in js and "'заданий'" in js
    assert 'assignmentCount(c.assignments)' in js
    assert "t('filter_group')" in js


def test_b7_demo_shortcuts_can_be_turned_off(monkeypatch):
    monkeypatch.setattr(api_main, 'DEMO_LOGIN_ENABLED', False)
    with TestClient(api_main.app) as client:
        assert client.get('/api/config').json()['demo_login_enabled'] is False
        assert client.post('/api/demo-login', json={'role':'admin'}).status_code == 404
        # Disabling one-click role login must not disable ordinary credential login.
        assert client.post('/api/login', json={'username':'teacher1','password':'teacher123'}).status_code == 200
    js = (ROOT / 'web/app.js').read_text()
    assert 'S.cfg.demo_login_enabled ? [' in js


def test_c2_body_limit_rejects_large_http_uploads(monkeypatch):
    monkeypatch.setattr(api_main, 'MAX_REQUEST_BYTES', 200)
    with TestClient(api_main.app) as client:
        large = client.post('/api/login', content=b'X' * 300, headers={'content-type':'application/json'})
        assert large.status_code == 413, large.text
        assert large.json()['detail'] == 'request_too_large'
        # Non-API assets should not be subject to the API limit.
        assert client.get('/').status_code == 200


def test_c3_past_assignment_deadline_rejected():
    with TestClient(api_main.app) as client:
        teacher = auth(client, 'teacher')
        past = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        payload = {'title':'Past deadline','course_id':1,'due_local':past,'mode':'file'}
        response = client.post('/api/assignments', json=payload, headers=teacher)
        assert response.status_code == 400
        assert response.json()['detail'] == 'deadline_in_past'


def test_c5_existing_translations_have_three_complete_forms():
    from core.i18n import S
    assert all(len(v) == 3 and all(isinstance(x,str) and x.strip() for x in v) for v in S.values())
    js = (ROOT / 'web/pages.js').read_text()
    for key in ('paceRecent','paceFalling','paceUnknown','modelSubtitle','rocCaption',
                'downloadQuestionTemplate','audit_login_failed','ouladProxyNotes'):
        assert re.search(r'\b'+key+r':\["[^\"]+', js)


def test_c1_role_docstrings_and_endpoint_count():
    import ast
    src=(ROOT/'api/features.py').read_text()
    tree=ast.parse(src)
    docs=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef) and any(isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute)
            and isinstance(d.func.value,ast.Name) and d.func.value.id=='router' for d in n.decorator_list):
            docs.append(ast.get_docstring(n))
    assert len(docs)==23 and all(doc and ('Teacher' in doc or 'Student' in doc or 'Admin' in doc) for doc in docs)
    import tokenize, io
    assert all(not (tok.type == tokenize.OP and tok.string == ';') for tok in tokenize.generate_tokens(io.StringIO(src).readline))
