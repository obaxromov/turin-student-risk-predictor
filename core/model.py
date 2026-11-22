"""Model: Random Forest that estimates the probability that a student fails.

Honest-evaluation rules used here:
  * the model is trained on a PAST cohort and evaluated on a held-out part of it;
  * the current cohort is only ever predicted, never used for training;
  * we compare against a trivial "everyone passes" baseline, because with ~20% failures
    plain accuracy hides how many at-risk students are missed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from core.data import FEATURES, HELP_T, WATCH_T  # noqa: F401  (re-exported)


@dataclass
class Trained:
    model: RandomForestClassifier
    medians: pd.Series
    metrics: dict
    importance: pd.DataFrame
    tier_table: pd.DataFrame
    n_train: int
    n_test: int
    base_rate: float
    evaluation: dict = field(default_factory=dict)


def observed_features(hist: pd.DataFrame) -> pd.DataFrame:
    """Use pre-imputation observations when supplied by the OULAD converter."""
    cols = [f"observed_{f}" for f in FEATURES]
    if all(c in hist.columns for c in cols):
        return hist[cols].set_axis(FEATURES, axis=1).astype(float)
    return hist[FEATURES].astype(float)


def split_history(hist: pd.DataFrame, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Keep every enrolment of one OULAD student on the same side."""
    indices = np.arange(len(hist))
    if "student_group" in hist.columns:
        return next(GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed)
                    .split(indices, hist["failed"], hist["student_group"]))
    return train_test_split(indices, test_size=0.3, stratify=hist["failed"], random_state=seed)


def feature_medians(X: pd.DataFrame) -> pd.Series:
    """Learn replacements on training rows; use neutral 50 if a grade is wholly absent."""
    defaults = pd.Series(0.0, index=FEATURES)
    defaults[["test_avg", "hw_completion", "hw_avg", "prev_result"]] = 50.0
    return X.median().fillna(defaults)


def new_forest(seed: int = 42) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=300, min_samples_leaf=8, max_features="sqrt", random_state=seed, n_jobs=1
    )


def tier_of(p: float) -> str:
    if p >= HELP_T:
        return "help"
    if p >= WATCH_T:
        return "watch"
    return "ok"


def tiers(p: np.ndarray) -> list[str]:
    return [tier_of(x) for x in p]


def train(hist: pd.DataFrame, seed: int = 42) -> Trained:
    X, y = observed_features(hist), hist["failed"].astype(int)
    train_idx, test_idx = split_history(hist, seed)
    Xtr, Xte, ytr, yte = X.iloc[train_idx], X.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]
    medians = feature_medians(Xtr)
    Xtr, Xte = Xtr.fillna(medians), Xte.fillna(medians)

    model = new_forest(seed).fit(Xtr, ytr)

    p = model.predict_proba(Xte)[:, 1]
    help_pred = (p >= HELP_T).astype(int)
    flag_pred = (p >= WATCH_T).astype(int)
    tn, fp, fn, tp = confusion_matrix(yte, flag_pred, labels=[0, 1]).ravel()

    metrics = {
        "roc_auc": float(roc_auc_score(yte, p)),
        "accuracy": float(accuracy_score(yte, help_pred)),
        "baseline_accuracy": float(1 - yte.mean()),  # "everyone passes"
        "precision_help": float(precision_score(yte, help_pred, zero_division=0)),
        "recall_help": float(recall_score(yte, help_pred, zero_division=0)),
        "precision_flag": float(precision_score(yte, flag_pred, zero_division=0)),
        "recall_flag": float(recall_score(yte, flag_pred, zero_division=0)),
        "confusion_flag": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }

    perm = permutation_importance(model, Xte, yte, n_repeats=8, random_state=seed, scoring="roc_auc")
    importance = (
        pd.DataFrame({"feature": FEATURES, "importance": perm.importances_mean})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    tt = pd.DataFrame({"tier": tiers(p), "failed": yte.values})
    tier_table = (
        tt.groupby("tier")
        .agg(students=("failed", "size"), fail_rate=("failed", "mean"))
        .reindex(["help", "watch", "ok"])
        .fillna(0)
        .reset_index()
    )

    return Trained(
        model=model,
        medians=medians,
        metrics=metrics,
        importance=importance,
        tier_table=tier_table,
        n_train=len(Xtr),
        n_test=len(Xte),
        base_rate=float(y.mean()),
        evaluation={
            "method": "student-grouped 30% holdout" if "student_group" in hist else "stratified 30% holdout",
            "imputation": "training-fold medians only",
            "student_overlap": len(set(hist.iloc[train_idx]["student_group"]) & set(hist.iloc[test_idx]["student_group"])) if "student_group" in hist else None,
            "seed": seed,
        },
    )


def predict(tr: Trained, X: pd.DataFrame) -> pd.DataFrame:
    """Return risk probability, tier and 'model agreement' for each row of X."""
    X = X[FEATURES].astype(float)
    p = tr.model.predict_proba(X)[:, 1]
    per_tree = np.stack([est.predict_proba(X.values)[:, 1] for est in tr.model.estimators_])
    spread = per_tree.std(axis=0)
    agreement = np.where(spread < 0.20, "high", np.where(spread < 0.30, "medium", "low"))
    return pd.DataFrame({"risk": p, "tier": tiers(p), "agreement": agreement}, index=X.index)


def contributions(tr: Trained, X: pd.DataFrame) -> pd.DataFrame:
    """Plain-language explainability: how much does each feature push this student's risk up?

    For each feature we replace the student's value with the typical (median) value and see how
    much the predicted risk drops. A positive number = this feature raises the student's risk.
    """
    X = X[FEATURES].astype(float)
    base = tr.model.predict_proba(X)[:, 1]
    out = {}
    for f in FEATURES:
        Xo = X.copy()
        Xo[f] = tr.medians[f]
        out[f] = base - tr.model.predict_proba(Xo)[:, 1]
    return pd.DataFrame(out, index=X.index)


def top_reasons(contrib_row: pd.Series, k: int = 3, min_effect: float = 0.01) -> list[tuple[str, float]]:
    s = contrib_row[contrib_row > min_effect].sort_values(ascending=False).head(k)
    return list(s.items())
