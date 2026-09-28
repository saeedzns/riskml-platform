import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import numpy as np
import pytest

from risk_ml.data.contracts import RAW_FEATURES
from risk_ml.data.fixture import generate_fixture
from risk_ml.data.sources import FIXTURE_SOURCE, OFFICIAL_UCI_SOURCE
from risk_ml.data.training_data import CURATED_TRAINING_RELATION
from risk_ml.modeling import training
from risk_ml.modeling.evaluation import evaluate_probabilities
from risk_ml.modeling.training import load_artifact, train_model


def test_known_evaluation_values() -> None:
    metrics = evaluate_probabilities([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8])
    assert metrics["roc_auc"] == pytest.approx(0.75)
    assert metrics["confusion_matrix"] == [[2, 0], [1, 1]]
    assert metrics["threshold_tradeoffs"][1]["illustrative_cost"] == 5


@pytest.mark.parametrize("kind", ["logistic", "xgboost"])
def test_training_round_trip(kind: str, tmp_path: Path) -> None:
    result = train_model(
        generate_fixture(160),
        kind=kind,  # type: ignore[arg-type]
        artifact_dir=tmp_path,
        dataset_source=FIXTURE_SOURCE,
        dataset_relation="unit-test-memory",
    )
    loaded = load_artifact(result.artifact_path)
    probability = loaded["model"].predict_proba(result.test_features)[:, 1]
    assert probability.shape == (40,)
    assert np.all((probability >= 0) & (probability <= 1))
    assert set(loaded["features"]) == set(RAW_FEATURES)
    assert 0 <= result.metrics["average_precision"] <= 1


def test_mlflow_records_curated_dataset_lineage(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    mlflow = ModuleType("mlflow")
    mlflow.set_tracking_uri = Mock()  # type: ignore[attr-defined]
    mlflow.set_experiment = Mock()  # type: ignore[attr-defined]
    mlflow.log_params = Mock()  # type: ignore[attr-defined]
    mlflow.log_metrics = Mock()  # type: ignore[attr-defined]
    mlflow.log_artifact = Mock()  # type: ignore[attr-defined]
    mlflow.set_tags = Mock()  # type: ignore[attr-defined]

    class Run:
        def __enter__(self) -> None:
            return None

        def __exit__(self, *args: object) -> None:
            return None

    mlflow.start_run = Mock(return_value=Run())  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mlflow", mlflow)

    train_model(
        generate_fixture(80),
        kind="logistic",
        artifact_dir=tmp_path,
        tracking_uri="sqlite:///unused.db",
        dataset_source=OFFICIAL_UCI_SOURCE,
        dataset_relation=CURATED_TRAINING_RELATION,
    )

    mlflow.set_tags.assert_called_once_with(  # type: ignore[attr-defined]
        {
            "dataset_source": OFFICIAL_UCI_SOURCE,
            "dataset_relation": CURATED_TRAINING_RELATION,
            "code_version": "0.1.0",
        }
    )


def test_training_splits_before_model_fit(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    class RecordingModel:
        fit_rows = 0

        def fit(self, features, target):  # type: ignore[no-untyped-def]
            self.fit_rows = len(features)
            return self

        def predict_proba(self, features):  # type: ignore[no-untyped-def]
            return np.column_stack((np.full(len(features), 0.5), np.full(len(features), 0.5)))

    model = RecordingModel()
    monkeypatch.setattr(training, "build_model", lambda kind, seed: model)
    monkeypatch.setattr(training.joblib, "dump", lambda payload, path: Path(path).touch())

    result = train_model(
        generate_fixture(200),
        kind="logistic",
        artifact_dir=tmp_path,
        dataset_source=FIXTURE_SOURCE,
        dataset_relation="unit-test-memory",
    )

    assert model.fit_rows == 150
    assert len(result.test_features) == 50
