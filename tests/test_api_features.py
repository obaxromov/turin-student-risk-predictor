"""End-to-end API checks across all 3 roles, using temporary SQLite from conftest."""
import base64
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from api.main import app
from core.data import FEATURES

@pytest.fixture
def client():
    with TestClient(app) as c: yield c

def auth(c, role):
    r=c.post('/api/demo-login',json={'role':role})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['token']}

def test_all_180_students_and_audited_reveal(client):
    teacher=auth(client,'teacher'); student=auth(client,'student')
    result=client.get('/api/students',headers=teacher)
    assert result.status_code==200,result.text
    arr=result.json()['students']
    assert len(arr)==180 and arr[0]['student_id']=='S001' and arr[-1]['student_id']=='S180'
    assert all(len(r['weeks'])==8 for r in arr)
    assert all('name' not in r for r in arr)
    assert client.get('/api/students',headers=student).status_code==403
    assert client.get('/api/students/S001',headers=student).status_code==403
    reveal=client.post('/api/students/S001/reveal',headers=teacher)
    assert reveal.status_code==200 and reveal.json()['name']
    assert client.post('/api/students/S001/notes',headers=teacher,json={'body':'Study plan discussed'}).status_code==200
    assert any('Study plan discussed' in n['body'] for n in client.get('/api/students/S001',headers=teacher).json()['notes'])
    assert client.post('/api/students/S001/contact',headers=teacher).status_code==200
    assert client.post('/api/students/S001/contact',headers=teacher).status_code==200
    audit=client.get('/api/accounts',headers=auth(client,'admin')).json()['audit']
    assert any(a['action']=='reveal_name' for a in audit)

def test_model_predictions_and_student_privacy(client):
    teacher=auth(client,'teacher');student=auth(client,'student')
    model=client.get('/api/model',headers=teacher).json()
    assert len(model['features'])==8 and 'roc_auc' in model['metrics']
    assert client.get('/api/model',headers=student).status_code==403
    row=client.get('/api/home',headers=student).json()
    assert row['linked'] and len(row['weeks'])==8 and len(row['projected'])==4
    assert 'tier' not in row and 'risk' not in row and 'class_median' not in row
    vals={f:float(model['medians'][f]) for f in FEATURES}
    pred=client.post('/api/predict',headers=teacher,json={'values':vals})
    assert pred.status_code==200 and pred.json()['tier'] in ('help','watch','ok')
    bad=vals.copy();bad['attendance']=700
    assert client.post('/api/predict',headers=teacher,json={'values':bad}).status_code==400
    assert client.post('/api/predict',headers=student,json={'values':vals}).status_code==403
    content='student_id,'+','.join(FEATURES)+'\nSTEST,'+','.join(str(vals[f]) for f in FEATURES)+'\n'
    csv=client.post('/api/predict/csv',headers=teacher,json={'content':content})
    assert csv.status_code==200 and len(csv.json()['rows'])==1

