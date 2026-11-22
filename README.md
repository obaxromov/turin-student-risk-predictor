# Student Risk Predictor — Web application

A **web-only university prototype** using HTML/CSS/JavaScript, FastAPI, SQLite and a scikit-learn Random Forest. There is no Streamlit application. This project is intended for demonstration with simulated data or anonymised **historical** OULAD research records. **It is not approved for real Turin student data or production deployment.**

### Real OULAD validation completed — 6 November 2026

This updated package includes prepared real historical OULAD inputs and 400 sample dashboard enrolments. Start the app normally; another download is needed only to reproduce conversion and evaluation from the raw source. No raw 450 MB download, model cache, account database or uploaded files are included.

The strict later-cohort test covers **7,702 enrolments from students absent from training**: **ROC AUC 0.7633**, **72.80% accuracy** at the unchanged 50% threshold, versus a **63.62% everyone-passes baseline**. These are historical OULAD results, not verified accuracy for Turin students. The Model page separately shows the student-grouped internal holdout: AUC **0.8162**, accuracy **75.19%**.

See `OULAD_VALIDATION_2026-11-06.md` and `data/oulad_validation.json` for cohort definitions, confidence intervals, limitations and reproducibility details.

The browser CSV workflow and **144 RU/UZ layout cases** also pass across all roles, desktop/mobile widths and light/dark themes. API errors use their translated messages, and assignment controls have an assignment-specific heading. See `UI_ACCEPTANCE_2026-11-06.md`. Windows 3.14 launch and public deployment remain separate checks.

## Launch on Windows with Python 3.14

1. Extract the entire ZIP into a writable folder.
2. Double-click **`start-python314.cmd`**. The launcher creates `.venv314`, installs suitable compiled packages, tests SciPy/scikit-learn and starts FastAPI.
3. Open **http://127.0.0.1:7860**. Keep the terminal open while using the website.

Or from PowerShell in this folder:

```powershell
py -3.14 -m venv .venv314
.\.venv314\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-web.txt
.\.venv314\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 7860
```

For Linux/macOS with a supported Python version: `python -m pip install -r requirements-web.txt` and `python -m uvicorn api.main:app --port 7860`.

**Do not open `web/index.html` directly.** It needs the API.

### Demo accounts (local, simulated data only)

| Role | Username | Demo password |
|---|---|---|
| Teacher | `teacher1` | `teacher123` |
| Student | `student1` | `student1pass` |
| Admin | `admin1` | `admin123` |

The demo role buttons work only when `APP_DEMO_LOGIN` is not set to `0`. **Never expose default credentials to a public site.** `APP_DEMO=0` alone is **not** an appropriate way to secure an installation: it also disables creating initial demo accounts, so no one can sign in to an empty database.

To disable one-click role logins while keeping the three roles, set `APP_DEMO_LOGIN=0` **before** launching. For a **fresh** private demo database only, you can also set `APP_ADMIN_PASSWORD`, `APP_TEACHER_PASSWORD`, and `APP_STUDENT_PASSWORD` to strong, private passwords **before the database is first created**. These variables do **not** reset passwords already stored in an existing SQLite file. Use a new `APP_DB` path (or intentionally reset the disposable demo database) to seed fresh accounts. The Admin interface can change other account passwords; use different passwords for each real user. No single switch makes this a production-safe system.

PowerShell example for a **new private demo database**:

```powershell
$env:APP_DB="data/private-demo.db"
$env:APP_DEMO_LOGIN="0"
$env:APP_ADMIN_PASSWORD="choose-a-unique-strong-secret"
$env:APP_TEACHER_PASSWORD="choose-another-unique-strong-secret"
$env:APP_STUDENT_PASSWORD="choose-a-third-strong-secret"
.\start-python314.cmd
```

Change these sample secrets yourself before launching. Keep them out of public repositories and screenshots.

### Windows Application Control error

If SciPy reports that a `.pyd`/DLL is blocked by a Windows *Application Control policy*, that is separate from Python-version compatibility. Check **Event Viewer → Applications and Services Logs → Microsoft → Windows → CodeIntegrity → Operational**, especially event ID 3077, and contact the device administrator if the computer is managed. Do not disable security protections or download replacement DLLs from unofficial websites. If changing scientific-library versions, delete only `data/cache/` after stopping the server so the model is retrained; don't delete the database inadvertently.

## Import real historical OULAD records

1. Stop the running app. On Windows double-click **`setup-real-oulad.cmd`**.
2. It downloads the official OULAD ZIP from the UCI Machine Learning Repository, extracts seven CSV files, prepares an eight-week dataset, clears the old model cache and runs a verification script.
3. Look for `SUCCESS - OULAD imported.` and open `data/oulad_validation.json`.
4. Restart `start-python314.cmd`; the **Demo data** badge should disappear. Inspect the **Model** page and its OULAD proxy warning.

