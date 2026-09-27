"""Reproducible baseline and boosted model pipelines."""

from typing import Literal

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from risk_ml.features.pipeline import build_preprocessor

ModelKind = Literal["logistic", "xgboost"]


def build_model(kind: ModelKind, seed: int = 20260928) -> Pipeline:
    """Return an unfitted, fully encapsulated model pipeline."""

    if kind == "logistic":
        estimator = LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=seed, solver="lbfgs"
        )
    elif kind == "xgboost":
        estimator = XGBClassifier(
            n_estimators=180,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=3,
            reg_lambda=2.0,
            eval_metric="logloss",
            random_state=seed,
            n_jobs=1,
        )
    else:
        raise ValueError(f"Unknown model kind: {kind}")
    return Pipeline([("preprocessor", build_preprocessor()), ("classifier", estimator)])
