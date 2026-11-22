"""Reproduce internal and later-presentation OULAD validation without future-data fitting.

    python tools/evaluate_oulad.py

The later presentation is tested twice: all eligible enrolments, then only
students absent from every older training presentation. No threshold is tuned.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
    precision_score, recall_score, roc_auc_score,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import data, model
from tools.verify_oulad import verify


def metrics(y, scores) -> dict:
    y = np.asarray(y, dtype=int)
    scores = np.asarray(scores, dtype=float)
    result = {
        'records': len(y), 'fail_or_withdrawn_records': int(y.sum()),
        'fail_or_withdrawn_fraction': float(y.mean()),
        'roc_auc': float(roc_auc_score(y, scores)),
        'average_precision': float(average_precision_score(y, scores)),
        'baseline_accuracy_everyone_passes': float(1 - y.mean()),
        'baseline_accuracy_majority_class': float(max(y.mean(), 1 - y.mean())),
        'brier_score_uncalibrated': float(brier_score_loss(y, scores)),
    }
    for threshold, label in ((0.25, '25_percent'), (0.50, '50_percent')):
        pred = (scores >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        result['threshold_' + label] = {
            'accuracy': float(accuracy_score(y, pred)),
            'precision': float(precision_score(y, pred, zero_division=0)),
            'recall': float(recall_score(y, pred, zero_division=0)),
            'flagged_fraction': float(pred.mean()),
            'confusion': dict(zip(('tn', 'fp', 'fn', 'tp'), map(int, (tn, fp, fn, tp)))),
        }
    result['tiers'] = []
    for name, mask in (('help', scores >= .5), ('watch', (scores >= .25) & (scores < .5)), ('ok', scores < .25)):
        result['tiers'].append({'tier': name, 'records': int(mask.sum()),
                                'outcome_rate': float(y[mask].mean()) if mask.any() else None})
    return result


def clustered_intervals(frame: pd.DataFrame, scores: np.ndarray, repeats: int = 1000) -> dict:
    """Resample students, keeping their simultaneous enrolments together."""
    y = frame.failed.to_numpy(dtype=int)
    groups, inverse = np.unique(frame.student_group, return_inverse=True)
    rng = np.random.default_rng(20261106)
    aucs, accuracies = [], []
    for _ in range(repeats):
        counts = np.bincount(rng.integers(0, len(groups), len(groups)), minlength=len(groups))
        weights = counts[inverse]
        if not all(weights[y == c].sum() for c in (0, 1)):
            continue
        aucs.append(roc_auc_score(y, scores, sample_weight=weights))
        accuracies.append(accuracy_score(y, scores >= .5, sample_weight=weights))
    return {'method': '95% percentile bootstrap by student; fixed fitted model',
            'seed': 20261106, 'requested_resamples': repeats, 'valid_resamples': len(aucs),
            'roc_auc': np.quantile(aucs, [.025, .975]).tolist(),
            'accuracy_at_50_percent': np.quantile(accuracies, [.025, .975]).tolist()}


def source_audit(raw: Path, cutoff: int = 56) -> dict:
    files = []
    for path in sorted(raw.glob('*.csv')):
        digest = hashlib.sha256()
        newlines, last = 0, b''
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
                newlines += block.count(b'\n')
                last = block[-1:]
        rows = newlines - 1 + int(bool(last and last != b'\n'))
        files.append({'name': path.name, 'bytes': path.stat().st_size,
                      'rows': rows, 'sha256': digest.hexdigest()})
    info = pd.read_csv(raw / 'studentInfo.csv', na_values=['?'])
    reg = pd.read_csv(raw / 'studentRegistration.csv', na_values=['?'])
    keys = ['code_module', 'code_presentation', 'id_student']
    if info.duplicated(keys).any() or reg.duplicated(keys).any():
        raise ValueError('Duplicate source enrolment keys')
    joined = info.merge(reg, on=keys, validate='one_to_one')
    left = joined.date_unregistration.lt(cutoff)
    late = joined.date_registration.ge(cutoff)
    return {
        'download_url': 'https://archive.ics.uci.edu/static/public/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset.zip',
        'dataset_doi': '10.24432/C5KK69', 'license': 'CC BY 4.0',
        'attribution': 'Kuzilek, Hlosta and Zdrahal; Open University Learning Analytics Dataset',
        'source_enrolments': len(info), 'source_unique_students': int(info.id_student.nunique()),
        'excluded_withdrawal_before_day_56': int(left.sum()),
        'excluded_late_registration_not_already_withdrawn': int((late & ~left).sum()),
        'eligible_records': int((~left & ~late).sum()),
        'files': files,
    }


def evaluate(folder: Path | None = None, bootstrap: int = 1000) -> dict:
    folder = Path(folder or data.DATA_DIR)
    report = verify(folder)
    meta = json.loads((folder / 'oulad_info.json').read_text())
    frame = pd.read_csv(folder / 'oulad_evaluation.csv')
    required = data.FEATURES + ['student_group', 'presentation', 'group', 'failed']
    if not set(required).issubset(frame.columns):
        raise ValueError('Incomplete independent evaluation inputs')
    if set(frame.failed.unique()) != {0, 1} or frame[required[-4:]].isna().any().any():
        raise ValueError('Invalid independent evaluation identifiers or outcomes')
    if frame.duplicated(['student_group', 'presentation', 'group']).any():
        raise ValueError('Repeated evaluation enrolment')
    for feat in data.FEATURES:
        if not frame[feat].dropna().between(*data.RANGES[feat]).all():
            raise ValueError('Out-of-range evaluation input: ' + feat)
    replay = meta['presentation']
    past = frame.loc[frame.presentation.lt(replay)].copy()
    future = frame.loc[frame.presentation.eq(replay)].copy()
    if len(past) != report['historical_records'] or future.empty or frame.presentation.gt(replay).any():
        raise ValueError('Temporal cohorts do not agree with the import metadata')
    medians = model.feature_medians(past[data.FEATURES])
    forest = model.new_forest().fit(past[data.FEATURES].fillna(medians), past.failed)
    scores = forest.predict_proba(future[data.FEATURES].fillna(medians))[:, 1]
    seen = future.student_group.isin(set(past.student_group)).to_numpy()
    unseen = future.loc[~seen].copy()
    if unseen.failed.nunique() != 2:
        raise ValueError('Need both outcomes among previously unseen students')
    report['temporal_validation'] = {
        'method': 'fit all older presentations, evaluate once on the later historical presentation',
        'training_presentations': sorted(past.presentation.unique().tolist()),
        'test_presentation': replay, 'training_records': len(past),
        'training_unique_students': int(past.student_group.nunique()),
        'imputation': 'older-training medians only; no later-presentation fitting',
        'thresholds': '25% and 50% fixed before evaluation; no tuning on test results',
        'all_later_enrolments': metrics(future.failed, scores),
        'later_enrolments_with_student_seen_in_training': int(seen.sum()),
        'unseen_students_only': metrics(unseen.failed, scores[~seen]),
        'student_overlap_in_unseen_test': len(set(unseen.student_group) & set(past.student_group)),
        'unseen_test_unique_students': int(unseen.student_group.nunique()),
        'unseen_students_95_percent_intervals': clustered_intervals(unseen, scores[~seen], bootstrap),
        'imputation_medians': medians.to_dict(),
        'missing_fraction_before_imputation_training': past[data.FEATURES].isna().mean().to_dict(),
        'missing_fraction_before_imputation_later': future[data.FEATURES].isna().mean().to_dict(),
        'per_module_all_later': {
            module: metrics(future.loc[future.group.eq(module), 'failed'], scores[future.group.eq(module).to_numpy()])
            for module in sorted(future.group.unique())
        },
    }
    predictions = future[['student_group', 'presentation', 'group', 'failed']].copy()
    predictions['score'] = scores
    predictions['student_seen_in_training'] = seen
    predictions.to_csv(folder / 'oulad_temporal_predictions.csv', index=False)
    raw = folder / 'oulad' / 'raw'
    if raw.exists():
        report['source_audit'] = source_audit(raw, int(meta['cutoff_weeks']) * 7)
        if report['source_audit']['eligible_records'] != len(frame):
            raise ValueError('Eligible source rows do not match evaluation rows')
    report['runtime'] = {'python': platform.python_version(), 'platform': platform.platform(),
                         'packages': {name: importlib.metadata.version(name)
                                      for name in ('numpy', 'pandas', 'scipy', 'scikit-learn', 'joblib')}}
    report['model'] = {'algorithm': 'RandomForestClassifier', 'parameters': forest.get_params(),
                       'features': data.FEATURES, 'cutoff': 'days 0 through 55 inclusive',
                       'outcome': 'Fail/Withdrawn=1; Pass/Distinction=0',
                       'display_sample': report['replay_records'],
                       'evaluation_uses_full_later_cohort': True}
    report['limitations'] = [
        'Historical UK distance-learning data; accuracy at Turin remains unknown.',
        'Assessment score timestamps are unavailable: submission date is the availability proxy.',
        'Many modules have no early CMA; missing grades use training medians and do not prove student inactivity.',
        'Attendance/logins are VLE activity proxies; previous result is an early assessment.',
        'Model scores are uncalibrated and thresholds have not been optimized for an intervention policy.',
        'Bootstrap intervals condition on one fitted model and do not measure institution-transfer uncertainty.',
    ]
    path = folder / 'oulad_validation.json'
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=data.DATA_DIR)
    parser.add_argument('--bootstrap', type=int, default=1000)
    args = parser.parse_args()
    report = evaluate(args.data, args.bootstrap)
    print(json.dumps(report, indent=2, allow_nan=False))
    print('\nSaved data/oulad_validation.json; historical validation does not establish Turin accuracy.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
