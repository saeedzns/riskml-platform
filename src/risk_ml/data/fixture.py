"""Deterministic source-compatible synthetic credit applications."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_fixture(rows: int = 600, seed: int = 20260928) -> pd.DataFrame:
    """Generate plausible educational data with a nonlinear default signal."""

    rng = np.random.default_rng(seed)
    checking = rng.choice(["none", "negative", "low", "high"], rows, p=[0.35, 0.2, 0.3, 0.15])
    history = rng.choice(
        ["critical", "delayed", "existing_paid", "all_paid", "no_credits"],
        rows,
        p=[0.12, 0.1, 0.55, 0.15, 0.08],
    )
    savings = rng.choice(["unknown", "low", "medium", "high"], rows, p=[0.25, 0.45, 0.2, 0.1])
    employment = rng.choice(
        ["unemployed", "short", "medium", "long"], rows, p=[0.08, 0.32, 0.38, 0.22]
    )
    duration = rng.choice(
        [6, 12, 18, 24, 36, 48, 60], rows, p=[0.05, 0.18, 0.14, 0.25, 0.2, 0.13, 0.05]
    )
    amount = np.maximum(250, rng.lognormal(mean=7.8, sigma=0.65, size=rows)).round(2)
    age = np.clip(rng.normal(36, 11, rows).round(), 18, 75).astype(int)
    logit = (
        -1.9
        + 0.75 * (checking == "negative")
        + 0.5 * (checking == "none")
        + 0.8 * (history == "critical")
        + 0.55 * (employment == "unemployed")
        + 0.45 * (savings == "low")
        + 0.018 * (duration - 20)
        + 0.000055 * (amount - 3000)
        + 0.35 * ((amount > 6000) & (duration > 30))
        - 0.02 * (age - 35)
    )
    probability = 1 / (1 + np.exp(-logit))
    return pd.DataFrame(
        {
            "age": age,
            "credit_amount": amount,
            "duration_months": duration,
            "installment_rate": rng.integers(1, 5, rows),
            "existing_credits": rng.choice([1, 2, 3, 4], rows, p=[0.65, 0.25, 0.08, 0.02]),
            "dependents": rng.choice([1, 2], rows, p=[0.84, 0.16]),
            "checking_status": checking,
            "credit_history": history,
            "purpose": rng.choice(["car", "furniture", "education", "business", "other"], rows),
            "savings_status": savings,
            "employment_duration": employment,
            "housing": rng.choice(["rent", "own", "free"], rows, p=[0.25, 0.67, 0.08]),
            "foreign_worker": rng.choice([True, False], rows, p=[0.94, 0.06]),
            "defaulted": rng.binomial(1, probability),
        }
    )


def write_fixture(path: Path, rows: int = 600, seed: int = 20260928) -> Path:
    """Write a deterministic CSV fixture for ingestion."""

    path.parent.mkdir(parents=True, exist_ok=True)
    generate_fixture(rows, seed).to_csv(path, index=False)
    return path
