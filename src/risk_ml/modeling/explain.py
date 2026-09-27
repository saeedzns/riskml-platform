"""Structured SHAP explanations for trusted fitted pipelines."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class FeatureContribution:
    feature: str
    contribution: float
    value: float


@dataclass(frozen=True)
class Explanation:
    base_value: float
    contributions: tuple[FeatureContribution, ...]
    note: str = "SHAP describes model behavior; it does not establish causal effects."


def explain_prediction(model: Pipeline, frame: pd.DataFrame, top_k: int = 8) -> Explanation:
    """Explain one boosted-model prediction in transformed feature space."""

    if len(frame) != 1:
        raise ValueError("Local explanation requires exactly one row")
    preprocessor = model.named_steps["preprocessor"]
    estimator = model.named_steps["classifier"]
    transformed = np.asarray(preprocessor.transform(frame), dtype=float)
    names = preprocessor.get_feature_names_out()
    import shap

    explainer = shap.TreeExplainer(estimator)
    shap_values = np.asarray(explainer.shap_values(transformed))
    values = shap_values[0] if shap_values.ndim == 2 else shap_values
    base = np.asarray(explainer.expected_value).reshape(-1)
    ranked = np.argsort(np.abs(values))[::-1][:top_k]
    contributions = tuple(
        FeatureContribution(str(names[index]), float(values[index]), float(transformed[0, index]))
        for index in ranked
    )
    return Explanation(float(base[0]), contributions)
