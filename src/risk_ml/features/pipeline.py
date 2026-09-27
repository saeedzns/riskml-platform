"""Leakage-safe learned preprocessing shared by every model."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from risk_ml.data.contracts import CATEGORICAL_FEATURES, NUMERIC_FEATURES, assert_no_leakage


def build_preprocessor() -> ColumnTransformer:
    """Construct an unfitted transformer; callers must fit on training data only."""

    features = [*NUMERIC_FEATURES, *CATEGORICAL_FEATURES]
    assert_no_leakage(features)
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, list(NUMERIC_FEATURES)),
            ("categorical", categorical, list(CATEGORICAL_FEATURES)),
        ],
        verbose_feature_names_out=True,
    )
