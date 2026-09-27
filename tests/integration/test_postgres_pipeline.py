from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import text

from risk_ml.data.fixture import write_fixture
from risk_ml.data.ingestion import ingest_csv
from risk_ml.db.core import create_db_engine, execute_sql_file

pytestmark = pytest.mark.integration


def test_ingest_is_idempotent_and_transformation_works(tmp_path: Path) -> None:
    engine = create_db_engine()
    fixture = write_fixture(tmp_path / "fixture.csv", rows=40)
    assert ingest_csv(engine, fixture, "integration") == 40
    assert ingest_csv(engine, fixture, "integration") == 40
    execute_sql_file(engine, Path("sql/transformations/001_modeling_view.sql"))
    with engine.connect() as connection:
        raw_count = connection.scalar(
            text("SELECT COUNT(*) FROM raw.credit_applications WHERE source_name='integration'")
        )
        curated = pd.read_sql(
            text(
                "SELECT * FROM curated.credit_modeling WHERE application_id IN "
                "(SELECT application_id FROM raw.credit_applications "
                "WHERE source_name='integration')"
            ),
            connection,
        )
    assert raw_count == 40
    assert len(curated) == 40
    assert curated["monthly_credit_burden"].notna().all()
