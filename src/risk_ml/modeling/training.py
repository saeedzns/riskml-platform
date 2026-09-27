"""Training workflow with split-before-fit and optional MLflow tracking."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.utils.class_weight import compute_sample_weight

from risk_ml.data.contracts import RAW_FEATURES, TARGET, validate_applications
from risk_ml.modeling.evaluation import evaluate_probabilities, write_evaluation_plot, write_metrics
from risk_ml.modeling.models import ModelKind, build_model


@dataclass(frozen=True)
class TrainingResult:
    model: Pipeline
    metrics: dict[str, Any]
    test_features: pd.DataFrame
    test_target: pd.Series
    artifact_path: Path


def train_model(
    frame: pd.DataFrame,
    *,
    kind: ModelKind,
    artifact_dir: Path,
    seed: int = 20260928,
    tracking_uri: str | None = None,
    experiment: str = "risk-ml-credit-default",
) -> TrainingResult:
    """Validate, stratify, fit only on train, evaluate, and persist the complete pipeline."""

    clean = validate_applications(frame)
    features = clean.loc[:, RAW_FEATURES]
    target = clean[TARGET]
    train_x, test_x, train_y, test_y = train_test_split(
        features, target, test_size=0.25, random_state=seed, stratify=target
    )
    model = build_model(kind, seed)
    if kind == "xgboost":
        sample_weight = compute_sample_weight("balanced", train_y)
        model.fit(train_x, train_y, classifier__sample_weight=sample_weight)
    else:
        model.fit(train_x, train_y)
    probability = model.predict_proba(test_x)[:, 1]
    metrics = evaluate_probabilities(test_y, probability)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{kind}.joblib"
    joblib.dump(
        {"model": model, "model_kind": kind, "model_version": "0.1.0", "features": RAW_FEATURES},
        artifact_path,
    )
    metrics_path = write_metrics(metrics, artifact_dir / f"metrics-{kind}.json")
    plot_path = write_evaluation_plot(test_y, probability, artifact_dir / f"evaluation-{kind}.png")
    if tracking_uri:
        import mlflow

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment)
        with mlflow.start_run(run_name=f"{kind}-seed-{seed}"):
            mlflow.log_params({"model_kind": kind, "seed": seed, "train_rows": len(train_x)})
            mlflow.log_metrics({k: v for k, v in metrics.items() if isinstance(v, float)})
            mlflow.log_artifact(str(metrics_path), artifact_path="evaluation")
            mlflow.log_artifact(str(plot_path), artifact_path="evaluation")
            mlflow.log_artifact(str(artifact_path), artifact_path="model")
            mlflow.set_tags(
                {
                    "dataset": "deterministic-synthetic-german-credit-compatible",
                    "code_version": "0.1.0",
                }
            )
    return TrainingResult(model, metrics, test_x, test_y, artifact_path)


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a trusted local training artifact and validate its envelope."""

    payload = joblib.load(path)
    required = {"model", "model_kind", "model_version", "features"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise ValueError("Invalid model artifact envelope")
    if tuple(payload["features"]) != RAW_FEATURES:
        raise ValueError("Model artifact feature contract is incompatible")
    return payload
