import json
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import text

from risk_ml.analytics.dashboard import export_dashboard
from risk_ml.data.fixture import write_fixture
from risk_ml.data.ingestion import ingest_csv
from risk_ml.data.training_data import TRAINING_COLUMNS, load_curated_training_frame
from risk_ml.db.core import create_db_engine, execute_sql_file

pytestmark = pytest.mark.integration


def test_ingest_is_idempotent_and_transformation_works(tmp_path: Path) -> None:
    engine = create_db_engine()
    fixture = write_fixture(tmp_path / "fixture.csv", rows=40)
    source_name = "integration"
    assert ingest_csv(engine, fixture, source_name) == 40
    assert ingest_csv(engine, fixture, source_name) == 40
    execute_sql_file(engine, Path("sql/transformations/001_modeling_view.sql"))
    execute_sql_file(engine, Path("sql/transformations/001_modeling_view.sql"))
    with engine.connect() as connection:
        raw_count = connection.scalar(
            text("SELECT COUNT(*) FROM raw.credit_applications WHERE source_name=:source_name"),
            {"source_name": source_name},
        )
        curated = pd.read_sql(
            text(
                "SELECT * FROM curated.credit_modeling WHERE application_id IN "
                "(SELECT application_id FROM raw.credit_applications "
                "WHERE source_name=:source_name)"
            ),
            connection,
            params={"source_name": source_name},
        )
    training = load_curated_training_frame(engine, source_name)
    assert raw_count == 40
    assert len(curated) == 40
    assert curated["monthly_credit_burden"].notna().all()
    assert tuple(training.frame.columns) == TRAINING_COLUMNS
    assert len(training.frame) == 40


def test_dashboard_export_is_source_scoped_and_read_only(tmp_path: Path) -> None:
    engine = create_db_engine()
    source_name = "integration-dashboard"
    fixture = write_fixture(tmp_path / "dashboard-fixture.csv", rows=25, seed=123)
    assert ingest_csv(engine, fixture, source_name) == 25
    execute_sql_file(engine, Path("sql/transformations/001_modeling_view.sql"))

    metric_payload = {
        "roc_auc": 0.7,
        "average_precision": 0.5,
        "brier_score": 0.2,
        "precision": 0.4,
        "recall": 0.6,
        "f1": 0.48,
        "threshold": 0.5,
        "positive_rate": 0.3,
        "predicted_positive_rate": 0.4,
        "confusion_matrix": [[10, 3], [2, 5]],
        "threshold_tradeoffs": [
            {
                "threshold": threshold,
                "false_positive": 3,
                "false_negative": 2,
                "illustrative_cost": 13,
            }
            for threshold in (0.3, 0.5, 0.7)
        ],
    }
    metric_paths = {}
    for model in ("logistic", "xgboost"):
        metric_path = tmp_path / f"metrics-{model}.json"
        metric_path.write_text(json.dumps(metric_payload), encoding="utf-8")
        metric_paths[model] = metric_path
    drift_path = tmp_path / "drift.json"
    drift_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "drifted_features": [],
                "semantics": ("Univariate data drift only; this does not establish concept drift."),
                "feature_results": {
                    "credit_amount": {
                        "method": "psi",
                        "score": 0.01,
                        "missingness_delta": 0.0,
                        "drifted": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    snapshot_sql = text(
        "SELECT application_id::text, record_hash, source_row_id "
        "FROM raw.credit_applications WHERE source_name=:source_name ORDER BY source_row_id"
    )
    with engine.connect() as connection:
        before = [
            tuple(row) for row in connection.execute(snapshot_sql, {"source_name": source_name})
        ]
    output_dir = tmp_path / "dashboard-data"

    counts = export_dashboard(
        engine,
        source_name,
        output_dir,
        drift_path,
        metric_paths,
    )

    portfolio = pd.read_csv(output_dir / "portfolio.csv")
    with engine.connect() as connection:
        after = [
            tuple(row) for row in connection.execute(snapshot_sql, {"source_name": source_name})
        ]
        raw_count = connection.scalar(
            text("SELECT COUNT(*) FROM raw.credit_applications WHERE source_name=:source_name"),
            {"source_name": source_name},
        )
    assert raw_count == 25
    assert counts["portfolio"] == raw_count
    assert len(portfolio) == raw_count
    assert set(portfolio["source_name"]) == {source_name}
    assert portfolio["application_id"].is_unique
    assert before == after
