# Power BI report design

The report contains exactly three pages. It presents generated RiskML evidence without changing the
ML system or implying causal, production-performance, or live-monitoring conclusions.

## Page 1 — Credit Portfolio Overview

Purpose: describe the explicitly selected credit portfolio.

KPI cards:

- Applications: distinct count of `application_id`.
- Observed default rate: average of binary `defaulted`, formatted as a percentage.
- Average credit amount: average of `credit_amount`.
- Average duration: average of `duration_months`.

Charts:

- Default versus non-default count and share.
- Credit-amount distribution using stable, documented bins.
- Applications and observed default rate by `purpose`.
- Applications and observed default rate by `checking_status`.
- Application distribution by `age_band`.
- Credit amount versus duration, using aggregation or transparency to avoid overplotting.

Slicers: `purpose`, `checking_status`, `age_band`, `housing`, and `employment_duration`.

Display note: these are descriptive associations in the selected dataset. Do not imply that a field
causes default. SQL-derived analytical fields are for presentation only and are not model features.

## Page 2 — Model Performance

Purpose: compare fixed-split evaluation evidence for Logistic Regression and XGBoost.

KPI/comparison cards: `roc_auc`, `average_precision`, `brier_score`, and `f1`, with `model` shown in
the visual or used as the comparison category.

Charts:

- Clustered comparison of Logistic Regression versus XGBoost metrics.
- Small-multiple confusion matrices using `actual`, `predicted`, and `count`.
- Threshold versus `false_positive` and `false_negative` counts.
- `illustrative_cost` by threshold and model.

Display note: metrics come from the fixed verified evaluation split. They are not live or production
performance. Lower Brier score is better; the illustrative threshold cost is not a production policy.

## Page 3 — Monitoring & Drift

Purpose: present the generated offline drift report.

Visuals:

- Drift score by feature, grouped or filtered by `method` because PSI and total variation have
  different interpretations.
- Drifted versus not-drifted feature status.
- Feature/method table with `score`, `missingness_delta`, and `drifted`.
- Alert summary from `report_status` and the count of drifted features.

The verified simulated case should highlight `credit_amount` and `checking_status`.

Place this label prominently on the page:

> **OFFLINE SIMULATED DATA DRIFT — NOT CONCEPT DRIFT — NOT LIVE PRODUCTION TELEMETRY**

Do not combine scores from different methods into a single universal ranking, and retain the exported
`semantics` text in a tooltip or information panel.
