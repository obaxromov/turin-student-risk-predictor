"""Validate a completed local OULAD import and report held-out ML metrics.

Run after setup-real-oulad.cmd / tools/prepare_oulad.py:
  python tools/verify_oulad.py

This only verifies a historical research replay; it cannot establish accuracy
on students at Turin University. Nothing is uploaded to an external service.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import data  # noqa: E402
from core.data import FEATURES, RANGES, WEEK_COLS  # noqa: E402


def verify(folder: Path | None = None, train: bool = True) -> dict:
    """Raise ValueError when the import isn't complete, return a serializable report otherwise."""
    folder = Path(folder or data.DATA_DIR)
    meta_file = folder / 'oulad_info.json'
    history_file, current_file = folder / 'history.csv', folder / 'current_students.csv'
    if not all(p.is_file() for p in (meta_file, history_file, current_file)):
        raise ValueError('OULAD has not been imported. Run setup-real-oulad.cmd first.')
    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except (ValueError, OSError) as exc:
        raise ValueError('Cannot read OULAD source metadata') from exc
    if meta.get('source') != 'oulad':
        raise ValueError('Dataset metadata does not identify OULAD')
    hist = pd.read_csv(history_file)
    current = pd.read_csv(current_file)
    for label, frame, cols in (
        ('history', hist, FEATURES + ['student_id', 'failed']),
        ('current', current, FEATURES + ['student_id', 'group'] + WEEK_COLS),
    ):
        missing = set(cols) - set(frame.columns)
        if missing:
            raise ValueError(f'{label} missing columns: {sorted(missing)}')
        if frame.empty:
            raise ValueError(f'{label} is empty')
        if frame.student_id.isna().any() or frame.student_id.duplicated().any():
            raise ValueError(f'{label} student identifiers are empty or repeated')
        for feat in FEATURES:
            vals = pd.to_numeric(frame[feat], errors='coerce')
            lo, hi = RANGES[feat]
            if vals.isna().any() or not vals.between(lo, hi).all():
                raise ValueError(f'{label}.{feat} contains missing/out-of-range values')
    labels = pd.to_numeric(hist['failed'], errors='coerce')
    if len(hist) < 200 or set(labels.unique()) != {0, 1}:
        raise ValueError('Historical training records need >=200 rows and both outcome classes')
    for col in WEEK_COLS:
        vals = pd.to_numeric(current[col], errors='coerce')
        if vals.isna().any() or not vals.between(0, 100).all():
            raise ValueError(f'current.{col} contains invalid weekly activity')
    if not current['student_id'].str.startswith('S').all():
        raise ValueError('Current students have unexpected identifiers')
    if any(col in current.columns for col in ('id_student', 'final_result', 'failed')):
        raise ValueError('Current cohort contains historical IDs/outcomes that must not be shown')
    if len(hist) != int(meta.get('historical_training_records', -1)) or len(current) != int(meta.get('displayed_historical_enrolments', -1)):
        raise ValueError('Metadata row counts do not match the imported data')
    if meta.get('converter_version', 1) >= 2:
        observed = [f'observed_{f}' for f in FEATURES]
        if not set(observed + ['student_group', 'presentation']).issubset(hist.columns):
            raise ValueError('Observed training values or student grouping are missing')
        if hist.student_group.isna().any() or not hist.student_group.str.fullmatch(r'[0-9a-f]{24}').all():
            raise ValueError('Invalid pseudonymous student grouping')
        if not hist.presentation.lt(meta['presentation']).all():
            raise ValueError('Training includes the replay presentation or a later one')
        for feat, col in zip(FEATURES, observed):
            vals = pd.to_numeric(hist[col], errors='raise').dropna()
            if not vals.between(*RANGES[feat]).all():
                raise ValueError(f'history.{col} contains out-of-range observations')
        if not (folder / 'oulad_evaluation.csv').is_file():
            raise ValueError('Full temporal evaluation dataset is missing')

    report = {
        'source': 'historical OULAD (NOT live Turin data)',
        'verified_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'presentation_replay': meta.get('presentation'),
        'cutoff_weeks': meta.get('cutoff_weeks'),
        'historical_records': len(hist),
        'replay_records': len(current),
        'historical_fail_or_withdrawn_percent': round(float(labels.mean() * 100), 1),
        'data_checks': 'passed',
        'external_validity': 'unknown; do not claim this model is accurate for Turin students',
        'risk_scores': 'uncalibrated; use for triage, not as verified probabilities',
        'evaluation_method': 'student-grouped 30% holdout within older OULAD presentations; training-fold imputation only' if 'student_group' in hist else 'stratified 30% holdout within older OULAD presentations, not prospective validation',
        'feature_limitation': 'attendance/logins are LMS activity proxies; previous result is an early assessment',
        'assignment_limitation': 'demo assignments are separate from OULAD and do not change historical risk estimates',
    }
    if train:
        # This is a quality report on the imported CSVs. Do not substitute simulated metrics.
        from core import model
        tr = model.train(hist)
        if not all(math.isfinite(float(v)) for v in tr.metrics.values() if isinstance(v, (int, float))):
            raise ValueError('Model returned non-finite metrics')
        report['held_out'] = {
            'train_records': tr.n_train,
            'test_records': tr.n_test,
            'roc_auc': round(tr.metrics['roc_auc'], 4),
            'baseline_accuracy': round(tr.metrics['baseline_accuracy'], 4),
            'accuracy_at_50_percent_threshold': round(tr.metrics['accuracy'], 4),
            'precision_flagged_at_25_percent': round(tr.metrics['precision_flag'], 4),
            'recall_flagged_at_25_percent': round(tr.metrics['recall_flag'], 4),
            'tier_outcomes': tr.tier_table.to_dict('records'),
            'split': tr.evaluation,
            'confusion_flagged_at_25_percent': tr.metrics['confusion_flag'],
            'precision_at_50_percent_threshold': round(tr.metrics['precision_help'], 4),
            'recall_at_50_percent_threshold': round(tr.metrics['recall_help'], 4),
        }
    return report


def main() -> int:
    try:
        report = verify()
    except (ValueError, OSError, KeyError) as exc:
        print(f'NOT READY: {exc}', file=sys.stderr)
        return 2
    path = data.DATA_DIR / 'oulad_validation.json'
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f'\nSaved local validation report: {path}')
    print('CAUTION: A historical hold-out does not prove accuracy at Turin University.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
