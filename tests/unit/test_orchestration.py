from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from risk_ml.data.fixture import generate_fixture, write_fixture
from risk_ml.data.sources import FIXTURE_SOURCE
from risk_ml.data.training_data import CuratedTrainingFrame
from risk_ml.orchestration import ingest_step, monitoring_step, train_step, validate_step


def test_local_non_database_orchestration_steps(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.chdir(tmp_path)
    assert Path(monitoring_step()).exists()


def test_ingest_step_labels_fixture_lineage(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    fixture = write_fixture(tmp_path / "fixture.csv", 20)
    engine = object()
    ingest = Mock(return_value=20)
    monkeypatch.setattr("risk_ml.orchestration.FIXTURE", fixture)
    monkeypatch.setattr("risk_ml.orchestration.create_db_engine", lambda: engine)
    monkeypatch.setattr("risk_ml.orchestration.ingest_csv", ingest)

    assert ingest_step() == 20
    ingest.assert_called_once_with(engine, fixture, FIXTURE_SOURCE)


def test_validation_and_training_use_curated_database_frame(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    engine = object()
    dataset = CuratedTrainingFrame(generate_fixture(24), FIXTURE_SOURCE)
    loader = Mock(return_value=dataset)
    trainer = Mock(return_value=SimpleNamespace(artifact_path=tmp_path / "xgboost.joblib"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("risk_ml.orchestration.create_db_engine", lambda: engine)
    monkeypatch.setattr("risk_ml.orchestration.load_curated_training_frame", loader)
    monkeypatch.setattr("risk_ml.orchestration.train_model", trainer)

    assert validate_step() == 24
    assert train_step() == str(tmp_path / "xgboost.joblib")
    assert loader.call_args_list == [
        ((engine, FIXTURE_SOURCE),),
        ((engine, FIXTURE_SOURCE),),
    ]
    assert trainer.call_args.args == (dataset.frame,)
    assert trainer.call_args.kwargs["dataset_source"] == FIXTURE_SOURCE
    assert trainer.call_args.kwargs["dataset_relation"] == dataset.relation
