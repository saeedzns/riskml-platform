# Local operations runbook

## Canonical Linux container workflow

This path is supported on Linux and on Windows hosts where Application Control prevents native
scikit-learn extensions from loading. It does not require weakening host security.

```bash
docker compose up -d postgres mlflow
docker compose run --rm cli python -m alembic upgrade head
docker compose run --rm cli risk-ml download-uci --output data/processed/uci_credit.csv
docker compose run --rm cli risk-ml ingest \
  --input data/processed/uci_credit.csv --source uci-statlog-german-credit-144
docker compose run --rm cli risk-ml transform
docker compose run --rm cli risk-ml train \
  --model all --source uci-statlog-german-credit-144
docker compose up -d api
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl -X POST http://localhost:8000/api/v1/predict \
  -H 'Content-Type: application/json' \
  -d '{"age":35,"credit_amount":3500,"duration_months":24,"installment_rate":3,"existing_credits":1,"dependents":1,"checking_status":"low","credit_history":"existing_paid","purpose":"car","savings_status":"medium","employment_duration":"medium","housing":"own","foreign_worker":true}'
docker compose run --rm cli risk-ml monitor --simulate-shift \
  --output artifacts/drift-shifted.json
```

The CLI service contains the project package and migrations, reaches PostgreSQL and MLflow on the
Compose network, writes only through the mounted data/artifact directories, and sees repository SQL
read-only. API images deliberately contain no model. Compose mounts the generated champion read-only;
without it `/health` remains available while `/ready` returns 503. MLflow host validation permits only
the internal `mlflow:5000` endpoint and local UI endpoints on `localhost`; the security middleware
remains enabled. Artifact uploads are proxied through the tracking server into its `mlflow-data`
volume; clients do not mount or write the server's `/mlflow` filesystem.

For the deterministic offline path, replace the download and ingest commands with:

```bash
docker compose run --rm cli risk-ml fixture --output data/processed/credit_fixture.csv
docker compose run --rm cli risk-ml ingest \
  --input data/processed/credit_fixture.csv --source synthetic-fixture
docker compose run --rm cli risk-ml transform
docker compose run --rm cli risk-ml train --model all --source synthetic-fixture
```

Native development remains available where host policy permits: install `.[dev]`, run `make verify`,
and set `RISK_ML_DATABASE_URL` and `RISK_ML_MLFLOW_TRACKING_URI` before invoking the same CLI commands.
Do not disable Windows Application Control to make native compiled extensions load.

Start orchestration with `docker compose up -d airflow-init`, wait for completion, then start
`airflow-api-server`, `airflow-scheduler`, and `airflow-dag-processor`.

## Recovery

Inspect `docker compose ps` and `docker compose logs SERVICE`. Database migrations are forward-only in
normal operation; restore a tested backup before downgrading. Ingestion upserts by source and row ID,
so it is safe to retry. Training writes a candidate before updating `champion.joblib`.

`docker compose down` preserves named volumes. `docker compose down --volumes` irreversibly removes
local service state and should only be used for an intentional clean-room test.

