import sys
from pathlib import Path

from risk_ml.cli import main


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
