"""Turn the real Open University (OULAD) CSV files into the two files the app reads.

    python tools/prepare_oulad.py PATH_TO_OULAD_FOLDER

Reads studentInfo, studentVle, studentAssessment, assessments (and studentRegistration if present).
Writes data/history.csv (older presentations, with the outcome) and data/current_students.csv (the newest
presentation, outcome ignored). Restart the app afterwards: the "Demo data" badge disappears.

OULAD has no attendance register, so some features are honest PROXIES (also stated on the Model page notes):
  attendance        % of the first N weeks in which the student clicked anything in the LMS
  attendance_trend  that percentage in the second half minus the first half (points)
  logins_per_week   average number of distinct days per week with LMS activity
  logins_trend      % change in active days, second half vs first half
  hw_completion     % of assignments (TMA) due by the cut-off that the student handed in by then
  hw_avg            average score of handed-in assignments (TMA)
  test_avg          average score of computer-marked quizzes (CMA)
  prev_result       score of the student's first handed-in assessment (OULAD has no earlier-term grades)
Only data from before the cut-off week is used for features, so the model cannot peek at the future.
Students who left before the cut-off are dropped (nobody can warn them). failed = Fail or Withdrawn.
Demographic columns (gender, age, region, disability, IMD) are never read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["code_module", "code_presentation", "id_student"]
FEATURES = ["attendance", "attendance_trend", "test_avg", "hw_completion", "hw_avg",
            "logins_per_week", "logins_trend", "prev_result"]
RAW_FEATURES = [f"observed_{c}" for c in FEATURES]


def _read(folder: Path, name: str, required: bool = True, **kw) -> pd.DataFrame | None:
    p = folder / f"{name}.csv"
    if not p.exists():
        if required:
            sys.exit(f"Missing file: {p}")
        return None
    return pd.read_csv(p, na_values=["?"], **kw)


def build(folder: Path, cutoff_weeks: int = 8, current: str | None = None, sample: int = 400,
          seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = cutoff_weeks * 7
    info = _read(folder, "studentInfo", usecols=KEYS + ["final_result"])
    sa = _read(folder, "studentAssessment")
    asm = _read(folder, "assessments")
    reg = _read(folder, "studentRegistration", required=False)

    info = info.drop_duplicates(KEYS)
    if reg is not None:  # drop students who unregistered before the cut-off
        left = reg[reg["date_unregistration"].notna() & (reg["date_unregistration"] < cutoff)]
        info = info.merge(left[KEYS].assign(_left=1), on=KEYS, how="left")
        info = info[info["_left"].isna()].drop(columns="_left")
        if "date_registration" in reg:
            late = reg.loc[reg["date_registration"].ge(cutoff), KEYS]
            info = info.merge(late.assign(_late=1), on=KEYS, how="left")
            info = info[info["_late"].isna()].drop(columns="_late")

    presentations = sorted(info["code_presentation"].unique())
    cur_name = current or presentations[-1]
    if cur_name not in presentations:
        sys.exit(f"Presentation {cur_name} not found. Available: {presentations}")
    # An explicitly selected older replay must not train on later presentations.
    info = info[info["code_presentation"].le(cur_name)].copy()

    # ----- LMS activity in the first `cutoff` days -----
    # studentVle.csv is 400+ MB uncompressed. Process it in chunks instead of
    # allocating a second full copy of the ~10.6 million-row table.
    vle_file = folder / "studentVle.csv"
    if not vle_file.exists():
        sys.exit(f"Missing file: {vle_file}")
    parts = []
    for chunk in pd.read_csv(vle_file, usecols=KEYS + ["date", "sum_click"], chunksize=200_000):
        v = chunk.loc[chunk["date"].ge(0) & chunk["date"].lt(cutoff)].copy()
        if v.empty:
            continue
        v["week"] = (v["date"] // 7).astype(int)
        # Each row records one site/student/day; aggregate days separately
        # because a student may visit several sites on the same date.
        daily = v.groupby(KEYS + ["week", "date"], sort=False)["sum_click"].sum().reset_index()
        parts.append(daily)
    if parts:
        v = pd.concat(parts, ignore_index=True)
        # A student/date can cross chunk boundaries, so combine those first.
        daily = v.groupby(KEYS + ["week", "date"], sort=False)["sum_click"].sum().reset_index()
        per_week = daily.groupby(KEYS + ["week"]).agg(clicks=("sum_click", "sum"), days=("date", "nunique")).reset_index()
    else:
        per_week = pd.DataFrame(columns=KEYS + ["week", "clicks", "days"])
    del parts

    clicks = per_week.pivot_table(index=KEYS, columns="week", values="clicks", fill_value=0).reindex(columns=range(cutoff_weeks), fill_value=0)
    days = per_week.pivot_table(index=KEYS, columns="week", values="days", fill_value=0).reindex(columns=range(cutoff_weeks), fill_value=0)
    base = info.set_index(KEYS)
    clicks = clicks.reindex(base.index, fill_value=0)
    days = days.reindex(base.index, fill_value=0)

    half = cutoff_weeks // 2
    active = (clicks > 0).astype(float)
    out = pd.DataFrame(index=base.index)
    out["attendance"] = active.mean(axis=1) * 100
    out["attendance_trend"] = (active.iloc[:, half:].mean(axis=1) - active.iloc[:, :half].mean(axis=1)) * 100
    out["logins_per_week"] = days.mean(axis=1)
    d1, d2 = days.iloc[:, :half].sum(axis=1), days.iloc[:, half:].sum(axis=1)
    trend = np.where(d1 > 0, (d2 / d1.replace(0, np.nan) - 1) * 100, np.where(d2 > 0, 100.0, 0.0))
    out["logins_trend"] = np.clip(trend, -100, 1000)

    # weekly activity 0-100 for the charts (95th percentile of weekly clicks = 100)
    past_clicks = clicks.loc[clicks.index.get_level_values("code_presentation") < cur_name].values
    cap = max(float(np.percentile(past_clicks[past_clicks > 0], 95)) if (past_clicks > 0).any() else 1.0, 1.0)
    weekly = np.clip(clicks / cap * 100, 0, 100).round(0)
    weekly.columns = [f"w{i + 1}" for i in range(cutoff_weeks)]

    # ----- assessments handed in by the cut-off -----
    a = sa.merge(asm[["id_assessment", "code_module", "code_presentation", "assessment_type", "date"]]
                 .rename(columns={"date": "due"}), on="id_assessment")
    # Day cutoff is the start of week 9; never consume assessment scores
    # submitted on day 56 when building an eight-week prediction.
    a = a[a["date_submitted"] < cutoff]
    due = asm[asm["date"].notna() & (asm["date"] < cutoff)]
    n_due = due[due["assessment_type"] == "TMA"].groupby(["code_module", "code_presentation"]).size().rename("n_due")
    # Completion must only consider work *due* at the week-8 cutoff.
    tma = a[(a["assessment_type"] == "TMA") & a["due"].notna() & (a["due"] < cutoff)].groupby(KEYS).agg(n_sub=("id_assessment", "nunique"), hw_avg=("score", "mean"))
    cma = a[a["assessment_type"] == "CMA"].groupby(KEYS).agg(test_avg=("score", "mean"))
    first = a.sort_values("date_submitted").groupby(KEYS).agg(prev_result=("score", "first"))

    out = out.join(tma).join(cma).join(first)
    out = out.join(n_due, on=["code_module", "code_presentation"])
    out["hw_completion"] = (out["n_sub"].fillna(0) / out["n_due"]).clip(0, 1) * 100
    out.loc[out["n_due"].isna(), "hw_completion"] = np.nan

    # Preserve observed inputs separately: evaluation learns imputation only
    # from its training fold. Filled display columns never drive that evaluation.
    for c in FEATURES:
        out[f"observed_{c}"] = out[c]
    historical_mask = out.index.get_level_values("code_presentation") < cur_name
    miss = {}
    for c in ["test_avg", "hw_avg", "prev_result", "hw_completion"]:
        miss[c] = float(out[c].isna().mean())
        median = out.loc[historical_mask, c].median()
        out[c] = out[c].fillna(float(median) if pd.notna(median) else 50.0)
    out = out.join(weekly).join(base["final_result"])
    out["failed"] = out["final_result"].isin(["Fail", "Withdrawn"]).astype(int)
    out = out.reset_index()
    out["group"] = out["code_module"]
    # Stable pseudonyms retain repeated-student grouping without exporting the
    # original OULAD student identifier to the application or evaluation files.
    out["student_group"] = out["id_student"].map(
        lambda value: hashlib.sha256(f"OULAD-student:{value}".encode()).hexdigest()[:24]
    )
    out["presentation"] = out["code_presentation"]
    out[FEATURES] = out[FEATURES].astype(float).round(1)
    out[RAW_FEATURES] = out[RAW_FEATURES].astype(float).round(1)

    pres = sorted(out["code_presentation"].unique())
    hist = out[out["code_presentation"] < cur_name].copy()
    cur = out[out["code_presentation"] == cur_name].copy()
    if len(hist) < 200:
        sys.exit("Fewer than 200 earlier students: not enough to train on.")
    if sample and len(cur) > sample:
        cur = cur.sample(sample, random_state=seed)

    hist = hist.sample(frac=1, random_state=seed).reset_index(drop=True)
    hist.insert(0, "student_id", [f"H{i:05d}" for i in range(1, len(hist) + 1)])
    cur = cur.sort_values(KEYS).reset_index(drop=True)
    cur.insert(0, "student_id", [f"S{i:03d}" for i in range(1, len(cur) + 1)])  # pseudonyms: real id_student never leaves this script
    print(f"history: {len(hist)} students from {pres[:-1] if current is None else [p for p in pres if p != cur_name]}, "
          f"{hist['failed'].mean():.0%} failed or withdrew")
    print(f"current: {len(cur)} students from {cur_name}")
    print("share of values that were missing and filled with the median:", {k: f"{v:.0%}" for k, v in miss.items()})
    history = hist[["student_id"] + FEATURES + ["failed", "student_group", "presentation"] + RAW_FEATURES].copy()
    current_frame = cur[["student_id", "group"] + FEATURES + list(weekly.columns)].copy()
    evaluation = out[["student_group", "presentation", "group", "failed"] + RAW_FEATURES].copy()
    evaluation = evaluation.rename(columns=dict(zip(RAW_FEATURES, FEATURES)))
    history.attrs["evaluation"] = evaluation
    history.attrs["missing_fraction"] = miss
    return history, current_frame


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="folder with the OULAD csv files")
    ap.add_argument("--cutoff-weeks", type=int, default=8)
    ap.add_argument("--current", help="presentation to treat as the current term, e.g. 2014J (default: newest)")
    ap.add_argument("--sample", type=int, default=400, help="max students shown in the app (0 = all)")
    ap.add_argument("--out", type=Path, default=ROOT / "data")
    a = ap.parse_args()
    hist, cur = build(a.folder, a.cutoff_weeks, a.current, a.sample)
    a.out.mkdir(parents=True, exist_ok=True)
    hist.to_csv(a.out / "history.csv", index=False)
    cur.to_csv(a.out / "current_students.csv", index=False)
    hist.attrs["evaluation"].to_csv(a.out / "oulad_evaluation.csv", index=False)
    # Keep source provenance explicit. Both CSVs still have the generic format
    # so other users can provide their own real data without being mislabeled.
    presentation = a.current or sorted(_read(a.folder, "studentInfo", usecols=["code_presentation"])["code_presentation"].unique())[-1]
    metadata = {
        "source": "oulad", "original_source": "https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset",
        "license": "CC BY 4.0", "presentation": presentation,
        "cutoff_weeks": a.cutoff_weeks, "historical_training_records": len(hist),
        "displayed_historical_enrolments": len(cur),
        "converter_version": 2,
        "missing_value_policy": "Observed features retained; model imputation fitted on training fold only. Display values use older-cohort medians.",
        "missing_fraction_before_imputation": hist.attrs["missing_fraction"],
        "warning": "All OULAD records are historical; the current presentation is a week-8 replay, not a live class."
    }
    (a.out / "oulad_info.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"written: {a.out / 'history.csv'}, {a.out / 'current_students.csv'}")
    print("These are REAL HISTORICAL OULAD records, not live students from your university.")


if __name__ == "__main__":
    main()
