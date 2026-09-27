"""Dataframe contracts and leakage controls."""

from collections.abc import Sequence

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

TARGET = "defaulted"
IDENTIFIERS = ("application_id",)
RAW_FEATURES = (
    "age",
    "credit_amount",
    "duration_months",
    "installment_rate",
    "existing_credits",
    "dependents",
    "checking_status",
    "credit_history",
    "purpose",
    "savings_status",
    "employment_duration",
    "housing",
    "foreign_worker",
)
CATEGORICAL_FEATURES = (
    "checking_status",
    "credit_history",
    "purpose",
    "savings_status",
    "employment_duration",
    "housing",
    "foreign_worker",
)
NUMERIC_FEATURES = tuple(name for name in RAW_FEATURES if name not in CATEGORICAL_FEATURES)

APPLICATION_SCHEMA = DataFrameSchema(
    {
        "age": Column(int, Check.in_range(18, 100), nullable=False, coerce=True),
        "credit_amount": Column(float, Check.greater_than(0), nullable=False, coerce=True),
        "duration_months": Column(int, Check.in_range(1, 120), nullable=False, coerce=True),
        "installment_rate": Column(int, Check.isin([1, 2, 3, 4]), coerce=True),
        "existing_credits": Column(int, Check.in_range(1, 4), coerce=True),
        "dependents": Column(int, Check.isin([1, 2]), coerce=True),
        "checking_status": Column(str, Check.isin(["none", "negative", "low", "high"])),
        "credit_history": Column(
            str, Check.isin(["critical", "delayed", "existing_paid", "all_paid", "no_credits"])
        ),
        "purpose": Column(str, Check.isin(["car", "furniture", "education", "business", "other"])),
        "savings_status": Column(str, Check.isin(["unknown", "low", "medium", "high"])),
        "employment_duration": Column(str, Check.isin(["unemployed", "short", "medium", "long"])),
        "housing": Column(str, Check.isin(["rent", "own", "free"])),
        "foreign_worker": Column(bool, coerce=True),
        TARGET: Column(int, Check.isin([0, 1]), required=False, coerce=True),
    },
    strict="filter",
    unique_column_names=True,
)


def validate_applications(frame: pd.DataFrame, *, require_target: bool = True) -> pd.DataFrame:
    """Validate raw feature types/domains and optional target presence."""

    if require_target and TARGET not in frame:
        raise pa.errors.SchemaError(  # type: ignore[no-untyped-call]
            APPLICATION_SCHEMA, frame, "target column is required"
        )
    return APPLICATION_SCHEMA.validate(frame, lazy=True)


def assert_no_leakage(feature_names: Sequence[str]) -> None:
    """Reject direct target/identifier and common post-outcome leakage fields."""

    forbidden = {TARGET, *IDENTIFIERS, "repayment_status", "loss_amount", "collection_status"}
    leaked = forbidden.intersection(feature_names)
    if leaked:
        raise ValueError(f"Leakage columns are forbidden: {sorted(leaked)}")