If automatic download fails, download from <https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset> and use:

```powershell
.\.venv314\Scripts\python.exe tools\download_oulad.py --zip "C:\path\to\oulad.zip"
.\.venv314\Scripts\python.exe tools\prepare_oulad.py data\oulad\raw --sample 400
.\.venv314\Scripts\python.exe tools\evaluate_oulad.py
```

The report supplies **actual measured** internal holdout and full later-presentation ROC AUC, accuracy, pass-all baseline, precision, recall and tier outcomes. The internal holdout keeps repeat enrolments of a student together and fits missing-value replacements only on training rows. The later test fits on older presentations only, with a separate result excluding all students seen in older training data. Its 95% intervals resample students 1,000 times. Neither test is restricted to the 400 display samples. The raw archive is **not included** in this source ZIP. **Do not quote synthetic demo ROC AUC as OULAD accuracy.** The study uses first-eight-week activity and assessment proxies for features such as attendance. OULAD has no physical attendance register or real names; the displayed samples are historical records, **not a live class**. Submissions and LMS activity from day 56 onward are excluded. Score-publication dates are unavailable, so submission date is an imperfect proxy for when a grade was known. Prototype-created assignments do not alter historical predictions.

## Features and design

- **Teacher** — Overview, all student IDs, risk groups and individual profiles; notes, contacted status, audited demo name reveal; prediction and CSV scoring; Model evaluation; courses, questions, file submissions, grading and deadlines.
- **Student** — private own progress, **observed** last-four-week engagement summary, goal and assignments. The API does **not** expose risk/tier/class median or model answer keys to students.
- **Admin** — account creation and management, role changes, password resets and audit log. Self-deactivation and demoting the current admin are not offered in the interface.
- **UI** — soft-glass controls, readable dark tier badges, mobile layout, clean course tiles, translated EN/RU/UZ display names, correct Russian assignment plurals, a sample questions-CSV download button and no speculative 0% four-week forecast.

The Student page deliberately **does not** extrapolate noisy week values into a percentage forecast. It shows a recent average and supportive trend text instead. Eight weekly engagement values are available, **not** a daily GitHub contributions record.

### CSV questions and attachments

The New assignment page offers **Download question CSV template**. Required columns: `kind,prompt,answer`. Optional: `choices,points,tolerance`; a multiple-choice `choices` cell uses the `|` separator. Up to **three** materials per assignment are accepted; each individual file is limited to 20 MB. Requests larger than 30 MB are rejected with HTTP 413 **before** they are parsed fully into memory.

### Machine-learning method

Features: `attendance`, `attendance_trend`, `test_avg`, `hw_completion`, `hw_avg`, `logins_per_week`, `logins_trend`, `prev_result`. The Random Forest learns from a historical training cohort; evaluation uses a held-out set and the pass-all baseline. Scores are **not calibrated probabilities** and should only initiate supportive conversations, not final decisions. Model-page **ROC AUC is a decimal** (e.g. `0.77`), not a percentage of correct classifications. See `PRESENTATION_CHEATSHEET.md` for an explanation of the pipeline and likely instructor questions.

## Tests

```bash
python -m pytest -q
node --check web/app.js
node --check web/pages.js
node --check web/controls.js
```

`REVIEW_FIX_STATUS.md` distinguishes implemented fixes from checks still requiring reviewer confirmation. Chromium component and API-backed UI checks were completed with a browser bridge because direct browser navigation to local HTTP was blocked in the test environment.

## Deployment

The Render Blueprint in `render.yaml` uses its free Docker plan. A fresh checkout and the deployed container use simulated demo data. The service generates private passwords for `teacher1`, `student1` and `admin1` and disables one-click demo login. View those passwords in the service's Environment settings. Free hosting can reset demo SQLite changes and uploaded files when the service stops.

The included `Dockerfile` is a starting point for a web demo but has **not been built and tested here**. Do not assume zero-cost hosting is persistent; demo SQLite accounts and uploaded files may disappear on free ephemeral services. Never put raw private student records in a public repository or Docker image. `.gitignore` / `.dockerignore` exclude local `data/`, virtual environments and `.env` files. For production use, replace seeded accounts with institutional authentication, secured persistent storage, appropriate access scopes, institution-level authorization, audit-retention practices and a security/privacy review.

## Structure

```text
api/           FastAPI routes, sessions, security checks
core/          Random Forest, data conversion inputs, SQLite, grading rules, localization
web/           HTML, CSS and JavaScript UI
scripts/       Python 3.14 dependency check
tools/         OULAD downloader, converter and validator
tests/         Automated regression/acceptance tests
start-python314.cmd, setup-real-oulad.cmd  Windows launch/import helpers
```

*OULAD source:* Kuzilek, Hlosta & Zdrahal, Open University Learning Analytics Dataset, UCI Machine Learning Repository, CC BY 4.0.
