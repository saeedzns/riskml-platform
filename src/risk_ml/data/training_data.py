"""Database-backed access to the leakage-safe curated training contract."""

from dataclasses import dataclass

import pandas as pd
from sqlalchemy import Engine, text

from risk_ml.data.contracts import RAW_FEATURES, TARGET, assert_no_leakage, validate_applications

CURATED_TRAINING_RELATION = "curated.credit_modeling"
TRAINING_COLUMNS = (*RAW_FEATURES, TARGET)
SELECT_TRAINING_FRAME = text(
    """
    SELECT
        age, credit_amount, duration_months, installment_rate, existing_credits, dependents,
        checking_status, credit_history, purpose, savings_status, employment_duration, housing,
        foreign_worker, defaulted
    FROM curated.credit_modeling
    WHERE source_name = :source_name
    ORDER BY source_row_id
    """
)


@dataclass(frozen=True)
class CuratedTrainingFrame:
    """Validated model frame plus its database lineage."""

    frame: pd.DataFrame
    source_name: str
    relation: str = CURATED_TRAINING_RELATION


def load_curated_training_frame(engine: Engine, source_name: str) -> CuratedTrainingFrame:
    """Load one explicitly identified source from the curated PostgreSQL relation."""

    normalized_source = source_name.strip()
    if not normalized_source:
        raise ValueError("source_name must be explicit and non-empty")
    with engine.connect() as connection:
        frame = pd.read_sql(
            SELECT_TRAINING_FRAME,
            connection,
            params={"source_name": normalized_source},
        )
    if frame.empty:
        raise ValueError(
            f"No rows found in {CURATED_TRAINING_RELATION} for source {normalized_source!r}"
        )
    clean = validate_applications(frame)
    assert_no_leakage(RAW_FEATURES)
    return CuratedTrainingFrame(clean.loc[:, TRAINING_COLUMNS], normalized_source)
