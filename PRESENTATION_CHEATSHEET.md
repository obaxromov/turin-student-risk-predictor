# Student Risk Predictor — presentation and Q&A notes

## A short demo flow (about 5–7 minutes)

1. **Problem:** some students disengage before the course ends, and teachers need a way to prioritize support.
2. **Data:** explain OULAD, a *historical anonymized UK university dataset*, or identify the dashboard as simulated if you haven't imported it. These are **not live Turin records**.
3. **Model:** show the eight numerical features, the Random Forest classifier (300 trees), the historical training / held-out test split, and the 25% / 50% *score* thresholds.
4. **Teacher:** open Overview, select a student in the weekly activity grid, open their profile, and show why the model flagged a student. Reveal names only in simulated demo mode.
5. **Student:** show only personal progress, goals and assignments, not risk tiers or class comparisons.
6. **Admin:** show accounts and role permissions, then return to the Model evaluation page.
7. **Limitations:** proxies for attendance and logins, historical rather than real-time data, unknown transfer to Turin, uncalibrated scores and the absence of real names. Predictions are a signal for support, not a verdict.

## Explain the pipeline in five steps

1. Download OULAD and join student, activity and assessment CSVs using their module/presentation/student identifiers.
2. Build eight week-8 features and a later binary outcome: Pass/Distinction = 0; Fail/Withdrawn = 1 (withdrawals before week 8 are excluded).
3. Keep repeat enrolments of the same student together in a seeded 70/30 group split of older historical records. Fit missing-value replacements on training rows only, train a Random Forest and evaluate on the held-out students; compare against a baseline that assumes everyone passes.
4. Use the fitted forest on a later **historical** presentation, whose result is deliberately not provided to the model. Return a score, risk tier and explanatory indicators.
5. Present the result in the web dashboard; teachers can triage and monitor, while students see only their own non-risk progress data.

## Verified real OULAD results — 6 November 2026

Measured results are saved in `data/oulad_validation.json`:

- Historical training-pool enrolments: **17,644** (2013B, 2013J, 2014B).
- Later presentation: **2014J**, **8,879** eligible enrolments; **400** displayed in the dashboard.
- Internal student-grouped holdout: **12,352** training / **5,292** test enrolments; zero overlapping students.
- Held-out ROC AUC: **0.8162**; accuracy at score ≥50%: **75.19%**.
- Internal everyone-passes baseline: **55.16%**.
- Internal precision / recall of flags at ≥25%: **56.34% / 88.79%**.

For a stronger separate check, the same forest settings were fitted on all older enrolments and tested on 2014J. On **7,702** later enrolments from students entirely absent from older training data: **AUC 0.7633**, **accuracy 72.80%**, baseline **63.62%**. The AUC 95% interval is **0.7525–0.7737**. At the 25% flag threshold, recall is **85.26%**, precision **47.47%** and **65.35%** of enrolments are flagged. The Model page shows the internal holdout, so its numbers differ from the later-cohort audit.

Suggested explanation: “On real historical OULAD data, our stricter later-cohort test reached about 73% accuracy versus a 64% simple baseline, with AUC 0.76. That demonstrates useful historical predictive signal, but does not prove accuracy for Turin students.”

**Never reuse the synthetic demo model's metrics as OULAD results.** Do not describe uncalibrated risk scores as confirmed 70% or 80% individual failure probabilities.

## Questions the teacher might ask

**Why Random Forest?** It handles nonlinear relationships across attendance-like activity and marks, works well on numerical tabular data, and allows relatively simple feature importance / perturbation-based explanations. It does not inherently provide calibrated probabilities.

**What is scikit-learn?** The Python package that trains and evaluates the Random Forest. **Pandas** loads, joins and transforms the tables. **FastAPI** supplies role-based web endpoints.

**What if grades are missing?** The OULAD converter fills unavailable early assessment fields with presentation-level median scores, or the overall median if necessary. This simplification may mask missingness patterns and affect model accuracy.

**Is attendance real?** No. The OULAD source contains virtual learning environment activity, not a physical attendance register. We label it a proxy.

**What does 50% risk mean?** A model score threshold for teacher prioritization, **not** a proven 50% probability of failing. Calibration and independent external validation would be needed before interpreting it probabilistically.

**Can the AI be biased?** Yes. OULAD is from a different institution and environment, and it may not generalize to TTPU. We deliberately exclude demographic columns from model inputs; that does not establish fairness by itself.

**Does the website actively update OULAD grades?** No. Teacher-created demo assignments are a separate sample workflow and do not rewrite historical OULAD predictions.

**Why only eight weeks?** It represents an early intervention checkpoint. Data from after the checkpoint is not allowed in the predictor features, to avoid predicting the past using future information.

**Could this be used at Turin today?** Not safely as-is. It needs authorized current data, a privacy/security review, real authentication, calibration and validation against local outcomes.

## Source credit

Kuzilek, J., Hlosta, M., and Zdrahal, Z., *Open University Learning Analytics dataset*, UCI Machine Learning Repository, DOI 10.24432/C5KK69 (CC BY 4.0).
