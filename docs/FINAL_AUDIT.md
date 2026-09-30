# Final adversarial audit

Date: 2026-09-30

## Architecture and scope

The modular monolith is appropriate: CLI, Airflow, and API reuse importable application functions;
PostgreSQL, MLflow, and Airflow are external only where they add demonstrable behavior. No additional
microservice, Spark, Kubernetes, or notebook layer is present. Boundaries and recovery paths are
documented. Residual complexity is dependency weight, especially Airflow/MLflow/SHAP.

## Data, SQL, and ML review

- Official UCI acquisition and deterministic offline fixtures both validate through the same contract.
- CLI and Airflow training now load an explicit source from `curated.credit_modeling` through the same
  parameterized adapter; neither canonical path rereads a CSV for training.
- The fixed split occurs before learned imputation, scaling, encoding, class weighting, or fitting.
- Target, identifiers, and named post-outcome fields are rejected. A target-derived purpose aggregate
  discovered during review was removed from the curated modeling view. Remaining whole-dataset SQL
  analytics are explicitly excluded from the model feature vector.
- SQL visibly uses constraints, indexes, CTEs, grouping, joins, conditional expressions, a subquery,
  null-safe ratios, and window functions. Query-plan commands are present for reproducible planner
  and index investigation.
- Ranking, imbalance, calibration-sensitive, confusion-matrix, and threshold-cost metrics are generated.
  Logistic has higher ROC-AUC; XGBoost has higher average precision/F1 and lower Brier score in the
  fixed evaluation. Documentation states these tradeoffs without calling either model the winner.
- Training and serving load the same complete pipeline envelope. Representative round-trip and unseen
  category tests protect against transformation skew.

## Production and security review

- API batch size is bounded, payload fields are strict, CORS is not enabled, debug mode is absent,
  request bodies are not logged, and liveness/readiness are distinct.
- Model files are operator-controlled trusted inputs; documentation warns that joblib/pickle is unsafe
  for untrusted artifacts. No upload/path traversal interface exists.
- SQL writes are parameterized; repository SQL files are trusted static inputs. PostgreSQL is bound to
  loopback in Compose and cloud public database access is disabled.
- API and MLflow images use non-root users; the API filesystem is read-only with `no-new-privileges`.
- Secret/private-key and machine-path scans returned no matches in project source. `.env`, raw data,
  models, MLflow state, SQLite databases, caches, and runtime logs are ignored. No file intended for
  commit exceeded 1 MB.
- `pip-audit --local --skip-editable` initially found vulnerable Airflow 3.1.8, pytest, and Starlette
  versions. Dependencies and images were upgraded to Airflow 3.3.2, pytest 9.1.1, FastAPI 0.136.3, and
  Starlette 1.7.0; the repeated audit reported no known vulnerabilities.
- Dataset DOI/license attribution and an MIT project license are present.

## Verification evidence

- Ruff format: 74 files checked, pass.
- Ruff lint: pass.
- mypy strict package check: 30 source files, pass.
- pytest: 51 non-integration tests passed, 1 native-Windows Airflow runtime import skipped, and 2
  integration tests deselected; 87.96% branch-aware coverage. Both PostgreSQL integration tests passed
  in the dedicated run.
- Official UCI training: both models completed; MLflow contained expected metrics and model/evaluation
  artifacts, including generated ROC, precision-recall, and calibration plots.
- SHAP local explanation: executed through API contract test.
- Real loopback HTTP smoke: `/health` and `/api/v1/predict` returned 200 on the final dependency stack.
- Stable and deliberately shifted monitoring scenarios: pass; the shift alerts on exactly the intended
  credit amount and checking-status changes among the asserted features.
- Workflow YAML: two files parsed locally. Compose configuration including the `tools` profile: valid;
  CLI writable data/artifact mounts, read-only SQL mount, and read-only root were asserted.
- Dependency audit: no known vulnerabilities after repair.
- Dashboard export: 1,000 portfolio rows, 2 model-metric rows, 6 threshold-tradeoff rows, 8
  confusion-matrix cells, and 13 drift-feature rows; Power BI remains presentation-only.
- Independent clean-room reproduction and GitHub Actions run #7: passed.

## Residual limitations

The accepted local/containerized path is independently verified. Native Windows clean-room execution
is blocked by Application Control for a compiled scikit-learn extension; the native PostgreSQL test
also confirmed a blocked `psycopg_binary.pq` extension. The documented Linux CLI container is the
supported path. Azure is designed but not deployed, and
Bicep `what-if` awaits Azure CLI/auth/subscription/network decisions. The dataset is old/small; there
is no temporal/external validation, fairness analysis, production telemetry backend, delayed-label
loop, or business-validated threshold cost. Resume actions are in `BLOCKERS.md`.

