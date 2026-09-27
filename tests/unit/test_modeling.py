from pathlib import Path

import numpy as np
import pytest

from risk_ml.data.contracts import RAW_FEATURES
from risk_ml.data.fixture import generate_fixture
from risk_ml.modeling.evaluation import evaluate_probabilities
from risk_ml.modeling.training import load_artifact, train_model


def test_known_evaluation_values() -> None:
    metrics = evaluate_probabilities([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])
    assert metrics["roc_auc"] == pytest.approx(0.75)
    assert metrics["confusion_matrix"] == [[2, 0], [1, 1]]
    assert metrics["threshold_tradeoffs"][1]["illustrative_cost"] == 5


@pytest.mark.parametrize("kind", ["logistic", "xgboost"])
def test_training_round_trip(kind: str, tmp_path: Path) -> None:
    result = train_model(generate_fixture(160), kind=kind, artifact_dir=tmp_path)  # type: ignore[arg-type]
    loaded = load_artifact(result.artifact_path)
    probability = loaded["model"].predict_proba(result.test_features)[:, 1]
    assert probability.shape == (40,)
    assert np.all((probability >= 0) & (probability <= 1))
    assert set(loaded["features"]) == set(RAW_FEATURES)
    assert 0 <= result.metrics["average_precision"] <= 1
