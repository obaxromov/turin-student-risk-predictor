"""Release-blocker checks for historical cohort isolation and data validation."""
import json
from pathlib import Path

import pandas as pd
import pytest

from core import db, data, service
from tools import verify_oulad


def test_demo_and_imported_cohorts_use_separate_db_files(tmp_path, monkeypatch):
    fake_core = tmp_path / 'core'
    fake_data = tmp_path / 'data'
    fake_core.mkdir()
    fake_data.mkdir()
    monkeypatch.setattr(db, '__file__', str(fake_core / 'db.py'))
    assert db.default_db_path() == fake_data / 'app.db'
    (fake_data / 'history.csv').write_text('failed\n0\n1\n')
    (fake_data / 'current_students.csv').write_text('student_id\nS001\n')
    first = db.default_db_path()
    assert first != fake_data / 'app.db'
    assert first.name.startswith('app-cohort-')
    assert db.default_db_path() == first
    (fake_data / 'current_students.csv').write_text('student_id\nS002\n')
    assert db.default_db_path() != first


def test_no_fictional_names_while_demo_accounts_still_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / 'new.db')
    db.init_db(['S001', 'S002'], demo=True, seed_names=False)
    assert db.authenticate('student1', 'student1pass')['student_id'] == 'S001'
    with db.conn() as c:
        assert c.execute('SELECT COUNT(*) FROM identities').fetchone()[0] == 0


def test_release_validator_refuses_demo_or_missing_data(tmp_path):
    with pytest.raises(ValueError, match='not been imported'):
        verify_oulad.verify(tmp_path, train=False)


def test_release_validator_accepts_complete_historical_csv(tmp_path):
    from tests.test_oulad import _fake
    from tools import prepare_oulad as po
    raw = tmp_path / 'raw';raw.mkdir()
    _fake(raw, n_per=150)
    hist, current = po.build(raw)
    hist.to_csv(tmp_path / 'history.csv', index=False)
    current.to_csv(tmp_path / 'current_students.csv', index=False)
    (tmp_path / 'oulad_info.json').write_text(json.dumps({
        'source':'oulad','presentation':'2014J','cutoff_weeks':8,
        'historical_training_records':len(hist),'displayed_historical_enrolments':len(current),
    }), encoding='utf-8')
    report = verify_oulad.verify(tmp_path, train=False)
    assert report['data_checks'] == 'passed'
    assert report['replay_records'] == len(current)
    assert 'uncalibrated' in report['risk_scores']
    current.at[0, 'w1'] = 101
    current.to_csv(tmp_path / 'current_students.csv', index=False)
    with pytest.raises(ValueError, match='weekly activity'):
        verify_oulad.verify(tmp_path, train=False)


def test_oulad_predictions_never_blend_demo_homework(monkeypatch):
    historical = service.Bundle(df=pd.DataFrame(), tr=None, class_median=pd.Series(dtype=float), demo=False, source='oulad')
    monkeypatch.setattr(service, 'bundle', lambda: historical)
    import core.homework as homework
    def must_not_run():
        raise AssertionError('Demo homework must not influence OULAD features')
    monkeypatch.setattr(homework, 'live_stats', must_not_run)
    assert service.live() is historical
