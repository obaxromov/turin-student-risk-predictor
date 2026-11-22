# November 1 reviewer fixes — status pending independent acceptance

**Baseline:** `student-risk-predictor-web-v8-python314`. This package is a revised copy, not a change to another version. **No boxes in the reviewer's original list have been ticked here**; only the reviewer can mark an item accepted after rerunning their checks.

| ID | Implemented here | Local evidence / outstanding check |
|---|---|---|
| A1 | Yes | Replaced speculative extrapolation with last-4-week average and supportive rising/falling/steady message. No 0% forecast headline. Added falling-series API test and no-risk-leak test. |
| A2 | Yes | Measured dark badge contrast: Needs help **5.41:1**, Watch **6.74:1**, On track **6.87:1**; all >=4.5:1. Chromium Overview/Students/Model/Profile snapshots saved externally. |
| A3 | Browser sweep completed, 6 November | **144 rendered cases** across teacher/student/admin pages, account menus and login: RU/UZ, light/dark, **1366px and 390px**. No page-level horizontal overflow, clipped checked headings/labels/buttons or missing rendered translation keys. All 13 course tiles included. Scrollable tables/navigation remain intentionally scrollable inside their own containers. Physical-device review remains separate. |
| A4 | **Real-data validation completed, 6 November 2026** | Downloaded all seven official UCI OULAD tables. Fixed `?` parsing, preserved observed values for training-only imputation, grouped repeat students and excluded later presentations from training. Internal grouped holdout: AUC **0.8162**, accuracy **75.19%**. Later 2014J test restricted to previously unseen students: **7,702 enrolments**, AUC **0.7633**, accuracy **72.80%**, baseline **63.62%**. Prepared inputs and 400 display samples are included. See `OULAD_VALIDATION_2026-11-06.md` and `data/oulad_validation.json`. This does not establish Turin accuracy. |
| B1–B2 | Yes | Model subtitle and unique metric captions; ROC AUC shown as decimal. |
| B3 | Yes | Both Students filters capitalized using translated keys. |
| B4 | Yes | Student profile assignments have title/course/deadline/status/mark, with actual `course_name` joined from SQLite; no misleading button/header. |
| B5 | Yes | Admin management form spacing, one heading, no self-deactivation or self role-change controls, translated audit action codes and dash for missing target. |
| B6 | Yes | Translation mapping for all 13 display course names, Russian assignment plural helper. Database retains stable English names. |
| B7 | Yes, toggle available | `APP_DEMO_LOGIN=0` hides role buttons and returns 404 from the endpoint; demo account seeding is independent. On a **new** database, `APP_ADMIN_PASSWORD`, `APP_TEACHER_PASSWORD` and `APP_STUDENT_PASSWORD` can set private seeded credentials. Existing DB passwords are unaffected. **Do not expose default credentials publicly.** |
| C1 | Yes | Reformatted `api/features.py`, separate statements, role-specific docstrings for **23 endpoints**. AST comparison confirms only docstrings and whitespace changed in the formatter pass; route list unchanged. |
| C2 | Yes | Streaming ASGI body limit **30 MB** (413); no more than **3** materials per assignment, 20MB each; accepted by API tests. |
| C3 | Yes | Reject past dates on create and deadline change with HTTP 400 (`deadline_in_past`); translated form error. |
| C4 | Yes | New single current-state README without V6/V7/V8 changelog. |
| C5 | Yes | Added regression tests for projection, privacy, badges, translations, profile course names, request limits, demo toggle, deadlines, import safeguards, endpoint docstrings. |
| D1 | Not tested | Modified package still needs a fresh Windows + Python 3.14 launch check on owner's PC. Earlier V8 did start there, but this one hasn't been executed there. |
| D2 | Not tested | Docker daemon / public hosting not available here. Need actual Docker build, deployment and phone visit. |
| D3 | CSV browser workflow verified, 6 November | Teacher downloaded the template, invalid CSV was rejected with a readable message, and a three-question number/text/choice CSV was imported and saved. Student answered through the UI; teacher saw **6/6**. Student API question objects contain no answer keys. No unexpected JS/console errors. Earlier written/file/attachment workflow evidence is retained. |
| E1 | Provided | `PRESENTATION_CHEATSHEET.md` with 5-stage pipeline, Random Forest, 8 features, metrics/limitations and teacher questions. |
| E2–E3 | Human work | Study `core/data.py` → `core/model.py` → `core/service.py`; rehearse mock questions. |
| E4 | Backup created | Preserve original V8 ZIP. Keep last week of November as a buffer. |

**Regression update, 6 November:** all original 80 tests plus five new OULAD checks pass (**85 total**) under Python 3.12/Linux. Real-data API checks confirm 400 historical enrolments, matching Model metrics, enforced roles, hidden student risk fields and no fictional names. The browser CSV flow and 144-case RU/UZ layout sweep now pass; see `UI_ACCEPTANCE_2026-11-06.md` and `data/ui_acceptance.json`. Fixed translated API error messages and the assignment settings heading. **Windows 3.14, Docker/public deployment and a physical phone visit still require their separate checks.**
