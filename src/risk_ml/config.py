"""Typed runtime configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from RISK_ML_* variables."""

    model_config = SettingsConfigDict(env_prefix="RISK_ML_", env_file=".env", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://risk_ml:risk_ml_dev@localhost:5432/risk_ml"
    model_path: Path = Path("artifacts/champion.joblib")
    reference_profile_path: Path = Path("artifacts/reference_profile.json")
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    mlflow_experiment: str = "risk-ml-credit-default"
    max_batch_size: int = Field(default=100, ge=1, le=1000)
    random_seed: int = 20260928


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide immutable-by-convention settings instance."""

    return Settings()
