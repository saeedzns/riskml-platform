# Power BI dashboard exports

This directory defines a reproducible presentation layer over RiskML's verified outputs. It does not
participate in model training, feature selection, serving, orchestration, or promotion. Power BI reads
the generated CSV files; the canonical ML feature contract remains unchanged.

## Generate the datasets

Run migrations, ingestion, transformation, training, and the offline simulated drift command first.
Then run through the read-only CLI container:

```bash
docker compose run --rm cli risk-ml export-dashboard \
  --source uci-statlog-german-credit-144 \
  --output-dir dashboard/data \
  --drift-report artifacts/drift-shifted.json \
  --metrics-dir artifacts
```

An editable native installation can run the same command without the `docker compose run --rm cli`
prefix. Compose exposes only the dedicated `dashboard/data` output mount; it does not make the CLI
root filesystem writable.

The command requires the explicit PostgreSQL source and both generated metric files
(`metrics-logistic.json` and `metrics-xgboost.json`). It fails rather than substituting synthetic data
or invented metrics. `dashboard/data/*.csv` is generated evidence and is intentionally gitignored.

## Tables and grain

### `portfolio.csv`

Grain: one row per credit application from the requested `source_name` in
`curated.credit_modeling`, ordered by `source_row_id`.

| Field | Meaning |
| --- | --- |
| `application_id` | Stable unique application identifier |
| `source_name`, `source_row_id` | Explicit dataset lineage and source row key |
| `age`, `age_band` | Applicant age and SQL-derived display band |
| `credit_amount`, `duration_months` | Credit principal and duration |
| `installment_rate`, `existing_credits`, `dependents` | Numeric application attributes |
| `checking_status`, `credit_history`, `purpose` | Credit/application categories |
| `savings_status`, `employment_duration`, `housing`, `foreign_worker` | Applicant categories |
| `monthly_credit_burden` | SQL-derived amount divided by duration |
| `amount_vs_purpose_avg` | SQL-derived amount relative to the purpose average |
| `purpose_applications` | SQL-derived portfolio count for the purpose |
| `amount_rank_within_purpose` | SQL-derived amount rank within purpose |
| `defaulted` | Observed binary target (`0` or `1`) |

`age_band`, `monthly_credit_burden`, `amount_vs_purpose_avg`, `purpose_applications`, and
`amount_rank_within_purpose` are analytical fields. The global aggregate/rank fields are deliberately
excluded from model training and must not be fed back into the canonical feature pipeline.

### `model_metrics.csv`

Grain: one row per generated model evidence file. Fields are `model`, `roc_auc`,
`average_precision`, `brier_score`, `precision`, `recall`, `f1`, `threshold`, `positive_rate`, and
`predicted_positive_rate`. Values come from executable evaluation evidence, not dashboard constants.

### `threshold_tradeoffs.csv`

Grain: one row per model and evaluated threshold. Fields are `model`, `threshold`,
`false_positive`, `false_negative`, and `illustrative_cost`. The current evaluator emits thresholds
0.3, 0.5, and 0.7. Cost is illustrative rather than a validated business loss estimate.

### `confusion_matrix.csv`

Grain: one matrix cell per model, actual class, and predicted class. Fields are `model`, `actual`,
`predicted`, and `count`. `actual` identifies the matrix row and `predicted` identifies the matrix
column, so false-positive and false-negative axes are unambiguous.

### `drift_features.csv`

Grain: one feature result from the selected generated drift report. Fields are `feature`, `method`,
`score`, `missingness_delta`, `drifted`, `report_status`, and `semantics`. This is offline univariate
data-drift evidence. It is not concept-drift detection and is not live production telemetry.

## Recommended relationships

- `model_metrics[model]` one-to-many to `threshold_tradeoffs[model]`.
- `model_metrics[model]` one-to-many to `confusion_matrix[model]`.
- Keep `portfolio` disconnected from model evaluation tables: evaluation rows summarize a fixed test
  split and are not application-level predictions.
- Keep `drift_features` disconnected unless a future governed feature dimension is introduced.

Use single-direction filtering from `model_metrics` to its two child tables. Do not create a
relationship that implies model metrics or drift scores were observed for individual portfolio rows.
