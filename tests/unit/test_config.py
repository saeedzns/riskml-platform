from pathlib import Path

import pytest
from pydantic import ValidationError

from risk_ml.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.environment == "development"
    assert settings.model_path == Path("artifacts/champion.joblib")
    assert settings.max_batch_size == 100


def test_settings_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RISK_ML_MAX_BATCH_SIZE", "7")
    assert Settings(_env_file=None).max_batch_size == 7


def test_settings_reject_invalid_batch_size() -> None:
    with pytest.raises(ValidationError):
        Settings(max_batch_size=0, _env_file=None)
