# Student Risk Predictor — real OULAD validation

**Completed: 6 November 2026.** Real historical OULAD validation passed after correcting the importer and evaluation isolation. These results demonstrate historical predictive signal; they do not establish performance on Turin students.

## Measured results

Accuracy uses the original, unchanged 50% model-score threshold. ROC AUC is a ranking measure, not a percentage of correct classifications.

| Evaluation | Training enrolments | Test enrolments | ROC AUC | Accuracy | Everyone-passes baseline |
|---|---:|---:|---:|---:|---:|
| Internal holdout; repeat students kept together | 12,352 | 5,292 | 0.8162 | 75.19% | 55.16% |
| Later 2014J presentation, all eligible enrolments | 17,644 | 8,879 | 0.7684 | 72.71% | 61.46% |
| Later 2014J; students entirely absent from training | 17,644 | 7,702 | 0.7633 | 72.80% | 63.62% |

**Use the third row as the stricter headline:** approximately **73% accuracy versus a 64% simple baseline**, with **AUC 0.76**. Its accuracy improvement is 9.18 percentage points. Zero students overlap between older training data and that test subset. Counts are enrolments; a person can have more than one enrolment.

The 95% student-cluster bootstrap intervals, using 1,000 resamples, are **0.7525–0.7737 for ROC AUC** and **71.88%–73.86% for accuracy**. They condition on the fitted model and do not quantify transfer uncertainty to another university.

The Model page displays the first row. The separate temporal audit refits the same model settings on all older enrolments before testing the later presentation. This is why the dashboard's AUC is 0.82 while the stricter later-cohort result is 0.76.

## What the flag thresholds mean

These are results on the stricter later cohort. The 25% and 50% thresholds were fixed before this evaluation; no thresholds or hyperparameters were tuned on the test results.

| Flag threshold | Precision | Recall of failures/withdrawals | Enrolments flagged |
|---|---:|---:|---:|
| Score ≥25%: Watch or Needs help | 47.47% | 85.26% | 65.35% |
| Score ≥50%: Needs help | 64.32% | 56.67% | 32.06% |

At 25%, the model finds 2,389 of 2,802 eventual failures/withdrawals, misses 413, and also flags 2,644 enrolments that ultimately pass. The lower threshold favors recall and creates a substantial support workload. Scores are uncalibrated; a 50% score is not a verified 50% failure probability.

## Source and cohort construction

Downloaded the seven original CSV tables from the [UCI OULAD repository](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset), DOI [10.24432/C5KK69](https://doi.org/10.24432/C5KK69). Attribution: Kuzilek, Hlosta and Zdrahal; Open University Learning Analytics Dataset, CC BY 4.0. The derivative retains numerical features and pseudonymous grouping, not the original student IDs or demographic fields. Transformations are described below and implemented in the supplied converter.

- Source: **32,593 enrolments**, **28,785 distinct anonymized student IDs**, 22 module-presentations.
- Excluded **6,061** withdrawals before the checkpoint and **9** additional registrations at/after it; **26,523** enrolments remain.
- Training pool: **17,644** older enrolments from 2013B, 2013J and 2014B.
- Later test: **8,879** eligible 2014J enrolments. Removing **1,177** enrolments whose students occur in older data leaves the **7,702** stricter test enrolments.
- The app displays **400** sampled historical enrolments. Evaluation uses the full eligible cohorts, not that display sample.
- Predictors use LMS activity on **days 0–55** and assessment submissions before day 56. Fail/Withdrawn is target 1; Pass/Distinction is target 0. Targets are not model inputs.

## Corrections made before measuring

1. Parse OULAD's literal `?` markers as missing values. The previous real importer crashed when comparing these strings with numeric dates.
2. Preserve observed features for evaluation. Fit missing-value replacements on the training fold only; later test values cannot change older training inputs.
3. Keep all enrolments of a repeat student on one side of the internal split. Pseudonymous student hashes support grouping without exporting the original IDs to the app.
4. Train only on presentations older than the selected replay, including when an older replay is explicitly selected. Exclude students registered after the prediction checkpoint.
5. Add full later-presentation evaluation, a separate unseen-student result, confidence intervals, raw-table row counts and SHA-256 hashes. Keep evaluation outcomes outside student API responses.

The Random Forest settings remain unchanged: 300 trees, minimum leaf size 8, square-root feature sampling, random seed 42. Display features use older-cohort median replacements; internal evaluation uses preserved observations and learns its replacements from the training fold. A wholly unobserved training grade field uses an explicit neutral value of 50.

## Verification and practical limits

- **85 automated tests pass:** all original 80 plus five new OULAD checks covering actual missing-value syntax, day-56 isolation, historical presentation order, repeat-student separation and imputation isolation. Tests use isolated temporary demo inputs and do not consume or overwrite imported data.
- Independently reconstructed **528 observed feature values across 66 enrolments**, covering three enrolments in each of the 22 module-presentations; all matched the raw source within the exported one-decimal precision.
- Real-data API checks confirm 400 historical display enrolments, matching internal model metrics, enforced student/teacher/admin permissions, hidden student risk fields, no fictional names and no static access to evaluation CSV targets.
- JavaScript syntax checks pass. This validation used Linux with Python 3.12.14; it does not complete the separate Windows 3.14 or deployment acceptance checks.
- OULAD represents historical UK distance learning, not live Turin records. Attendance and login inputs are LMS proxies; previous result is an early scored assessment, not a previous-term grade.
- About 69.7% of older early quiz averages are missing. Median imputation cannot reconstruct unknown grades and can conceal differences in assessment schedules.
- Grade-publication timestamps are unavailable. Submission date is only a proxy for when a score could have been known; strict real-time score availability cannot be proven from these tables.
- Historical student activity, missingness and course mix may differ at Turin. Calibration, local validation and an appropriate intervention policy remain separate work.

## Reproduce

The updated ZIP already contains the prepared inputs, evaluation observations and measured results. Extract it and use `start-python314.cmd` as before to view the imported historical sample.

For a fresh raw-source reproduction on Windows, stop the server and run `setup-real-oulad.cmd`. It downloads the source, rebuilds the inputs and runs the complete evaluation. Equivalent commands after installing the project requirements:

```bash
python tools/download_oulad.py
python tools/prepare_oulad.py data/oulad/raw --sample 400
python tools/evaluate_oulad.py
```

Read `data/oulad_validation.json` for full precision, per-module results, confidence intervals, model parameters, package versions and source checksums. `data/oulad_temporal_predictions.csv` contains the pseudonymous audit predictions. `data/oulad_evaluation.csv` contains the unfilled observations and outcomes for reproducibility; neither is a student-facing endpoint.

Measured scientific packages: numpy 2.3.5, pandas 2.2.3, scipy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3. Changing package versions can slightly change results; rerun the evaluator in the target environment when exact reproduction is required.
