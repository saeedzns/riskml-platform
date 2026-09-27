"""Thread-safe immutable scoring facade."""

from pathlib import Path
from typing import Any

import pandas as pd

from risk_ml.data.contracts import RAW_FEATURES, validate_applications
from risk_ml.modeling.explain import Explanation, explain_prediction
from risk_ml.modeling.training import load_artifact


class ScoringService:
    """Load one trusted pipeline artifact and share it for process lifetime."""

    def __init__(self, path: Path) -> None:
        payload = load_artifact(path)
        self.model: Any = payload["model"]
        self.model_kind = str(payload["model_kind"])
        self.model_version = str(payload["model_version"])

    def predict(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        frame = validate_applications(pd.DataFrame(records), require_target=False)
        frame = frame.loc[:, RAW_FEATURES]
        probabilities = self.model.predict_proba(frame)[:, 1]
        return [
            {
                "probability": float(probability),
                "predicted_default": bool(probability >= 0.5),
                "threshold": 0.5,
                "model_version": self.model_version,
            }
            for probability in probabilities
        ]

    def explain(self, record: dict[str, Any], top_k: int = 8) -> Explanation:
        if self.model_kind != "xgboost":
            raise ValueError("Local SHAP explanation is available for the xgboost artifact")
        frame = validate_applications(pd.DataFrame([record]), require_target=False)
        return explain_prediction(self.model, frame.loc[:, RAW_FEATURES], top_k)
