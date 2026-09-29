from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest

from risk_ml.analytics.dashboard import (
    CONFUSION_COLUMNS,
    DRIFT_COLUMNS,
    METRIC_COLUMNS,
    OUTPUT_FILES,
    PORTFOLIO_COLUMNS,
    SELECT_PORTFOLIO,
    export_dashboard,
    flatten_drift_report,
    load_portfolio_frame,
    parse_model_evidence,
)
from risk_ml.data.fixture import generate_fixture
from risk_ml.monitoring.drift import drift_report, write_report


def _portfolio(source: str = "source-a") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "application_id": "00000000-0000-0000-0000-000000000001",
                "source_name": source,
                "source_row_id": 0,
                "age": 22,
                "age_band": "young",
                "credit_amount": 1200.0,
                "duration_months": 12,
                "installment_rate": 2,
                "existing_credits": 1,
                "dependents": 1,
                "checking_status": "low",
                "credit_history": "existing_paid",
                "purpose": "car",
                "savings_status": "low",
                "employment_duration": "medium",
                "housing": "own",
                "foreign_worker": True,
                "monthly_credit_burden": 100.0,
                "amount_vs_purpose_avg": 0.8,
                "purpose_applications": 2,
                "amount_rank_within_purpose": 2,
                "defaulted": 0,
            },
            {
                "application_id": "00000000-0000-0000-0000-000000000002",
                "source_name": source,
                "source_row_id": 1,
                "age": 57,
                "age_band": "senior",
                "credit_amount": 1800.0,
                "duration_months": 18,
                "installment_rate": 3,
                "existing_credits": 2,
                "dependents": 1,
                "checking_status": "negative",
                "credit_history": "critical",
                "purpose": "car",
                "savings_status": "unknown",
                "employment_duration": "short",
                "housing": "rent",
                "foreign_worker": False,
                "monthly_credit_burden": 100.0,
                "amount_vs_purpose_avg": 1.2,
                "purpose_applications": 2,
                "amount_rank_within_purpose": 1,
                "defaulted": 1,
            },
        ],
        columns=PORTFOLIO_COLUMNS,
    )


def _metrics() -> dict[str, object]:
    return {
        "roc_auc": 0.75,
        "average_precision": 0.55,
        "brier_score": 0.2,
        "precision": 0.45,
        "recall": 0.6,
        "f1": 0.51,
        "threshold": 0.5,
        "positive_rate": 0.3,
        "predicted_positive_rate": 0.4,
        "confusion_matrix": [[12, 3], [2, 5]],
        "threshold_tradeoffs": [
            {
                "threshold": threshold,
                "false_positive": index + 3,
                "false_negative": index + 1,
                "illustrative_cost": index + 8,
            }
            for index, threshold in enumerate((0.3, 0.5, 0.7))
        ],
    }


def _drift_payload() -> dict[str, object]:
    return {
        "status": "alert",
        "drifted_features": ["checking_status", "credit_amount"],
        "semantics": "Univariate data drift only; this does not establish concept drift.",
        "feature_results": {
            "checking_status": {
                "method": "total_variation",
                "score": 0.8,
                "missingness_delta": 0.0,
                "drifted": True,
            },
            "credit_amount": {
                "method": "psi",
                "score": 5.2,
                "missingness_delta": 0.0,
                "drifted": True,
            },
        },
    }


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _engine_with_frame(monkeypatch: pytest.MonkeyPatch, frame: pd.DataFrame) -> Mock:
    engine = MagicMock()
    connection = object()
    engine.connect.return_value.__enter__.return_value = connection
    read_sql = Mock(return_value=frame)
    monkeypatch.setattr("risk_ml.analytics.dashboard.pd.read_sql", read_sql)
    engine._dashboard_read_sql = read_sql
    return engine


def test_portfolio_query_is_parameterized_and_source_scoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _engine_with_frame(monkeypatch, _portfolio())

    frame = load_portfolio_frame(engine, " source-a ")

    assert tuple(frame.columns) == PORTFOLIO_COLUMNS
    assert frame["application_id"].is_unique
    assert set(frame["source_name"]) == {"source-a"}
    assert set(frame["defaulted"]) == {0, 1}
    assert ":source_name" in str(SELECT_PORTFOLIO)
    assert "source-a" not in str(SELECT_PORTFOLIO)
    assert engine._dashboard_read_sql.call_args.kwargs["params"] == {"source_name": "source-a"}


def test_portfolio_requires_explicit_source(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine_with_frame(monkeypatch, _portfolio())
    with pytest.raises(ValueError, match="explicit"):
        load_portfolio_frame(engine, "  ")
    engine.connect.assert_not_called()


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda frame: frame.assign(source_name="other"), "expected 'source-a'"),
        (
            lambda frame: frame.assign(application_id=frame["application_id"].iloc[0]),
            "application_id",
        ),
        (lambda frame: frame.assign(defaulted=2), "binary domain"),
        (lambda frame: frame.drop(columns=["age_band"]), "missing required columns"),
    ],
)
def test_portfolio_integrity_failures_are_explicit(
    monkeypatch: pytest.MonkeyPatch,
    mutator: object,
    message: str,
) -> None:
    invalid = mutator(_portfolio())  # type: ignore[operator]
    engine = _engine_with_frame(monkeypatch, invalid)
    with pytest.raises(ValueError, match=message):
        load_portfolio_frame(engine, "source-a")


