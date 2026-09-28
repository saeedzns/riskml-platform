import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from risk_ml.cli import main
from risk_ml.data.fixture import generate_fixture
from risk_ml.data.sources import OFFICIAL_UCI_SOURCE
from risk_ml.data.training_data import CURATED_TRAINING_RELATION, CuratedTrainingFrame


def test_fixture_command(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    output = tmp_path / "fixture.csv"
    monkeypatch.setattr(sys, "argv", ["risk-ml", "fixture", "--output", str(output)])
    main()
    assert output.exists()
    assert len(output.read_text(encoding="utf-8").splitlines()) == 601


def test_monitor_command(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["risk-ml", "monitor"])
    main()
    assert (tmp_path / "artifacts/drift-report.json").exists()


def test_ingest_command_forwards_explicit_uci_lineage(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    source = tmp_path / "uci.csv"
    source.write_text("unused", encoding="utf-8")
    engine = object()
    ingest = Mock(return_value=1000)
    monkeypatch.setattr("risk_ml.cli.create_db_engine", lambda: engine)
    monkeypatch.setattr("risk_ml.cli.ingest_csv", ingest)
    monkeypatch.setattr(
        sys,
        "argv",
        ["risk-ml", "ingest", "--input", str(source), "--source", OFFICIAL_UCI_SOURCE],
    )

    main()

    ingest.assert_called_once_with(engine, source, OFFICIAL_UCI_SOURCE)


def test_train_command_uses_curated_database_frame(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    engine = object()
    dataset = CuratedTrainingFrame(generate_fixture(40), OFFICIAL_UCI_SOURCE)
    loader = Mock(return_value=dataset)
    trainer = Mock(
        return_value=SimpleNamespace(
            metrics={"roc_auc": 0.5}, artifact_path=tmp_path / "model.joblib"
        )
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("risk_ml.cli.create_db_engine", lambda: engine)
    monkeypatch.setattr("risk_ml.cli.load_curated_training_frame", loader)
    monkeypatch.setattr("risk_ml.cli.train_model", trainer)
    monkeypatch.setattr(
        sys,
        "argv",
        ["risk-ml", "train", "--model", "logistic", "--source", OFFICIAL_UCI_SOURCE],
    )

    main()

    loader.assert_called_once_with(engine, OFFICIAL_UCI_SOURCE)
    assert trainer.call_args.args == (dataset.frame,)
    assert trainer.call_args.kwargs["dataset_source"] == OFFICIAL_UCI_SOURCE
    assert trainer.call_args.kwargs["dataset_relation"] == CURATED_TRAINING_RELATION
