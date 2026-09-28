# Project completion report

## A. What was built

RiskML includes official UCI acquisition plus a seeded fixture, Pandera contracts, idempotent
PostgreSQL ingestion, Alembic schemas, advanced SQL transformations/quality checks, shared sklearn
preprocessing, logistic and balanced XGBoost models, metric/plot generation, SQLite-backed local
MLflow tracking, SHAP explanations, bounded FastAPI single/batch scoring, reference/drift profiling,
an Airflow DAG over reusable steps, non-root container definitions, Compose, GitHub CI/deployment
workflows, and Azure Container Apps/PostgreSQL/Storage/Log Analytics Bicep and runbooks.

## B. Verified commands

- `python -m ruff format --check .` — passed, 68 files.
- `python -m ruff check .` — passed.
- `python -m mypy` — passed, 28 source files.
- `python -m pytest -m "not integration" --cov --cov-report=term-missing` — passed with the skips below.
- Targeted curated-loader, CLI, orchestration, modeling, and API tests — 18 passed.
- `python -m pip_audit --local --skip-editable` — passed; no known vulnerabilities.
- `docker compose --profile tools config --quiet` — passed; rendered CLI mounts were also asserted.
- Python YAML parsing over both workflow files — passed.

Earlier generated UCI metrics and HTTP smoke evidence remain valid for the unchanged model/API
behavior. The new database-backed training path, PostgreSQL integration test, image builds, and
full-stack smoke could not complete after the local Docker daemon disappeared; they are not reported
as passing. The explicit native integration-test attempt also confirmed Application Control blocks
`psycopg_binary.pq`. Exact recovery actions are in `BLOCKERS.md` and the local runbook.

## C. Test results

Final local run: 38 tests collected; 36 passed, 1 skipped because Airflow 3.3 requires POSIX rather
than native Windows, and 1 PostgreSQL integration test was deselected because the Docker/database
runtime became unavailable. Coverage was 90.29% with branch measurement and a 75% enforced floor.

## D. Model results

Dataset: official UCI Statlog German Credit, 1,000 rows, 30% adverse target. Split: seeded stratified
750 train / 250 test. Logistic: ROC-AUC 0.749562, average precision 0.551498, Brier 0.199420, F1
0.497110. Balanced XGBoost: ROC-AUC 0.735314, average precision 0.543204, Brier 0.197525, F1 0.526946.
These generated metrics predate the database-loader repair and were not regenerated during this run;
the selected feature contract and split code are unchanged. The single small historical split is not
production evidence; see `docs/evaluation-report.md`.

## E. SQL evidence

- `alembic/versions/20260928_0001_initial.py`: schemas, keys, constraints, indexes.
- `sql/transformations/001_modeling_view.sql`: CTEs, grouping, join, window functions, `CASE`,
  correlated `EXISTS`, ratios, and `NULLIF`.
- `sql/features/portfolio_summary.sql`: multi-column aggregation, target counts/rates, ordered-set median.
- `sql/quality/credit_applications.sql`: zero-row target, duplicate, and numeric-domain assertions.
- `sql/ddl/explain_modeling_query.sql`: reproducible planner/index investigation.

## F. Deployment status

**Azure-ready but not deployed.** No Azure credentials, approved subscription/region/budget, globally
unique naming context, or final private-network design was available. The minimum owner action and
validation/deployment commands are in `BLOCKERS.md` and `docs/runbooks/azure-deployment.md`.

## G. Known limitations

Reported CI run #2 passed quality, PostgreSQL integration, and the dedicated Linux Airflow DAG job,
and the API build passed its earlier artifact-copy failure. The current database-backed training and
CLI-container repair awaits new CI and clean-room acceptance. Native Windows clean-room execution is
blocked by Application Control for a compiled scikit-learn extension; the supported workaround is the
Linux container path, not weaker security. The source has no reliable time axis, so the split is not
temporal. Fairness, lending compliance, external validation, authenticated API ingress, a production
feature store, and live concept/performance monitoring are deliberately out of scope.

## H. Portfolio talking points

- Built a SQL-first data layer with repeatable migrations, idempotent upserts, constraints, windows,
  aggregations, data-quality assertions, and documented index reasoning.
- Prevented leakage by splitting before fitting and sharing one serialized feature/model pipeline
  across training and serving.
- Compared a class-weighted linear baseline with balanced XGBoost using ROC-AUC, PR-AUC, Brier,
  threshold costs, and confusion matrices rather than accuracy alone.
- Logged reproducible MLflow runs with parameters, metrics, dataset/code tags, plots, and artifacts.
- Served strict, bounded single/batch predictions and SHAP explanations with distinct health/readiness.
- Tested deterministic no-drift and controlled-drift scenarios with transparent PSI/TV thresholds.
- Repaired an audit finding by moving the orchestration/runtime stack to patched dependency versions.
- Prepared cost-conscious Azure Container Apps infrastructure and OIDC deployment without claiming an
  unperformed cloud deployment.

## I. Resume skill line

Python 3.12, SQL, PostgreSQL, pandas, NumPy, Pandera, scikit-learn, XGBoost, MLflow, SHAP, FastAPI,
Pydantic, Airflow, Alembic, pytest, Ruff, mypy, Docker Compose, GitHub Actions, Azure Bicep.

