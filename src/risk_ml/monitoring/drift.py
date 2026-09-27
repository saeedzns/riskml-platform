"""Transparent univariate drift detection using PSI and total variation distance."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from risk_ml.data.contracts import CATEGORICAL_FEATURES, NUMERIC_FEATURES


def reference_profile(frame: pd.DataFrame) -> dict[str, Any]:
    """Create a JSON-safe audit profile for the training/reference population."""

    return {
        "rows": len(frame),
        "numeric": {
            name: {
                "mean": float(frame[name].mean()),
                "std": float(frame[name].std()),
                "missing_rate": float(frame[name].isna().mean()),
            }
            for name in NUMERIC_FEATURES
        },
        "categorical": {
            name: frame[name].astype(str).value_counts(normalize=True).sort_index().to_dict()
            for name in CATEGORICAL_FEATURES
        },
    }


def _psi(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    edges = np.unique(np.quantile(reference.dropna(), np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    ref = pd.cut(reference, edges, include_lowest=True).value_counts(normalize=True, sort=False)
    cur = pd.cut(current, edges, include_lowest=True).value_counts(normalize=True, sort=False)
    ref_values = np.clip(ref.to_numpy(), 1e-6, None)
    cur_values = np.clip(cur.to_numpy(), 1e-6, None)
    return float(np.sum((cur_values - ref_values) * np.log(cur_values / ref_values)))


def _total_variation(reference: pd.Series, current: pd.Series) -> float:
    categories = sorted(set(reference.dropna().astype(str)) | set(current.dropna().astype(str)))
    ref = reference.astype(str).value_counts(normalize=True).reindex(categories, fill_value=0)
    cur = current.astype(str).value_counts(normalize=True).reindex(categories, fill_value=0)
    return float(0.5 * np.abs(ref - cur).sum())


def drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    *,
    psi_threshold: float = 0.2,
    categorical_threshold: float = 0.15,
    missingness_threshold: float = 0.1,
) -> dict[str, Any]:
    """Compare feature distributions and return deterministic alert semantics."""

    features: dict[str, Any] = {}
    for name in NUMERIC_FEATURES:
        score = _psi(reference[name], current[name])
        missing_delta = abs(float(reference[name].isna().mean() - current[name].isna().mean()))
        features[name] = {
            "method": "psi",
            "score": score,
            "missingness_delta": missing_delta,
            "drifted": score > psi_threshold or missing_delta > missingness_threshold,
        }
    for name in CATEGORICAL_FEATURES:
        score = _total_variation(reference[name], current[name])
        missing_delta = abs(float(reference[name].isna().mean() - current[name].isna().mean()))
        features[name] = {
            "method": "total_variation",
            "score": score,
            "missingness_delta": missing_delta,
            "drifted": score > categorical_threshold or missing_delta > missingness_threshold,
        }
    drifted = [name for name, result in features.items() if result["drifted"]]
    return {
        "status": "alert" if drifted else "ok",
        "drifted_features": drifted,
        "feature_results": features,
        "semantics": "Univariate data drift only; this does not establish concept drift.",
    }


def write_report(report: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
