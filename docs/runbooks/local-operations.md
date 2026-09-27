# Local operations runbook

## Bootstrap and verify

Use Python 3.12. Create and activate a virtual environment, then run:

```bash
python -m pip install -e ".[dev]"
make verify
docker compose config
docker compose up -d postgres mlflow
python -m alembic upgrade head
python -m risk_ml.cli ingest
python -m risk_ml.cli transform
python -m risk_ml.cli train --model all
```

Start the API with `make api`, then in another shell run `make smoke`. `/health` proves the process is
alive; `/ready` proves a compatible artifact loaded. Start orchestration with `docker compose up -d
airflow-init`, wait for completion, then start `airflow-api-server airflow-scheduler
airflow-dag-processor`.

## Recovery

Inspect `docker compose ps` and `docker compose logs SERVICE`. Database migrations are forward-only in
normal operation; restore a tested backup before downgrading. Ingestion upserts by source and row ID,
so it is safe to retry. Training writes a candidate before updating `champion.joblib`.

`docker compose down` preserves named volumes. `docker compose down --volumes` irreversibly removes
local service state and should only be used for an intentional clean-room test.

