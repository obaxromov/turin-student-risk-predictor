"""The OULAD converter is tested on a tiny fake dataset in the same file format."""
import sys

import numpy as np
import pandas as pd

from core import data
from tools import prepare_oulad as po


def _fake(folder, n_per=150):
    rng = np.random.default_rng(1)
    info, vle, sa, reg = [], [], [], []
    ids = iter(range(1000, 100000))
    for pres in ("2013J", "2014B", "2014J"):
        for _ in range(n_per):
            sid = next(ids)
            good = rng.random() > 0.35
            res = "Pass" if good else rng.choice(["Fail", "Withdrawn"])
            info.append(("AAA", pres, sid, res))
            reg.append(("AAA", pres, sid, np.nan if res != "Withdrawn" else 200))
            for d in range(0, 56, 2):
                if rng.random() < (0.7 if good else 0.3):
                    vle.append(("AAA", pres, sid, d, int(rng.integers(1, 30))))
            for aid in (1, 2):
                a = int(f"{aid}{pres[2:4]}{ord(pres[-1])}")
                if rng.random() < (0.9 if good else 0.4):
                    sa.append((a, sid, 20 * aid + 5, int(rng.integers(50, 100) if good else rng.integers(10, 60))))
    asm = []
    for pres in ("2013J", "2014B", "2014J"):
        for aid, typ in ((1, "TMA"), (2, "CMA")):
            asm.append((int(f"{aid}{pres[2:4]}{ord(pres[-1])}"), "AAA", pres, typ, 20 * aid + 10, 10))
    pd.DataFrame(info, columns=["code_module", "code_presentation", "id_student", "final_result"]).to_csv(folder / "studentInfo.csv", index=False)
    pd.DataFrame(reg, columns=["code_module", "code_presentation", "id_student", "date_unregistration"]).to_csv(folder / "studentRegistration.csv", index=False)
    pd.DataFrame(vle, columns=["code_module", "code_presentation", "id_student", "date", "sum_click"]).to_csv(folder / "studentVle.csv", index=False)
    pd.DataFrame(sa, columns=["id_assessment", "id_student", "date_submitted", "score"]).assign(is_banked=0).to_csv(folder / "studentAssessment.csv", index=False)
    pd.DataFrame(asm, columns=["id_assessment", "code_module", "code_presentation", "assessment_type", "date", "weight"]).to_csv(folder / "assessments.csv", index=False)


def test_converter_output_is_loadable_and_private(tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    _fake(src)
    hist, cur = po.build(src)
    assert set(po.FEATURES + ["failed"]) <= set(hist.columns)
    assert len(cur) == 150 and len(hist) > 200
    assert not hist[po.FEATURES].isna().any().any() and not cur[po.FEATURES].isna().any().any()
    for col, (lo, hi) in data.RANGES.items():
        assert hist[col].between(lo, hi).all(), col
    assert "id_student" not in cur.columns and cur["student_id"].str.startswith("S").all()
    assert not data.validate_features(cur)
    # signal exists: failing students were less active
    assert hist.groupby("failed")["attendance"].mean().loc[1] < hist.groupby("failed")["attendance"].mean().loc[0]
