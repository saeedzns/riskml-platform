"""Canonical command-line workflows."""

import argparse
import json
import shutil
from pathlib import Path

from risk_ml.config import get_settings
from risk_ml.data.fixture import generate_fixture, write_fixture
from risk_ml.data.ingestion import ingest_csv
from risk_ml.data.sources import KNOWN_SOURCES
from risk_ml.data.training_data import load_curated_training_frame
from risk_ml.data.uci import download_uci_credit
from risk_ml.db.core import create_db_engine, execute_sql_file
from risk_ml.logging import configure_logging
from risk_ml.modeling.models import ModelKind
from risk_ml.modeling.training import train_model
from risk_ml.monitoring.drift import drift_report, reference_profile, write_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="risk-ml")
    commands = parser.add_subparsers(dest="command", required=True)
    fixture = commands.add_parser("fixture")
    fixture.add_argument("--output", type=Path, default=Path("data/processed/credit_fixture.csv"))
    download = commands.add_parser("download-uci")
    download.add_argument("--output", type=Path, default=Path("data/processed/uci_credit.csv"))
    ingest = commands.add_parser("ingest")
    ingest.add_argument("--input", type=Path, required=True)
    ingest.add_argument("--source", choices=KNOWN_SOURCES, required=True)
    commands.add_parser("transform")
    train = commands.add_parser("train")
    train.add_argument("--model", choices=["logistic", "xgboost", "all"], default="all")
    train.add_argument("--source", choices=KNOWN_SOURCES, required=True)
    monitor = commands.add_parser("monitor")
    monitor.add_argument("--simulate-shift", action="store_true")
    monitor.add_argument("--output", type=Path, default=Path("artifacts/drift-report.json"))
    return parser


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    args = _parser().parse_args()
    if args.command == "fixture":
        write_fixture(args.output, seed=settings.random_seed)
        print(args.output)
    elif args.command == "download-uci":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        download_uci_credit().to_csv(args.output, index=False)
        print(args.output)
    elif args.command == "ingest":
        print(
            json.dumps(
                {
                    "ingested": ingest_csv(create_db_engine(), args.input, args.source),
                    "source": args.source,
                }
            )
        )
    elif args.command == "transform":
        execute_sql_file(create_db_engine(), Path("sql/transformations/001_modeling_view.sql"))
        print("curated.credit_modeling refreshed")
    elif args.command == "train":
        dataset = load_curated_training_frame(create_db_engine(), args.source)
        kinds: list[ModelKind] = ["logistic", "xgboost"] if args.model == "all" else [args.model]
        for kind in kinds:
            result = train_model(
                dataset.frame,
                kind=kind,
                artifact_dir=Path("artifacts"),
                seed=settings.random_seed,
                tracking_uri=settings.mlflow_tracking_uri,
                experiment=settings.mlflow_experiment,
                dataset_source=dataset.source_name,
                dataset_relation=dataset.relation,
            )
            print(json.dumps({"model": kind, "metrics": result.metrics}, sort_keys=True))
            if kind == "xgboost":
                shutil.copy2(result.artifact_path, settings.model_path)
    elif args.command == "monitor":
        reference = generate_fixture(600, settings.random_seed)
        current = generate_fixture(600, settings.random_seed + 1)
        if args.simulate_shift:
            current["credit_amount"] *= 4
            current["checking_status"] = "negative"
        report = drift_report(reference, current)
        write_report(reference_profile(reference), settings.reference_profile_path)
        write_report(report, args.output)
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