def test_teacher_create_student_submit_teacher_mark_and_material(client):
    teacher=auth(client,'teacher');student=auth(client,'student')
    future=(datetime.now()+timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
    payload={'title':'Test API written','description':'Describe the answer','due_local':future,'course_id':1,
             'category':'homework','mode':'file','max_score':100,
             'materials':[{'name':'instructions.txt','data':base64.b64encode(b'Read before submitting').decode()}]}
    r=client.post('/api/assignments',headers=teacher,json=payload)
    assert r.status_code==200,r.text
    aid=r.json()['id']
    assert any(a['id']==aid for a in client.get('/api/assignments',headers=student).json()['assignments'])
    sd=client.get(f'/api/assignments/{aid}',headers=student).json()
    assert len(sd['materials'])==1
    mid=sd['materials'][0]['id']
    assert client.get(f'/api/materials/{mid}',headers=student).content==b'Read before submitting'
    submit={'text':'My paper','file':{'name':'submission.txt','data':base64.b64encode(b'my file').decode()}}
    r=client.post(f'/api/assignments/{aid}/submit',headers=student,json=submit)
    assert r.status_code==200,r.text
    assert client.post(f'/api/assignments/{aid}/submit',headers=student,json=submit).status_code==400
    assert client.post(f'/api/assignments/{aid}/grade',headers=student,json={'student_id':'S001','score':76}).status_code==403
    assert client.post(f'/api/assignments/{aid}/grade',headers=teacher,json={'student_id':'S001','score':76,'comment':'Good'}).status_code==200
    assert client.get(f'/api/submissions/{aid}/S001/file',headers=teacher).content==b'my file'
    assert client.get(f'/api/submissions/{aid}/S001/file',headers=student).status_code==403
    assert client.get(f'/api/assignments/{aid}',headers=student).json()['mine']['score']==76
    assert client.delete(f'/api/assignments/{aid}',headers=student).status_code==403
    assert client.delete(f'/api/assignments/{aid}',headers=teacher).status_code==200

def test_autograde_students_do_not_get_keys(client):
    teacher=auth(client,'teacher');student=auth(client,'student')
    future=(datetime.now()+timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
    r=client.post('/api/assignments',headers=teacher,json={
        'title':'Test API quiz','due_local':future,'course_id':2,'mode':'key',
        'questions':[{'kind':'number','prompt':'Two plus two?','answer':'4','points':10,'tolerance':0,'choices':''}]})
    assert r.status_code==200,r.text
    aid=r.json()['id']
    question=client.get(f'/api/assignments/{aid}',headers=student).json()['questions'][0]
    assert 'answer' not in question and 'tolerance' not in question
    assert client.get(f'/api/assignments/{aid}',headers=teacher).json()['questions'][0]['answer']=='4'
    r=client.post(f'/api/assignments/{aid}/submit',headers=student,json={'answers':{str(question['id']):'4'}})
    assert r.status_code==200,r.text
    score=client.get(f'/api/assignments/{aid}',headers=student).json()['mine']['score']
    assert score==10.0
    client.delete(f'/api/assignments/{aid}',headers=teacher)

def test_admin_crud_and_last_admin_guard(client):
    admin=auth(client,'admin');teacher=auth(client,'teacher')
    assert client.get('/api/accounts',headers=teacher).status_code==403
    r=client.post('/api/accounts',headers=admin,json={
        'username':'v6tempuser','password':'testpass456','role':'student','student_id':'S170'})
    assert r.status_code==200,r.text
    users=client.get('/api/accounts',headers=admin).json()['users']
    target=next(u for u in users if u['username']=='v6tempuser')
    assert client.patch(f'/api/accounts/{target["id"]}',headers=admin,json={'role':'teacher'}).status_code==200
    assert client.patch(f'/api/accounts/{target["id"]}',headers=admin,json={'password':'newpass888'}).status_code==200
    assert client.patch(f'/api/accounts/{target["id"]}',headers=admin,json={'active':False}).status_code==200
    assert client.post('/api/login',json={'username':'v6tempuser','password':'newpass888'}).status_code==401
    me=next(u for u in users if u['username']=='admin1')
    assert client.patch(f'/api/accounts/{me["id"]}',headers=admin,json={'active':False}).status_code==400
    assert client.patch(f'/api/accounts/{me["id"]}',headers=admin,json={'role':'student','student_id':'S179'}).status_code==400


def test_import_question_csv_for_teacher(client):
    teacher=auth(client,'teacher')
    student=auth(client,'student')
    content='kind,prompt,answer,points,tolerance,choices\nnumber,What is 1+1?,2,5,0,\n'
    good=client.post('/api/questions/parse-csv',headers=teacher,json={'content':content})
    assert good.status_code==200,good.text
    assert len(good.json()['questions'])==1
    assert client.post('/api/questions/parse-csv',headers=student,json={'content':content}).status_code==403
