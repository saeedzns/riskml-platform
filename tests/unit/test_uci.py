import pandas as pd

from risk_ml.data.uci import map_uci_frames


def test_official_uci_mapping() -> None:
    row = {f"Attribute{i}": "unused" for i in range(1, 21)}
    row.update(
        {
            "Attribute1": "A11",
            "Attribute2": 6,
            "Attribute3": "A34",
            "Attribute4": "A43",
            "Attribute5": 1169,
            "Attribute6": "A65",
            "Attribute7": "A75",
            "Attribute8": 4,
            "Attribute13": 67,
            "Attribute15": "A152",
            "Attribute16": 2,
            "Attribute18": 1,
            "Attribute20": "A201",
        }
    )
    mapped = map_uci_frames(pd.DataFrame([row]), pd.DataFrame({"class": [2]}))
    assert mapped.iloc[0].to_dict() == {
        "age": 67,
        "credit_amount": 1169.0,
        "duration_months": 6,
        "installment_rate": 4,
        "existing_credits": 2,
        "dependents": 1,
        "checking_status": "negative",
        "credit_history": "critical",
        "purpose": "other",
        "savings_status": "unknown",
        "employment_duration": "long",
        "housing": "own",
        "foreign_worker": True,
        "defaulted": 1,
    }
