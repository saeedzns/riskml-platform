"""Deterministic Power BI-ready exports from curated data and generated evidence."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pandas as pd
from sqlalchemy import Engine, text

PORTFOLIO_COLUMNS = (
    "application_id",
    "source_name",
    "source_row_id",
    "age",
    "age_band",
    "credit_amount",
    "duration_months",
    "installment_rate",
    "existing_credits",
    "dependents",
    "checking_status",
    "credit_history",
    "purpose",
    "savings_status",
    "employment_duration",
    "housing",
    "foreign_worker",
    "monthly_credit_burden",
    "amount_vs_purpose_avg",
    "purpose_applications",
    "amount_rank_within_purpose",
    "defaulted",
)
METRIC_COLUMNS = (
    "model",
    "roc_auc",
    "average_precision",
    "brier_score",
    "precision",
    "recall",
    "f1",
    "threshold",
    "positive_rate",
    "predicted_positive_rate",
)
THRESHOLD_COLUMNS = (
    "model",
    "threshold",
    "false_positive",
    "false_negative",
    "illustrative_cost",
)
CONFUSION_COLUMNS = ("model", "actual", "predicted", "count")
DRIFT_COLUMNS = (
    "feature",
    "method",
    "score",
    "missingness_delta",
    "drifted",
    "report_status",
    "semantics",
)
SUPPORTED_MODELS = ("logistic", "xgboost")
OUTPUT_FILES = {
    "portfolio": "portfolio.csv",
    "model_metrics": "model_metrics.csv",
    "threshold_tradeoffs": "threshold_tradeoffs.csv",
    "confusion_matrix": "confusion_matrix.csv",
    "drift_features": "drift_features.csv",
}

SELECT_PORTFOLIO = text(
    """
    SELECT
        application_id, source_name, source_row_id, age, age_band, credit_amount,
        duration_months, installment_rate, existing_credits, dependents, checking_status,
        credit_history, purpose, savings_status, employment_duration, housing, foreign_worker,
        monthly_credit_burden, amount_vs_purpose_avg, purpose_applications,
        amount_rank_within_purpose, defaulted
    FROM curated.credit_modeling
    WHERE source_name = :source_name
    ORDER BY source_row_id
    """
)


@dataclass(frozen=True)
class ModelEvidence:
    """Validated normalized rows derived from one model evidence document."""

    metrics: dict[str, object]
    threshold_tradeoffs: tuple[dict[str, object], ...]
    confusion_matrix: tuple[dict[str, object], ...]


def _normalized_source(source_name: str) -> str:
    normalized = source_name.strip()
    if not normalized:
        raise ValueError("source_name must be explicit and non-empty")
    return normalized


def load_portfolio_frame(engine: Engine, source_name: str) -> pd.DataFrame:
    """Load and validate one explicit source from the curated analytical relation."""

    normalized = _normalized_source(source_name)
    with engine.connect() as connection:
        frame = pd.read_sql(
            SELECT_PORTFOLIO,
            connection,
            params={"source_name": normalized},
        )
    if frame.empty:
        raise ValueError(
            "No dashboard rows found in curated.credit_modeling "
            f"for source {normalized!r}; synthetic fallback is prohibited"
        )
    missing = sorted(set(PORTFOLIO_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Curated portfolio is missing required columns: {missing}")
    clean = frame.loc[:, PORTFOLIO_COLUMNS].copy()
    if clean["application_id"].isna().any() or not clean["application_id"].is_unique:
        raise ValueError("application_id must be present and unique")
    if clean[["source_name", "source_row_id"]].isna().any().any():
        raise ValueError("source_name and source_row_id must remain present")
    observed_sources = set(clean["source_name"].astype(str))
    if observed_sources != {normalized}:
        raise ValueError(
            f"Portfolio query returned sources {sorted(observed_sources)!r}, "
            f"expected {normalized!r}"
        )
    if not clean["source_row_id"].is_unique:
        raise ValueError("source_row_id must be unique within the requested source")
    target_values = set(clean["defaulted"].dropna().astype(int))
    if clean["defaulted"].isna().any() or not target_values.issubset({0, 1}):
        raise ValueError("defaulted must contain only the binary domain {0, 1}")
    return clean


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read valid JSON evidence from {path}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"Evidence in {path} must be a JSON object")
    return cast(dict[str, Any], payload)


def _finite_number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    return number


def _nonnegative_integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _infer_model(path: Path) -> str:
    prefix = "metrics-"
    if not path.stem.startswith(prefix):
        raise ValueError(f"Cannot infer model name from evidence filename {path.name!r}")
    return path.stem.removeprefix(prefix)


def parse_model_evidence(path: Path, expected_model: str | None = None) -> ModelEvidence:
    """Validate flat or model-wrapped metric JSON and normalize its nested structures."""

    payload = _load_json_object(path)
    if "metrics" in payload:
        declared_model = payload.get("model")
        metrics_payload = payload["metrics"]
        if not isinstance(declared_model, str) or not declared_model.strip():
            raise ValueError(f"Wrapped metric evidence in {path} requires a model name")
        model = declared_model.strip()
    else:
        metrics_payload = payload
        model = expected_model or _infer_model(path)
    if expected_model is not None and model != expected_model:
        raise ValueError(f"Evidence model {model!r} does not match expected {expected_model!r}")
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model evidence {model!r}")
    if not isinstance(metrics_payload, dict):
        raise ValueError(f"Metrics in {path} must be a JSON object")
    metrics = cast(dict[str, Any], metrics_payload)

    metric_row: dict[str, object] = {"model": model}
    for field in METRIC_COLUMNS[1:]:
        if field not in metrics:
            raise ValueError(f"Metric evidence in {path} is missing {field!r}")
        metric_row[field] = _finite_number(metrics[field], field)

    tradeoff_payload = metrics.get("threshold_tradeoffs")
    if not isinstance(tradeoff_payload, list) or not tradeoff_payload:
        raise ValueError(f"Metric evidence in {path} requires threshold_tradeoffs")
    tradeoff_rows: list[dict[str, object]] = []
    for index, raw_tradeoff in enumerate(tradeoff_payload):
        if not isinstance(raw_tradeoff, dict):
            raise ValueError(f"threshold_tradeoffs[{index}] must be an object")
        tradeoff = cast(dict[str, object], raw_tradeoff)
        required = set(THRESHOLD_COLUMNS[1:])
        if not required.issubset(tradeoff):
            raise ValueError(f"threshold_tradeoffs[{index}] is missing required fields")
        tradeoff_rows.append(
            {
                "model": model,
                "threshold": _finite_number(tradeoff["threshold"], "threshold"),
                "false_positive": _nonnegative_integer(
                    tradeoff["false_positive"], "false_positive"
                ),
                "false_negative": _nonnegative_integer(
                    tradeoff["false_negative"], "false_negative"
                ),
                "illustrative_cost": _nonnegative_integer(
                    tradeoff["illustrative_cost"], "illustrative_cost"
                ),
            }
        )

    matrix_payload = metrics.get("confusion_matrix")
    if (
        not isinstance(matrix_payload, list)
        or len(matrix_payload) != 2
        or any(not isinstance(row, list) or len(row) != 2 for row in matrix_payload)
    ):
        raise ValueError("confusion_matrix must be exactly 2x2 with rows=actual, columns=predicted")
    confusion_rows: list[dict[str, object]] = []
    for actual, raw_row in enumerate(matrix_payload):
        row = cast(list[object], raw_row)
        for predicted, raw_count in enumerate(row):
            confusion_rows.append(
                {
                    "model": model,
                    "actual": actual,
                    "predicted": predicted,
                    "count": _nonnegative_integer(raw_count, "confusion_matrix count"),
                }
            )
    return ModelEvidence(metric_row, tuple(tradeoff_rows), tuple(confusion_rows))


def flatten_drift_report(path: Path) -> pd.DataFrame:
    """Validate and flatten univariate drift evidence without changing its semantics."""

    payload = _load_json_object(path)
    status = payload.get("status")
    semantics = payload.get("semantics")
    feature_results = payload.get("feature_results")
    if not isinstance(status, str) or not status:
        raise ValueError("Drift report requires a non-empty status")
    if not isinstance(semantics, str) or not semantics:
        raise ValueError("Drift report requires explicit semantics")
    semantics_lower = semantics.lower()
    if (
        "univariate data drift" not in semantics_lower
        or "does not establish concept drift" not in semantics_lower
    ):
        raise ValueError("Drift report must retain univariate data-drift semantics")
    if not isinstance(feature_results, dict) or not feature_results:
        raise ValueError("Drift report requires non-empty feature_results")

    rows: list[dict[str, object]] = []
    for feature in sorted(feature_results):
        raw_result = feature_results[feature]
        if not isinstance(feature, str) or not isinstance(raw_result, dict):
            raise ValueError("Each drift feature result must be a named object")
        result = cast(dict[str, object], raw_result)
        method = result.get("method")
        drifted = result.get("drifted")
        if not isinstance(method, str) or not method:
            raise ValueError(f"Drift feature {feature!r} requires a method")
        if not isinstance(drifted, bool):
            raise ValueError(f"Drift feature {feature!r} requires a boolean drifted flag")
        rows.append(
            {
                "feature": feature,
                "method": method,
                "score": _finite_number(result.get("score"), "score"),
                "missingness_delta": _finite_number(
                    result.get("missingness_delta"), "missingness_delta"
                ),
                "drifted": drifted,
                "report_status": status,
                "semantics": semantics,
            }
        )
    return pd.DataFrame(rows, columns=DRIFT_COLUMNS)


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def export_dashboard(
    engine: Engine,
    source_name: str,
    output_dir: Path,
    drift_report_path: Path,
    metric_paths: Mapping[str, Path],
) -> dict[str, int]:
    """Generate the complete deterministic dashboard dataset set."""

    if set(metric_paths) != set(SUPPORTED_MODELS):
        raise ValueError(f"Metric evidence is required for exactly {SUPPORTED_MODELS!r}")
    portfolio = load_portfolio_frame(engine, source_name)
    evidence = [parse_model_evidence(metric_paths[model], model) for model in SUPPORTED_MODELS]
    model_metrics = pd.DataFrame([item.metrics for item in evidence], columns=METRIC_COLUMNS)
    threshold_tradeoffs = pd.DataFrame(
        [row for item in evidence for row in item.threshold_tradeoffs],
        columns=THRESHOLD_COLUMNS,
    )
    confusion_matrix = pd.DataFrame(
        [row for item in evidence for row in item.confusion_matrix],
        columns=CONFUSION_COLUMNS,
    )
    drift_features = flatten_drift_report(drift_report_path)
    frames = {
        "portfolio": portfolio,
        "model_metrics": model_metrics,
        "threshold_tradeoffs": threshold_tradeoffs,
        "confusion_matrix": confusion_matrix,
        "drift_features": drift_features,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        _write_csv(frame, output_dir / OUTPUT_FILES[name])
    return {name: len(frame) for name, frame in frames.items()}
