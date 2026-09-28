"""Validated idempotent PostgreSQL ingestion."""

import hashlib
import json
import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from risk_ml.data.contracts import validate_applications

INSERT = text(
    """
    INSERT INTO raw.credit_applications (
        application_id, source_name, source_row_id, record_hash, age, credit_amount,
        duration_months, installment_rate, existing_credits, dependents, checking_status,
        credit_history, purpose, savings_status, employment_duration, housing, foreign_worker,
        defaulted
    ) VALUES (
        :application_id, :source_name, :source_row_id, :record_hash, :age, :credit_amount,
        :duration_months, :installment_rate, :existing_credits, :dependents, :checking_status,
        :credit_history, :purpose, :savings_status, :employment_duration, :housing,
        :foreign_worker, :defaulted
    )
    ON CONFLICT (source_name, source_row_id) DO UPDATE SET
        record_hash = EXCLUDED.record_hash,
        age = EXCLUDED.age,
        credit_amount = EXCLUDED.credit_amount,
        duration_months = EXCLUDED.duration_months,
        installment_rate = EXCLUDED.installment_rate,
        existing_credits = EXCLUDED.existing_credits,
        dependents = EXCLUDED.dependents,
        checking_status = EXCLUDED.checking_status,
        credit_history = EXCLUDED.credit_history,
        purpose = EXCLUDED.purpose,
        savings_status = EXCLUDED.savings_status,
        employment_duration = EXCLUDED.employment_duration,
        housing = EXCLUDED.housing,
        foreign_worker = EXCLUDED.foreign_worker,
        defaulted = EXCLUDED.defaulted,
        ingested_at = now()
    """
)


def ingest_csv(engine: Engine, path: Path, source_name: str) -> int:
    """Validate and upsert a CSV using a stable source business key."""

    normalized_source = source_name.strip()
    if not normalized_source:
        raise ValueError("source_name must be explicit and non-empty")
    frame = validate_applications(pd.read_csv(path))
    records: list[dict[str, object]] = []
    namespace = uuid.UUID("a6e8ce78-55ca-4731-8828-05a69d1ae947")
    for row_id, row in enumerate(frame.to_dict(orient="records")):
        canonical = json.dumps(row, sort_keys=True, default=str)
        records.append(
            {
                **row,
                "application_id": uuid.uuid5(namespace, f"{normalized_source}:{row_id}"),
                "source_name": normalized_source,
                "source_row_id": row_id,
                "record_hash": hashlib.sha256(canonical.encode()).hexdigest(),
            }
        )
    with engine.begin() as connection:
        connection.execute(INSERT, records)
    return len(records)
