"""Loads data, trains the model once and scores the current cohort.

Speed: training takes a few seconds, so the result is saved to `data/cache/` and later starts just
load that file. A background thread warms it up when the server starts, so the login page never waits.
sklearn is imported only when the bundle is built or loaded (never on the login page).
"""
from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from core import data
from core.data import FEATURES, WEEK_COLS

CACHE_DIR = Path(os.environ.get("APP_CACHE", data.DATA_DIR / "cache"))
_SOURCES = [data.ROOT / "core" / "data.py", data.ROOT / "core" / "model.py", data.ROOT / "core" / "service.py"]
_DATA_FILES = [data.DATA_DIR / "history.csv", data.DATA_DIR / "current_students.csv", data.DATA_DIR / "oulad_info.json"]

_lock = threading.Lock()
_bundle: "Bundle | None" = None


@dataclass
class Bundle:
    df: pd.DataFrame           # current cohort + risk, tier, agreement, reasons
    tr: "object"               # core.model.Trained
    class_median: pd.Series    # median of every feature and weekly column
    demo: bool                 # True while running on simulated data
    source: str = "demo"      # demo / oulad / csv, not a claim of live university records


def _key() -> str:
    h = hashlib.sha1()
    for f in _SOURCES + _DATA_FILES:
        h.update(f.name.encode())
        if f.exists():
            h.update(f.read_bytes() if f.suffix == ".py" else f"{f.stat().st_size}:{f.stat().st_mtime_ns}".encode())
    return h.hexdigest()[:16]


def _build() -> Bundle:
    from core import model  # imports sklearn: kept out of the login path
    hist = data.history()
    tr = model.train(hist)
    cur = data.current_cohort()
    pred = model.predict(tr, cur)
    contrib = model.contributions(tr, cur)
    df = pd.concat([cur, pred], axis=1)
    df["reasons"] = [model.top_reasons(contrib.loc[i]) for i in df.index]
    demo = not all((data.DATA_DIR / name).exists() for name in ("history.csv", "current_students.csv"))
    source = "demo" if demo else ("oulad" if (data.DATA_DIR / "oulad_info.json").exists() else "csv")
    return Bundle(df=df, tr=tr, class_median=cur[FEATURES + WEEK_COLS].median(), demo=demo, source=source)


def bundle() -> Bundle:
    """Return the trained bundle (memory, then disk, then train). Thread-safe; concurrent callers wait once."""
    global _bundle
    if _bundle is not None:
        return _bundle
    with _lock:
        if _bundle is not None:
            return _bundle
        import joblib
        path = CACHE_DIR / f"bundle-{_key()}.joblib"
        b = None
        if path.exists():
            try:
                b = joblib.load(path)
            except Exception:
                b = None
        if b is None:
            b = _build()
            try:
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                for old in CACHE_DIR.glob("bundle-*.joblib"):
                    old.unlink(missing_ok=True)
                tmp = path.with_suffix(".tmp")
                joblib.dump(b, tmp)
                os.replace(tmp, path)
            except OSError:
                pass  # read-only disk: still works, just retrains next start
        _bundle = b
        return b


def warm_up() -> None:
    """Start loading/training in the background (once per server process)."""
    if _bundle is None:
        threading.Thread(target=bundle, daemon=True, name="warm-model").start()


_live: tuple | None = None


def live() -> Bundle:
    """The bundle with homework marks mixed in for students who have an account.

    hw_completion, hw_avg and test_avg of those students blend the CSV figure with their closed assignments
    (see homework.blend); their risk, tier and reasons are recomputed. Everyone else is unchanged.
    """
    global _live
    from core import homework
    b = bundle()
    # Assignments created inside this prototype do not belong to the historical
    # Open University course presentation. Mixing their marks into OULAD input
    # features would manufacture a misleading historical risk estimate.
    if b.source == "oulad":
        return b
    stats = homework.live_stats()
    known = set(b.df["student_id"])
    stats = {s: v for s, v in stats.items() if s in known}
    if not stats:
        return b
    key = (id(b), tuple(sorted((k, tuple(sorted(v.items()))) for k, v in stats.items())))
    if _live and _live[0] == key:
        return _live[1]

    from dataclasses import replace
    from core import model
    df = b.df.copy()
    idx = df.index[df["student_id"].isin(stats)]
    for i in idx:
        st_ = stats[df.at[i, "student_id"]]
        if st_["hw_closed"]:
            df.at[i, "hw_completion"] = homework.blend(df.at[i, "hw_completion"], 100.0 * st_["hw_handed"], st_["hw_closed"])
        if st_["hw_graded"]:
            df.at[i, "hw_avg"] = homework.blend(df.at[i, "hw_avg"], st_["hw_graded"] * st_["hw_avg"], st_["hw_graded"])
        if st_["test_n"]:
            df.at[i, "test_avg"] = homework.blend(df.at[i, "test_avg"], st_["test_sum"], st_["test_n"])
    sub = df.loc[idx]
    pred = model.predict(b.tr, sub)
    contrib = model.contributions(b.tr, sub)
    for col in ("risk", "tier", "agreement"):
        df.loc[idx, col] = pred[col]
    for i in idx:
        df.at[i, "reasons"] = model.top_reasons(contrib.loc[i])
    out = replace(b, df=df)
    _live = (key, out)
    return out
