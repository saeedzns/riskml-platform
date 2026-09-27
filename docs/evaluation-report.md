# Verified evaluation report

Generated from the 2026-09-28 local pipeline run on the official UCI Statlog German Credit dataset.
The source has 1,000 rows and a 30% adverse-class rate. A fixed seed (`20260928`) creates a stratified
750-row training set and 250-row test set. Preprocessing is fitted only on training rows.

| Metric | Logistic regression | Balanced XGBoost |
|---|---:|---:|
| ROC-AUC | 0.749562 | 0.735314 |
| Average precision | 0.551498 | 0.543204 |
| Brier score (lower is better) | 0.199420 | 0.197525 |
| Precision at 0.5 | 0.438776 | 0.478261 |
| Recall at 0.5 | 0.573333 | 0.586667 |
| F1 at 0.5 | 0.497110 | 0.526946 |

At threshold 0.5, the logistic confusion matrix is `[[120, 55], [32, 43]]`; XGBoost is
`[[127, 48], [31, 44]]`. With the explicitly illustrative cost `FP + 5 × FN`, XGBoost costs are 146,
203, and 276 at thresholds 0.3, 0.5, and 0.7. These weights are not validated business economics and
are included to make threshold consequences visible.

Logistic regression has stronger ranking metrics; XGBoost has slightly better Brier/F1/recall in this
single split. Neither result establishes generalization. No hyperparameter tuning used the held-out
test set. The model is not calibrated post hoc because the dataset is small; Brier score is reported
as calibration-sensitive evidence, and a future production candidate would require nested or
out-of-fold calibration plus temporal/external validation.

Exact machine-readable metrics are generated at `artifacts/metrics-logistic.json` and
`artifacts/metrics-xgboost.json` and logged to MLflow. Generated artifacts are deliberately ignored
rather than committed as model state.

