@echo off
setlocal
cd /d "%~dp0"
title Student Risk Predictor - Import Real OULAD Data

echo =======================================================
echo  REAL OULAD DATA IMPORT - Student Risk Predictor

echo =======================================================
echo IMPORTANT: Close the running web server before importing.
echo This imports historical Open University records, NOT live Turin student data.
echo Raw data needs around 500 MB of disk space.
echo.

if not exist ".venv314\Scripts\python.exe" (
    echo Creating your Python 3.14 environment ...
    py -3.14 -m venv .venv314
    if errorlevel 1 goto failed
)
set "PYTHON=.venv314\Scripts\python.exe"
"%PYTHON%" -c "import pandas, sklearn, scipy" >nul 2>&1
if errorlevel 1 (
    echo Installing compatible dependencies ...
    "%PYTHON%" -m pip install --disable-pip-version-check --only-binary=:all: -r requirements-web.txt
    if errorlevel 1 goto failed
)

echo [1/4] Downloading/extracting the 7 real OULAD CSV files ...
"%PYTHON%" tools\download_oulad.py
if errorlevel 1 goto failed

echo.
echo [2/4] Building the model input tables from weeks 1-8 ...
"%PYTHON%" tools\prepare_oulad.py data\oulad\raw --sample 400
if errorlevel 1 goto failed

echo.
echo [3/4] Clearing ONLY the previously cached ML model ...
if exist "data\cache" rmdir /s /q "data\cache"
if errorlevel 1 goto failed

echo.
echo [4/4] Validating the imported historical data and evaluation ...
"%PYTHON%" tools\evaluate_oulad.py
if errorlevel 1 goto failed

echo.
echo SUCCESS - OULAD imported. Your 400 displayed example enrolments

echo are sampled from a historical course presentation, not a live class.
echo Your sample demo accounts are still available.
echo Read data\oulad_validation.json for your REAL held-out model metrics.
echo Start start-python314.cmd again and open http://127.0.0.1:7860.
echo The first model training can take longer than the demo model.
echo.
pause
exit /b 0

:failed
echo.
echo Import did not finish. Your project can still run its previous data.
echo If automatic download failed, manually download OULAD from

echo https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset

echo and run: .venv314\Scripts\python.exe tools\download_oulad.py --zip YOUR_ZIP_PATH
pause
exit /b 1
