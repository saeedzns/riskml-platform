"""RiskML daily retraining pipeline; business logic remains in the application package."""

from datetime import datetime, timedelta

from airflow.providers.standard.operators.python import PythonOperator

from airflow import DAG
from risk_ml.orchestration import (
    ingest_step,
    monitoring_step,
    train_step,
    transform_step,
    validate_step,
)

DEFAULT_ARGS = {"owner": "risk-ml", "retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="risk_ml_training_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@weekly",
    catchup=False,
    default_args=DEFAULT_ARGS,
    dagrun_timeout=timedelta(hours=2),
    tags=["risk", "ml"],
) as dag:
    ingest = PythonOperator(task_id="ingest", python_callable=ingest_step)
    validate = PythonOperator(task_id="validate", python_callable=validate_step)
    transform = PythonOperator(task_id="transform", python_callable=transform_step)
    train = PythonOperator(task_id="train_evaluate_register", python_callable=train_step)
    monitor = PythonOperator(task_id="monitoring_baseline", python_callable=monitoring_step)
    ingest >> validate >> transform >> train >> monitor
