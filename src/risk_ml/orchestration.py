"""Idempotent coarse-grained pipeline steps shared with Airflow."""

from pathlib import Path

import pandas as pd

from risk_ml.config import get_settings
from risk_ml.data.contracts import validate_applications
from risk_ml.data.fixture import generate_fixture, write_fixture
from risk_ml.data.ingestion import ingest_csv
from risk_ml.db.core import create_db_engine, execute_sql_file
from risk_ml.modeling.training import train_model
from risk_ml.monitoring.drift import drift_report, write_report

FIXTURE = Path("data/processed/credit_fixture.csv")


def ingest_step() -> int:
    if not FIXTURE.exists():
        write_fixture(FIXTURE, seed=get_settings().random_seed)
    return ingest_csv(create_db_engine(), FIXTURE)


def validate_step() -> int:
    return len(validate_applications(pd.read_csv(FIXTURE)))


def transform_step() -> None:
    execute_sql_file(create_db_engine(), Path("sql/transformations/001_modeling_view.sql"))


def train_step() -> str:
    settings = get_settings()
    result = train_model(
        pd.read_csv(FIXTURE),
        kind="xgboost",
        artifact_dir=Path("artifacts"),
        seed=settings.random_seed,
        tracking_uri=settings.mlflow_tracking_uri,
        experiment=settings.mlflow_experiment,
    )
    return str(result.artifact_path)


def monitoring_step() -> str:
    settings = get_settings()
    reference = generate_fixture(600, settings.random_seed)
    current = generate_fixture(600, settings.random_seed + 1)
    return str(write_report(drift_report(reference, current), Path("artifacts/drift-report.json")))
