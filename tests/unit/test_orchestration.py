from pathlib import Path

from risk_ml.data.fixture import write_fixture
from risk_ml.orchestration import monitoring_step, validate_step


def test_local_non_database_orchestration_steps(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    fixture = tmp_path / "fixture.csv"
    write_fixture(fixture, 20)
    monkeypatch.setattr("risk_ml.orchestration.FIXTURE", fixture)
    monkeypatch.chdir(tmp_path)
    assert validate_step() == 20
    assert Path(monitoring_step()).exists()
