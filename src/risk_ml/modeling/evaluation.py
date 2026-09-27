"""Imbalance-aware model evaluation and artifact generation."""

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_probabilities(y_true: Any, probability: Any, threshold: float = 0.5) -> dict[str, Any]:
    """Evaluate ranking, calibration, and threshold-dependent behavior."""

    y_array = np.asarray(y_true)
    probability_array = np.asarray(probability)
    prediction = (probability_array >= threshold).astype(int)
    tradeoffs = []
    for candidate in (0.3, 0.5, 0.7):
        candidate_prediction = (probability_array >= candidate).astype(int)
        matrix = confusion_matrix(y_array, candidate_prediction, labels=[0, 1])
        false_positive = int(matrix[0, 1])
        false_negative = int(matrix[1, 0])
        tradeoffs.append(
            {
                "threshold": candidate,
                "false_positive": false_positive,
                "false_negative": false_negative,
                "illustrative_cost": false_positive + 5 * false_negative,
            }
        )
    return {
        "roc_auc": float(roc_auc_score(y_array, probability_array)),
        "average_precision": float(average_precision_score(y_array, probability_array)),
        "brier_score": float(brier_score_loss(y_array, probability_array)),
        "precision": float(precision_score(y_array, prediction, zero_division=0)),
        "recall": float(recall_score(y_array, prediction, zero_division=0)),
        "f1": float(f1_score(y_array, prediction, zero_division=0)),
        "threshold": threshold,
        "confusion_matrix": confusion_matrix(y_array, prediction).tolist(),
        "positive_rate": float(y_array.mean()),
        "predicted_positive_rate": float(prediction.mean()),
        "threshold_tradeoffs": tradeoffs,
    }


def write_metrics(metrics: dict[str, Any], path: Path) -> Path:
    """Persist machine-readable evidence."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_evaluation_plot(y_true: Any, probability: Any, path: Path) -> Path:
    """Persist ROC, precision-recall, and calibration evidence in one reviewable figure."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.calibration import CalibrationDisplay
    from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay

    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 3, figsize=(14, 4))
    RocCurveDisplay.from_predictions(y_true, probability, ax=axes[0])
    PrecisionRecallDisplay.from_predictions(y_true, probability, ax=axes[1])
    CalibrationDisplay.from_predictions(
        y_true, probability, n_bins=8, strategy="quantile", ax=axes[2]
    )
    figure.tight_layout()
    figure.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(figure)
    return path
