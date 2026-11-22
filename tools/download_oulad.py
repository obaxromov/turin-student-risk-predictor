"""Download OULAD from the UCI Machine Learning Repository and safely extract its CSVs.

    python tools/download_oulad.py
    python tools/download_oulad.py --zip C:\\Users\\You\\Downloads\\oulad.zip

Source: https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset
The dataset is licensed CC BY 4.0 (Kuzilek, Hlosta & Zdrahal).
Requires no third-party Python libraries. Raw CSVs use approximately 450 MB.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "oulad" / "raw"
SOURCE = "https://archive.ics.uci.edu/static/public/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset.zip"
EXPECTED = (
    "assessments.csv", "courses.csv", "studentAssessment.csv", "studentInfo.csv",
    "studentRegistration.csv", "studentVle.csv", "vle.csv",
)


def _download(dest: Path) -> None:
    req = urllib.request.Request(SOURCE, headers={"User-Agent": "StudentRiskPredictor-education/1.0"})
    print("Downloading real OULAD from the UCI repository (~45 MB compressed)...", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=90) as response, dest.open("wb") as out:
            total = int(response.headers.get("Content-Length", "0"))
            downloaded = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                out.write(block)
                downloaded += len(block)
                if downloaded // (8 * 1024 * 1024) != (downloaded - len(block)) // (8 * 1024 * 1024):
                    print(f"  {downloaded // (1024 * 1024)} MB" +
                          (f" of {total // (1024 * 1024)} MB" if total else ""), flush=True)
    except (OSError, urllib.error.URLError) as exc:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"Download failed: {exc}") from exc


def _extract(source: Path, output: Path, level: int = 0) -> set[str]:
    """Extract only known CSV basenames, not arbitrary paths or executable files."""
    if level > 2:
        raise RuntimeError("Unexpected archive nesting")
    found = set()
    with zipfile.ZipFile(source) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            basename = Path(item.filename.replace('\\', '/')).name
            if basename in EXPECTED:
                if item.file_size > 1_000_000_000:
                    raise RuntimeError(f"Unreasonable CSV size: {basename}")
                target = output / basename
                if not target.exists() or target.stat().st_size != item.file_size:
                    with z.open(item) as inp, target.open("wb") as out:
                        shutil.copyfileobj(inp, out, 1024 * 1024)
                found.add(basename)
        if not EXPECTED_SET.issubset(found):
            for item in z.infolist():
                if item.is_dir() or not item.filename.lower().endswith(".zip"):
                    continue
                if item.file_size > 1_000_000_000:
                    raise RuntimeError("Unexpected nested archive size")
                with tempfile.TemporaryDirectory() as td:
                    nested = Path(td) / "nested.zip"
                    with z.open(item) as inp, nested.open("wb") as out:
                        shutil.copyfileobj(inp, out, 1024 * 1024)
                    found.update(_extract(nested, output, level + 1))
    return found


EXPECTED_SET = set(EXPECTED)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", type=Path, dest="archive", help="Existing downloaded ZIP; skip the network download")
    ap.add_argument("--out", type=Path, default=DATA_DIR, help="Destination for raw OULAD CSV files")
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if all((out / name).is_file() for name in EXPECTED):
        print(f"All seven OULAD CSV files are already available in {out}")
        return
    try:
        if args.archive:
            if not args.archive.is_file():
                raise RuntimeError(f"ZIP not found: {args.archive}")
            found = _extract(args.archive, out)
        else:
            with tempfile.TemporaryDirectory() as td:
                archive = Path(td) / "oulad.zip"
                _download(archive)
                found = _extract(archive, out)
        missing = EXPECTED_SET - found - {name for name in EXPECTED if (out / name).exists()}
        if missing:
            raise RuntimeError("Archive is missing required files: " + ", ".join(sorted(missing)))
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        sys.exit(f"ERROR: {exc}\nAlternative: download the OULAD ZIP at "
                 "https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset "
                 "and run tools/download_oulad.py --zip PATH_TO_ZIP")
    print(f"Extracted all 7 real OULAD CSV files to: {out}")
    print("Source: Open University Learning Analytics Dataset, CC BY 4.0.")


if __name__ == "__main__":
    main()
