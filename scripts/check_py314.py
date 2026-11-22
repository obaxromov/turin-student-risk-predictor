"""Quick dependency/Windows App Control diagnostic for the Python 3.14 launcher.

Read-only: imports libraries and reports errors. It never changes Windows security settings.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import platform
import sys


def main() -> int:
    print(f"Python: {sys.version.split()[0]} ({platform.system()}, {platform.machine()})")
    if sys.version_info[:2] != (3, 14):
        print("ERROR: This launcher expects Python 3.14; use start-python314.cmd.")
        return 1

    for name in ("numpy", "pandas", "scipy", "scikit-learn"):
        try:
            print(f"{name}: {importlib.metadata.version(name)}")
        except importlib.metadata.PackageNotFoundError:
            print(f"{name}: NOT INSTALLED")
            return 1

    for name in ("numpy", "pandas", "scipy.optimize", "sklearn.ensemble"):
        try:
            importlib.import_module(name)
            print(f"OK: import {name}")
        except (Exception, OSError) as exc:
            print(f"FAILED: import {name}\n{type(exc).__name__}: {exc}")
            message = str(exc).lower()
            if "policy" in message or "политика" in message or "заблок" in message:
                print("\nWindows Application Control is preventing a native library from loading.")
                print("This is a Windows device/security policy issue, not a Python syntax issue.")
                print("Do not disable Windows security or download replacement DLLs.")
                print("Open Event Viewer > Applications and Services Logs > Microsoft >")
                print("Windows > CodeIntegrity > Operational and look for event 3077")
                print("at the time of this error. See README.md for safe next steps.")
            return 1

    try:
        importlib.import_module("api.main")
        print("OK: import api.main")
    except Exception as exc:
        print(f"FAILED: import api.main\n{type(exc).__name__}: {exc}")
        return 1

    print("\nPython 3.14 dependency checks passed. Starting the web server...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
