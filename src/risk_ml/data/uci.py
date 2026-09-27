"""Official UCI Statlog German Credit acquisition and semantic mapping."""

from typing import Any

import pandas as pd

from risk_ml.data.contracts import validate_applications

CHECKING = {"A11": "negative", "A12": "low", "A13": "high", "A14": "none"}
HISTORY = {
    "A30": "no_credits",
    "A31": "all_paid",
    "A32": "existing_paid",
    "A33": "delayed",
    "A34": "critical",
}
PURPOSE = {
    "A40": "car",
    "A41": "car",
    "A42": "furniture",
    "A43": "other",
    "A44": "other",
    "A45": "other",
    "A46": "education",
    "A47": "other",
    "A48": "education",
    "A49": "business",
    "A410": "other",
}
SAVINGS = {"A61": "low", "A62": "medium", "A63": "medium", "A64": "high", "A65": "unknown"}
EMPLOYMENT = {
    "A71": "unemployed",
    "A72": "short",
    "A73": "short",
    "A74": "medium",
    "A75": "long",
}
HOUSING = {"A151": "rent", "A152": "own", "A153": "free"}


def map_uci_frames(features: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """Map the official 20-field symbolic source into the smaller model contract."""

    frame = pd.DataFrame(
        {
            "age": features["Attribute13"],
            "credit_amount": features["Attribute5"],
            "duration_months": features["Attribute2"],
            "installment_rate": features["Attribute8"],
            "existing_credits": features["Attribute16"],
            "dependents": features["Attribute18"],
            "checking_status": features["Attribute1"].map(CHECKING),
            "credit_history": features["Attribute3"].map(HISTORY),
            "purpose": features["Attribute4"].map(PURPOSE),
            "savings_status": features["Attribute6"].map(SAVINGS),
            "employment_duration": features["Attribute7"].map(EMPLOYMENT),
            "housing": features["Attribute15"].map(HOUSING),
            "foreign_worker": features["Attribute20"].eq("A201"),
            "defaulted": target.iloc[:, 0].eq(2).astype(int),
        }
    )
    return validate_applications(frame)


def download_uci_credit() -> pd.DataFrame:
    """Fetch UCI dataset 144 through its official client; requires network access."""

    from ucimlrepo import fetch_ucirepo

    dataset: Any = fetch_ucirepo(id=144)
    return map_uci_frames(dataset.data.features, dataset.data.targets)
