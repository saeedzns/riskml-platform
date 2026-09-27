# ADR 0003: PostgreSQL, scikit-learn/XGBoost, MLflow, and Airflow

- Status: Accepted
- Date: 2026-09-28

## Context

The implementation needs meaningful SQL, a transparent baseline and boosted comparator, local
experiment tracking, and visible orchestration using stable mainstream tools.

## Decision

Use PostgreSQL 16 with Alembic; scikit-learn pipelines for preprocessing and logistic regression;
XGBoost for nonlinear boosting; MLflow with a local SQLite backend; and Airflow for DAG
orchestration. SHAP supplies model-behavior explanations.

## Consequences

The stack is familiar and testable but dependency-heavy. Airflow is isolated in its Compose image;
core unit tests do not require it. XGBoost and SHAP compatibility is pinned by bounded versions.

