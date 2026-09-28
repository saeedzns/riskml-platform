from unittest.mock import MagicMock

import pandas as pd
import pandera.pandas as pa
import pytest

from risk_ml.data.contracts import RAW_FEATURES, TARGET
from risk_ml.data.fixture import generate_fixture
from risk_ml.data.sources import FIXTURE_SOURCE
from risk_ml.data.training_data import TRAINING_COLUMNS, load_curated_training_frame


def _mock_engine(monkeypatch, frame: pd.DataFrame) -> MagicMock:  # type: ignore[no-untyped-def]
    engine = MagicMock()
    connection = object()
    engine.connect.return_value.__enter__.return_value = connection
    monkeypatch.setattr(
        "risk_ml.data.training_data.pd.read_sql",
        lambda query, active_connection, params: frame.copy(),
    )
    return engine


def test_curated_loader_validates_and_selects_only_leakage_safe_columns(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    frame = generate_fixture(20).assign(
        amount_vs_purpose_avg=1.5,
        purpose_applications=20,
        amount_rank_within_purpose=1,
    )
    dataset = load_curated_training_frame(_mock_engine(monkeypatch, frame), FIXTURE_SOURCE)

    assert tuple(dataset.frame.columns) == TRAINING_COLUMNS
    assert tuple(dataset.frame.columns) == (*RAW_FEATURES, TARGET)
    assert dataset.source_name == FIXTURE_SOURCE


def test_curated_loader_rejects_invalid_training_contract(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    invalid = generate_fixture(10).drop(columns=[TARGET])
    with pytest.raises(pa.errors.SchemaError, match="target column is required"):
        load_curated_training_frame(_mock_engine(monkeypatch, invalid), FIXTURE_SOURCE)


def test_curated_loader_requires_explicit_nonempty_source() -> None:
    with pytest.raises(ValueError, match="source_name"):
        load_curated_training_frame(MagicMock(), "  ")
