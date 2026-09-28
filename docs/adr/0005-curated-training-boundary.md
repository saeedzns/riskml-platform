# ADR 0005: Curated PostgreSQL is the canonical training source

## Status

Accepted.

## Context

The platform documented a raw PostgreSQL to SQL-curated to training flow, but the CLI and Airflow
training step reread source CSV files. The curated view also contains portfolio-wide analytical
columns whose values are calculated before the train/test split and therefore are unsuitable as
automatic model inputs.

## Decision

Canonical training loads rows from `curated.credit_modeling` through one parameterized,
source-filtered loader. Ingestion and training require an explicit stable source identifier, which is
also logged to MLflow with the curated relation. The loader validates the result and selects only the
existing raw feature contract plus `defaulted`. SQL aggregate, rank, and ratio columns remain useful
for analytics and SQL evidence but are not model features.

Native Python remains supported where platform policy permits compiled extensions. A dedicated
non-root Compose CLI image is the supported Linux execution path and shares PostgreSQL and MLflow
networking while mounting data and artifacts writable and repository SQL read-only.

## Consequences

- CLI and Airflow training fail clearly when migration, ingestion, transformation, or the requested
  source is missing instead of silently training from a CSV.
- Multiple ingested sources cannot be silently mixed, and official UCI runs are not tagged as
  synthetic.
- Learned preprocessing and model fitting still happen only after the stratified split.
- Curated analytical columns require a separate leakage review and split-aware implementation before
  they can enter the model contract.
