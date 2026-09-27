# Contributing

Create a focused branch and conventional commit. Install with `python -m pip install -e ".[dev]"`.
Before a pull request run `make verify`; for data-layer changes also run `make test-integration` against
PostgreSQL and validate `docker compose config`. Add a migration for schema changes and an ADR for a
consequential or hard-to-reverse decision. Never commit secrets, downloaded raw data, or generated
model/MLflow artifacts.

