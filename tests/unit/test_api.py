from pathlib import Path

from fastapi.testclient import TestClient

from risk_ml.api.app import create_app
from risk_ml.config import Settings
from risk_ml.data.fixture import generate_fixture
from risk_ml.modeling.training import train_model
from risk_ml.services.scoring import ScoringService


def _record() -> dict[str, object]:
    return generate_fixture(1).drop(columns=["defaulted"]).iloc[0].to_dict()


def _client(tmp_path: Path, max_batch_size: int = 3) -> TestClient:
    result = train_model(generate_fixture(160), kind="xgboost", artifact_dir=tmp_path)
    settings = Settings(
        model_path=result.artifact_path, max_batch_size=max_batch_size, _env_file=None
    )
    return TestClient(create_app(settings, ScoringService(result.artifact_path)))


def test_health_and_readiness(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        assert client.get("/health").json() == {"status": "alive"}
        assert client.get("/ready").status_code == 200


def test_predict_and_explain_contract(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        prediction = client.post("/api/v1/predict", json=_record())
        assert prediction.status_code == 200
        assert 0 <= prediction.json()["probability"] <= 1
        explanation = client.post("/api/v1/explain", json=_record())
        assert explanation.status_code == 200
        assert explanation.json()["contributions"]


def test_invalid_payload_and_batch_limit(tmp_path: Path) -> None:
    with _client(tmp_path, max_batch_size=2) as client:
        invalid = {**_record(), "age": 12}
        assert client.post("/api/v1/predict", json=invalid).status_code == 422
        assert (
            client.post("/api/v1/predict/batch", json={"records": [_record()] * 3}).status_code
            == 422
        )


def test_readiness_failure_when_model_missing(tmp_path: Path) -> None:
    settings = Settings(model_path=tmp_path / "missing.joblib", _env_file=None)
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
