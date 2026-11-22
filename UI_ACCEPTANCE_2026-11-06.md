# Student Risk Predictor — browser acceptance

Completed: **6 November 2026**. The validated OULAD build passed the question CSV workflow and a 144-case Russian/Uzbek layout sweep in Chromium 153 on Linux.

## Workflow verified in the browser

1. Signed in as the teacher and downloaded `questions-template.csv`; checked its required header.
2. Uploaded an invalid CSV. The server returned the expected HTTP 400 and the UI displayed a readable CSV-format error.
3. Imported a valid three-question CSV containing a numerical answer, a text answer and a multiple-choice question; created an assignment through the UI.
4. Signed in as a student, confirmed the question API objects omit answer keys, and answered all three questions using the actual form and custom choice control.
5. Submitted the answers and refreshed the teacher's assignment page. The recorded result was **6/6**.

All test assignments and submissions used a disposable local database. Historical OULAD features and outcome evaluations were not changed by this exercise.

## Layout coverage

Each state was checked in **Russian and Uzbek**, **light and dark themes**, at **1366×900** and **390×844** browser viewports: eight combinations per state.

| Role/state | Pages or panels checked | Cases |
|---|---|---:|
| Teacher | Overview, courses, assignments, students, student profile, prediction, model, new assignment, assignment detail, account menu | 80 |
| Student | Progress, courses, assignments, assignment detail, account menu | 40 |
| Admin | Accounts and account menu | 16 |
| Signed out | Login | 8 |
| Total | 18 rendered states × eight combinations | **144** |

Results: **zero page-level horizontal overflows**, zero clipped headings/labels/buttons among the checked elements, zero missing rendered translation keys, and zero unexpected browser JavaScript or console errors. All 13 course tiles were included. Tables and navigation may scroll inside their own containers; that intentional behavior was excluded from text-clipping checks. Three representative Russian mobile screenshots were also visually inspected during QA.

## Fixes from this check

- Known API error codes now resolve to their translated text instead of displaying strings such as `hw_err_csv`. The invalid-CSV UI check confirms the readable English message; the shared translation mapping provides Russian and Uzbek equivalents. The existing translated past-deadline message is preserved.
- The assignment controls panel now says **Assignment settings / Настройки задания / Topshiriq sozlamalari**, matching its deadline and deletion controls.

All **85 Python tests pass** after these fixes, and the frontend JavaScript syntax checks pass. OULAD model code, feature preparation and measured statistical results were not changed by these UI fixes. Full browser measurements and workflow results are included in `data/ui_acceptance.json`.

## Next check on Windows

1. Extract the updated project ZIP into a writable folder.
2. Run **`start-python314.cmd`** with Python **3.14** installed.
3. Open **http://127.0.0.1:7860** and sign in as the teacher.
4. Confirm **400** students on Overview, and internal **ROC AUC about 0.82** on the Model page. Its more precise measured value is 0.8162; the separate stricter later-cohort audit is 0.7633.
5. Open the student and admin roles and confirm they load normally.

This browser run used Linux and an emulated mobile viewport. The updated Windows 3.14 build, Docker/public hosting and a visit from a physical phone have not been verified here. Presentation rehearsal remains a human preparation task.