def test_portfolio_does_not_fall_back_to_synthetic_data(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _engine_with_frame(monkeypatch, pd.DataFrame(columns=PORTFOLIO_COLUMNS))
    with pytest.raises(ValueError, match="synthetic fallback is prohibited"):
        load_portfolio_frame(engine, "missing-source")


def test_flat_and_wrapped_model_evidence_formats_parse(tmp_path: Path) -> None:
    flat = _write_json(tmp_path / "metrics-logistic.json", _metrics())
    wrapped = _write_json(
        tmp_path / "wrapped.json",
        {"model": "xgboost", "metrics": _metrics()},
    )

    logistic = parse_model_evidence(flat)
    xgboost = parse_model_evidence(wrapped, "xgboost")

    assert tuple(logistic.metrics) == METRIC_COLUMNS
    assert logistic.metrics["model"] == "logistic"
    assert xgboost.metrics["model"] == "xgboost"
    assert len(logistic.threshold_tradeoffs) == 3
    assert all(isinstance(row["false_positive"], int) for row in logistic.threshold_tradeoffs)
    assert len(logistic.confusion_matrix) == 4
    assert tuple(logistic.confusion_matrix[0]) == CONFUSION_COLUMNS
    assert sum(int(row["count"]) for row in logistic.confusion_matrix) == 22
    assert {(row["actual"], row["predicted"]) for row in logistic.confusion_matrix} == {
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    }


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"roc_auc": float("nan")}, "finite"),
        ({"confusion_matrix": [[1, 2, 3], [4, 5, 6]]}, "exactly 2x2"),
        ({"threshold_tradeoffs": []}, "requires threshold_tradeoffs"),
    ],
)
def test_malformed_model_evidence_fails_clearly(
    tmp_path: Path,
    change: dict[str, object],
    message: str,
) -> None:
    payload = {**_metrics(), **change}
    path = _write_json(tmp_path / "metrics-logistic.json", payload)
    with pytest.raises(ValueError, match=message):
        parse_model_evidence(path)


def test_drift_features_preserve_verified_simulation_semantics(tmp_path: Path) -> None:
    reference = generate_fixture(1000, 10)
    shifted = generate_fixture(1000, 11)
    shifted["credit_amount"] *= 4
    shifted["checking_status"] = "negative"
    report = drift_report(reference, shifted)
    path = write_report(report, tmp_path / "drift.json")

    frame = flatten_drift_report(path)

    assert tuple(frame.columns) == DRIFT_COLUMNS
    assert {"credit_amount", "checking_status"}.issubset(
        set(frame.loc[frame["drifted"], "feature"])
    )
    assert frame["drifted"].dtype == bool
    assert set(frame["semantics"]) == {report["semantics"]}
    assert "concept_drift" not in frame.columns


def test_export_is_deterministic_and_writes_only_expected_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "risk_ml.analytics.dashboard.load_portfolio_frame",
        lambda _engine, _source: _portfolio(),
    )
    metrics = {
        model: _write_json(tmp_path / f"metrics-{model}.json", _metrics())
        for model in ("logistic", "xgboost")
    }
    drift = _write_json(tmp_path / "drift.json", _drift_payload())
    existing_paths = set(tmp_path.iterdir())
    output_dir = tmp_path / "dashboard"

    counts = export_dashboard(Mock(), "source-a", output_dir, drift, metrics)
    first_contents = {path.name: path.read_bytes() for path in output_dir.iterdir()}
    repeated_counts = export_dashboard(Mock(), "source-a", output_dir, drift, metrics)

    assert counts == {
        "portfolio": 2,
        "model_metrics": 2,
        "threshold_tradeoffs": 6,
        "confusion_matrix": 8,
        "drift_features": 2,
    }
    assert repeated_counts == counts
    assert set(first_contents) == set(OUTPUT_FILES.values())
    assert {path.name: path.read_bytes() for path in output_dir.iterdir()} == first_contents
    assert all(path.parent == output_dir for path in output_dir.iterdir())
    assert set(tmp_path.iterdir()) == existing_paths | {output_dir}


def test_generated_dashboard_csvs_are_gitignored() -> None:
    ignore = Path(".gitignore").read_text(encoding="utf-8").splitlines()
    assert "dashboard/data/*" in ignore
    assert "!dashboard/data/.gitkeep" in ignore
    docker_ignore = Path(".dockerignore").read_text(encoding="utf-8").splitlines()
    assert "dashboard/data/*" in docker_ignore
    assert "!dashboard/data/.gitkeep" in docker_ignore
