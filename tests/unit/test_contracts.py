import pandas as pd
import pandera.pandas as pa
import pytest

from risk_ml.data.contracts import RAW_FEATURES, assert_no_leakage, validate_applications
from risk_ml.data.fixture import generate_fixture


def test_clean_fixture_passes_contract() -> None:
    clean = validate_applications(generate_fixture(20))
    assert len(clean) == 20


@pytest.mark.parametrize(
    ("column", "value"),
    [("age", 12), ("credit_amount", 0), ("purpose", "casino"), ("defaulted", 2)],
)
def test_bad_values_fail_contract(column: str, value: object) -> None:
    frame = generate_fixture(10)
    frame.loc[0, column] = value
    with pytest.raises(pa.errors.SchemaErrors):
        validate_applications(frame)


def test_target_is_not_a_feature() -> None:
    assert "defaulted" not in RAW_FEATURES
    with pytest.raises(ValueError, match="Leakage"):
        assert_no_leakage([*RAW_FEATURES, "defaulted"])


def test_duplicate_columns_are_rejected() -> None:
    frame = generate_fixture(5)
    duplicated = pd.concat([frame, frame[["age"]]], axis=1)
    with pytest.raises(pa.errors.SchemaErrors):
        validate_applications(duplicated)
