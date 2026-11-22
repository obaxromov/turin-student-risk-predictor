"""Shared test setup: point the app at a throw-away database BEFORE anything imports core.db."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["APP_DB"] = str(Path(tempfile.mkdtemp()) / "test.db")
os.environ["APP_DEMO"] = "1"

# Keep the original demo regression assertions reproducible after real data
# has been imported. Tests must neither consume nor modify the owner's CSVs.
from core import data
data.DATA_DIR = Path(tempfile.mkdtemp(prefix="student-risk-test-data-"))
