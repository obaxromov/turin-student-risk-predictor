@echo off
setlocal
cd /d "%~dp0"
title Student Risk Predictor - Python 3.14

py -3.14 -c "import sys; assert sys.version_info[:2] == (3,14)" >nul 2>&1
if errorlevel 1 (
    echo Python 3.14 was not found by the Python launcher.
    echo Run: py --list
    pause
    exit /b 1
)

if not exist ".venv314\Scripts\python.exe" (
    echo Creating an isolated Python 3.14 environment...
    py -3.14 -m venv .venv314
    if errorlevel 1 goto fail
)

".venv314\Scripts\python.exe" -c "import sys; assert sys.version_info[:2] == (3,14)" >nul 2>&1
if errorlevel 1 (
    echo The .venv314 environment is not running Python 3.14.
    echo Remove only the .venv314 folder, then try again.
    goto fail
)

echo Installing/updating Python 3.14-compatible packages from PyPI...
".venv314\Scripts\python.exe" -m pip install --disable-pip-version-check --only-binary=:all: -r requirements-web.txt
if errorlevel 1 goto fail

echo Checking installed AI libraries...
".venv314\Scripts\python.exe" scripts\check_py314.py
if errorlevel 1 goto fail

echo.
echo Visit http://127.0.0.1:7860 in your browser.
".venv314\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 7860
if errorlevel 1 goto fail
pause
exit /b 0

:fail
echo.
echo Unable to start. Read the error above and the Python 3.14 section in README.md.
echo If Windows reports a policy block, reinstalling Python alone may not fix it.
pause
exit /b 1
