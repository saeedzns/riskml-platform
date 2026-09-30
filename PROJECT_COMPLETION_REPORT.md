# Project completion report

## A. What was built

RiskML includes official UCI acquisition plus a seeded fixture, Pandera contracts, idempotent
PostgreSQL ingestion, Alembic schemas, advanced SQL transformations/quality checks, shared sklearn
preprocessing, logistic and balanced XGBoost models, metric/plot generation, SQLite-backed local
MLflow tracking, SHAP explanations, bounded FastAPI single/batch scoring, reference/drift profiling,
an Airflow DAG over reusable steps, non-root container definitions, Compose, GitHub CI/deployment
workflows, reproducible Power BI presentation exports, and Azure Container
Apps/PostgreSQL/Storage/Log Analytics Bicep and runbooks.

## B. Verified commands

- `python -m ruff format --check .` — passed, 74 files.
- `python -m ruff check .` — passed.
- `python -m mypy` — passed, 30 source files.
- `python -m pytest -m "not integration" --cov --cov-report=term-missing` — passed with the skips below.
- `python -m pytest -m integration` — 2 PostgreSQL integration tests passed.
- `python -m pip_audit --local --skip-editable` — passed; no known vulnerabilities.
- `docker compose --profile tools config --quiet` — passed; rendered CLI mounts were also asserted.
- Python YAML parsing over both workflow files — passed.

Independent clean-room verification completed the official UCI, PostgreSQL, database-backed training,
MLflow artifact-proxy, read-only API, SHAP, drift, and Power BI export paths. GitHub Actions run #7
passed all jobs. Native Windows Application Control still blocks some compiled extensions, so Linux
Compose remains the supported full-stack path.

## C. Test results

Current analytics-layer run: 51 non-integration tests passed, 1 Airflow runtime test was skipped on
native Windows because it requires POSIX, and 2 integration tests were deselected. Branch-aware
coverage was 87.96% with a 75% enforced floor. Both PostgreSQL integration tests passed separately.

## D. Model results

Dataset: official UCI Statlog German Credit, 1,000 rows, 30% adverse target. Split: seeded stratified
750 train / 250 test. Logistic: ROC-AUC 0.749562, average precision 0.551498, Brier 0.199420, F1
0.497110. Balanced XGBoost: ROC-AUC 0.741257, average precision 0.561384, Brier 0.194161, F1 0.524390.
Logistic has higher ROC-AUC; XGBoost has higher average precision/F1 and lower Brier score and is the
explanation-capable champion artifact used by the API. The single small historical split is not
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

GitHub Actions run #7 and independent clean-room execution verified the accepted local/containerized
portfolio path. Native Windows clean-room execution remains blocked by Application Control for a
compiled scikit-learn extension; the supported route is Linux Compose, not weaker security. The source
has no reliable time axis, so the split is not temporal. Fairness, lending compliance, external
validation, authenticated API ingress, a production feature store, and live concept/performance
monitoring are deliberately out of scope.

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
Pydantic, Airflow, Alembic, pytest, Ruff, mypy, Docker Compose, GitHub Actions, Power BI, DAX, Power
Query, Azure Bicep.

