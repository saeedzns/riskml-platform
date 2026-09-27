import numpy as np

from risk_ml.data.contracts import RAW_FEATURES
from risk_ml.data.fixture import generate_fixture
from risk_ml.features.pipeline import build_preprocessor


def test_transform_is_deterministic_and_traceable() -> None:
    features = generate_fixture(30).loc[:, RAW_FEATURES]
    transformer = build_preprocessor().fit(features)
    first = transformer.transform(features)
    second = transformer.transform(features)
    np.testing.assert_array_equal(first, second)
    names = transformer.get_feature_names_out().tolist()
    assert len(names) == first.shape[1]
    assert any("checking_status" in name for name in names)


def test_unseen_category_does_not_break_serving() -> None:
    train = generate_fixture(30).loc[:, RAW_FEATURES]
    inference = train.iloc[[0]].copy()
    inference.loc[:, "purpose"] = "unseen-but-schema-valid-only-at-service-boundary"
    transformer = build_preprocessor().fit(train)
    assert transformer.transform(inference).shape[0] == 1
