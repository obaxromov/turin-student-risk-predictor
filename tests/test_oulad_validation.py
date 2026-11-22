"""Real-source format, cutoff and evaluation-isolation regression checks."""
import numpy as np
import pandas as pd

from core import data, model
from tests.test_oulad import _fake
from tools import prepare_oulad as po


def test_uci_question_mark_dates_and_scores_are_missing_values(tmp_path):
    _fake(tmp_path)
    for name in ('studentRegistration', 'studentAssessment', 'assessments'):
        path = tmp_path / (name + '.csv')
        frame = pd.read_csv(path)
        if name == 'studentAssessment':
            frame.loc[0, 'score'] = np.nan
        frame.to_csv(path, index=False, na_rep='?')
    hist, current = po.build(tmp_path)
    assert len(hist) == 300 and len(current) == 150
    assert hist.student_group.str.fullmatch(r'[0-9a-f]{24}').all()
    assert not current[data.FEATURES].isna().any().any()
    assert 'id_student' not in hist and 'id_student' not in current


def test_assessments_and_activity_at_day_56_do_not_change_features(tmp_path):
    _fake(tmp_path)
    before, replay_before = po.build(tmp_path)
    activity = pd.read_csv(tmp_path / 'studentVle.csv')
    extra = activity.iloc[:50].copy()
    extra['date'] = 56
    extra['sum_click'] = 999999
    pd.concat([activity, extra], ignore_index=True).to_csv(tmp_path / 'studentVle.csv', index=False)
    assessments = pd.read_csv(tmp_path / 'studentAssessment.csv')
    extra = assessments.iloc[:50].copy()
    extra['date_submitted'] = 56
    extra['score'] = 0
    pd.concat([assessments, extra], ignore_index=True).to_csv(tmp_path / 'studentAssessment.csv', index=False)
    after, replay_after = po.build(tmp_path)
    pd.testing.assert_frame_equal(before, after)
    pd.testing.assert_frame_equal(replay_before, replay_after)


def test_older_replay_never_trains_on_newer_presentations(tmp_path):
    _fake(tmp_path, n_per=220)
    hist, replay = po.build(tmp_path, current='2014B')
    assert set(hist.presentation) == {'2013J'}
    assert set(hist.attrs['evaluation'].presentation) == {'2013J', '2014B'}
    assert len(replay) == 220


def test_repeated_student_enrolments_share_a_split_and_imputation_is_training_only():
    hist = data.simulate(500, seed=73, with_outcome=True)
    hist['student_group'] = [f'group-{i // 2}' for i in range(len(hist))]
    for feat in data.FEATURES:
        hist[f'observed_{feat}'] = hist[feat]
    train, test = model.split_history(hist)
    assert set(hist.iloc[train].student_group).isdisjoint(hist.iloc[test].student_group)
    hist.loc[train, 'observed_test_avg'] = np.linspace(10, 50, len(train))
    hist.loc[test, 'observed_test_avg'] = 100
    hist.loc[train[::3], 'observed_hw_avg'] = np.nan
    tr = model.train(hist)
    assert tr.evaluation['student_overlap'] == 0
    assert np.isclose(tr.medians.test_avg, 30)
    assert not np.isclose(tr.medians.test_avg, hist.observed_test_avg.median())
    assert all(np.isfinite(value) for value in tr.medians)


def test_replay_values_cannot_change_older_imputation(tmp_path):
    _fake(tmp_path)
    before, _ = po.build(tmp_path)
    sa = pd.read_csv(tmp_path / 'studentAssessment.csv')
    asm = pd.read_csv(tmp_path / 'assessments.csv')
    replay_assessments = set(asm.loc[asm.code_presentation.eq('2014J'), 'id_assessment'])
    sa.loc[sa.id_assessment.isin(replay_assessments), 'score'] = 0
    sa.to_csv(tmp_path / 'studentAssessment.csv', index=False)
    after, _ = po.build(tmp_path)
    pd.testing.assert_frame_equal(before, after)
