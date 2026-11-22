"""Demo data: a simulated past cohort (with known outcomes) and a current cohort.

By default the application uses simulated data. To import actual historical Open University
Learning Analytics Dataset (OULAD) records, run setup-real-oulad.cmd. Some model inputs
are proxies because OULAD does not have a classroom attendance register.

To use real data, put a CSV at data/current_students.csv (and optionally
data/history.csv with a `failed` column). See README.md for the exact columns.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

FEATURES = [
    "attendance",        # % of sessions attended
    "attendance_trend",  # change in attendance, percentage points, second half vs first half
    "test_avg",          # average test score, 0-100
    "hw_completion",     # % of homework handed in
    "hw_avg",            # average homework score, 0-100
    "logins_per_week",   # average LMS logins per week
    "logins_trend",      # % change in LMS logins, last weeks vs first weeks
    "prev_result",       # previous term result, 0-100
]
RANGES = {
    "attendance": (0, 100),
    "attendance_trend": (-100, 100),
    "test_avg": (0, 100),
    "hw_completion": (0, 100),
    "hw_avg": (0, 100),
    "logins_per_week": (0, 200),
    "logins_trend": (-100, 1000),
    "prev_result": (0, 100),
}
WEEKS = 8
HELP_T = 0.50   # probability of failing at or above this -> "Needs help"
WATCH_T = 0.25  # at or above this -> "Watch"; below -> "On track"
GROUPS = ["CS-1", "CS-2", "CS-3"]
WEEK_COLS = [f"w{i}" for i in range(1, WEEKS + 1)]


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def simulate(n: int, seed: int, with_outcome: bool) -> pd.DataFrame:
    """Simulate students. A hidden 'ability' and 'motivation' drive every visible feature,
    so features are correlated with the outcome but never a perfect predictor."""
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)
    motivation = 0.5 * ability + rng.normal(0, 0.85, n)

    # ~12% of students "drop off": activity fades during the term
    dropoff = rng.random(n) < 0.12
    drift = np.where(dropoff, rng.uniform(-0.9, -0.5, n), 0.12 * motivation + rng.normal(0, 0.12, n))

    base = np.clip(6.5 + 2.0 * motivation, 0.8, 16)
    wk = np.arange(WEEKS)
    mult = np.clip(1 + drift[:, None] * (wk[None, :] - (WEEKS - 1) / 2) / ((WEEKS - 1) / 2), 0.05, 3.0)
    logins = rng.poisson(base[:, None] * mult)

    first = logins[:, : WEEKS // 2].mean(axis=1)
    last = logins[:, WEEKS // 2 :].mean(axis=1)
    worse = np.minimum(drift, 0)

    df = pd.DataFrame(
        {
            "attendance": np.clip(82 + 6 * ability + 4 * motivation + 8 * worse + rng.normal(0, 5, n), 25, 100),
            "attendance_trend": np.clip(10 * drift + rng.normal(0, 3, n), -40, 15),
            "test_avg": np.clip(68 + 11 * ability + rng.normal(0, 7, n), 10, 100),
            "hw_completion": np.clip(82 + 8 * ability + 5 * motivation + rng.normal(0, 8, n), 10, 100),
            "hw_avg": np.clip(70 + 9 * ability + rng.normal(0, 8, n), 10, 100),
            "logins_per_week": logins.mean(axis=1),
            "logins_trend": np.clip((last - first) / np.maximum(first, 1) * 100, -100, 300),
            "prev_result": np.clip(70 + 10 * ability + rng.normal(0, 8, n), 30, 100),
        }
    ).round(1)

    # weekly engagement score 0-100 (used for charts)
    weekly = np.clip(logins * 100 / 12, 0, 100).round(0)
    for i, col in enumerate(WEEK_COLS):
        df[col] = weekly[:, i]

    if with_outcome:
        logit = -2.05 - 1.2 * ability - 0.5 * motivation + 1.6 * np.maximum(-drift, 0) + rng.normal(0, 0.35, n)
        df["failed"] = (rng.random(n) < _sigmoid(logit)).astype(int)
    return df


def history(n: int = 1000, seed: int = 7) -> pd.DataFrame:
    """Past cohort with known outcomes. Used to train and test the model."""
    csv = DATA_DIR / "history.csv"
    if csv.exists():
        df = pd.read_csv(csv)
        missing = [c for c in FEATURES + ["failed"] if c not in df.columns]
        if missing:
            raise ValueError(f"data/history.csv is missing columns: {missing}")
        observed = [f"observed_{f}" for f in FEATURES]
        optional = [c for c in ["student_group", "presentation"] + observed if c in df.columns]
        # Observed OULAD grade fields may be missing. The model learns their
        # replacement values from its training fold, never from held-out rows.
        return df[FEATURES + ["failed"] + optional].dropna(subset=FEATURES + ["failed"]).reset_index(drop=True)
    df = simulate(n, seed, with_outcome=True)
    df.insert(0, "student_id", [f"H{i:04d}" for i in range(1, n + 1)])
    return df[["student_id"] + FEATURES + ["failed"]]


def current_cohort(n: int = 180, seed: int = 11) -> pd.DataFrame:
    """Students of the current term (outcome not known yet)."""
    csv = DATA_DIR / "current_students.csv"
    if csv.exists():
        df = pd.read_csv(csv)
        missing = [c for c in ["student_id"] + FEATURES if c not in df.columns]
        if missing:
            raise ValueError(f"data/current_students.csv is missing columns: {missing}")
        if "group" not in df.columns:
            df["group"] = GROUPS[0]
        for col in WEEK_COLS:  # weekly activity is optional: fall back to a flat line
            if col not in df.columns:
                df[col] = np.clip(df["logins_per_week"] * 100 / 12, 0, 100).round(0)
        return df[["student_id", "group"] + FEATURES + WEEK_COLS].dropna().reset_index(drop=True)
    df = simulate(n, seed, with_outcome=False)
    df.insert(0, "group", [GROUPS[i % len(GROUPS)] for i in range(n)])
    df.insert(0, "student_id", [f"S{i:03d}" for i in range(1, n + 1)])
    return df


def validate_features(df: pd.DataFrame) -> list[dict]:
    """Check an uploaded table. Returns a list of problems (empty list = OK).

    Each problem is a dict with a `kind` ("missing", "empty", "nan" or "range") and details.
    `rows` are spreadsheet row numbers (header = row 1), at most 3 per problem.
    """
    missing = [c for c in FEATURES if c not in df.columns]
    if missing:
        return [{"kind": "missing", "cols": ", ".join(missing)}]
    if len(df) == 0:
        return [{"kind": "empty"}]
    problems = []
    for col in FEATURES:
        num = pd.to_numeric(df[col], errors="coerce")
        if num.isna().any():
            rows = ", ".join(str(i) for i in (num[num.isna()].index[:3] + 2))
            problems.append({"kind": "nan", "col": col, "rows": rows})
            continue
        lo, hi = RANGES[col]
        bad = num[(num < lo) | (num > hi)]
        if len(bad):
            rows = ", ".join(str(i) for i in (bad.index[:3] + 2))
            problems.append({"kind": "range", "col": col, "lo": lo, "hi": hi, "rows": rows})
    return problems


def student_ids() -> list[str]:
    """Ids of the current cohort (cheap: no model needed)."""
    return current_cohort()["student_id"].tolist()
